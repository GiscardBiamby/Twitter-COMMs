"""
Script to download images from twitter. Runs via multiprocessing, and can download at roughly 20,000
imgs / hour.

The input is currently intended to be a .json file which was generated from the Twitter Search API
(v2). If you have some other format, you can modify the get_photo_urls() function to work with your
data. If you are working with tweet json generated from a tool such as "hydrator" you can probably
make small modifications to the existing functions to parse out the URL's, or simply write you own
loading code.
"""
import logging
import multiprocessing
import os
import shutil
import sys
import time
from argparse import ArgumentParser
from functools import wraps
from multiprocessing.process import BaseProcess
from pathlib import Path
from typing import List, cast

import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

logger = logging.getLogger()
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format="[%(asctime)s]:[%(processName)-11s]" + "[%(levelname)-s]:[%(name)s] %(message)s",
)


class LastTime:
    """
    Credit: Copied and modified this: https://gist.github.com/gregburek/1441055

    >>> import rate_limited as rt
    >>> a = rt.LastTime()
    >>> a.add_cnt()
    >>> a.get_cnt()
    1
    >>> a.add_cnt()
    >>> a.get_cnt()
    2
    """

    def __init__(self, name="LT"):
        # Init variables to None
        self.name = name
        self.ratelock = None
        self.cnt = None
        self.last_time_called = None

        # Instantiate control variables
        self.ratelock = multiprocessing.Lock()
        self.cnt = multiprocessing.Value("i", 0)
        self.last_time_called = multiprocessing.Value("d", 0.0)

        logging.debug("\t__init__: name=[{!s}]".format(self.name))

    def acquire(self):
        self.ratelock.acquire()

    def release(self):
        self.ratelock.release()

    def set_last_time_called(self):
        self.last_time_called.value = time.time()
        # self.debug('set_last_time_called')

    def get_last_time_called(self):
        return self.last_time_called.value

    def add_cnt(self):
        self.cnt.value += 1

    def get_cnt(self):
        return self.cnt.value

    def debug(self, debugname="LT"):
        now = time.time()
        logging.debug(
            "___Rate name:[{!s}] "
            "debug=[{!s}] "
            "\n\t        cnt:[{!s}] "
            "\n\tlast_called:{!s} "
            "\n\t  timenow():{!s} ".format(
                self.name,
                debugname,
                self.cnt.value,
                time.strftime(
                    "%T.{}".format(
                        str(self.last_time_called.value - int(self.last_time_called.value)).split(
                            "."
                        )[1][:3]
                    ),
                    time.localtime(self.last_time_called.value),
                ),
                time.strftime(
                    "%T.{}".format(str(now - int(now)).split(".")[1][:3]), time.localtime(now)
                ),
            )
        )


def rate_limited(max_per_second):
    """
    Decorator to rate limit a python function.

    Example, limits to 10 requests per second, and works w/ multiprocessing as well:

        > @rate_limited(10)
        > def download_img(media_url):
        > ...

    Credit: Copied and modified this: https://gist.github.com/gregburek/1441055
    """
    min_interval = 1.0 / max_per_second
    LT = LastTime("rate_limited")

    def decorate(func):
        LT.acquire()
        if LT.get_last_time_called() == 0:
            LT.set_last_time_called()
        LT.debug("DECORATE")
        LT.release()

        @wraps(func)
        def rate_limited_function(*args, **kwargs):

            logging.debug(
                "___Rate_limited f():[{!s}]: "
                "Max_per_Second:[{!s}]".format(func.__name__, max_per_second)
            )

            try:
                LT.acquire()
                LT.add_cnt()
                xfrom = time.time()

                elapsed = xfrom - LT.get_last_time_called()
                left_to_wait = min_interval - elapsed
                logging.debug(
                    "___Rate f():[{!s}] "
                    "cnt:[{!s}] "
                    "\n\tlast_called:{!s} "
                    "\n\t time now():{!s} "
                    "elapsed:{:6.2f} "
                    "min:{!s} "
                    "to_wait:{:6.2f}".format(
                        func.__name__,
                        LT.get_cnt(),
                        time.strftime("%T", time.localtime(LT.get_last_time_called())),
                        time.strftime("%T", time.localtime(xfrom)),
                        elapsed,
                        min_interval,
                        left_to_wait,
                    )
                )
                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                ret = func(*args, **kwargs)

                LT.debug("OVER")
                LT.set_last_time_called()
                LT.debug("NEXT")

            except Exception as ex:
                sys.stderr.write(
                    "+++000 " "Exception on rate_limited_function: [{!s}]\n".format(ex)
                )
                sys.stderr.flush()
                raise
            finally:
                LT.release()
            return ret

        return rate_limited_function

    return decorate


@rate_limited(30)
def save_image(idx, img_row, images_dir: Path, size="large"):
    """
    Download and save image to path.

    Args:

        image: The url of the image.
        path: The directory where the image will be saved.
        filename:
        size: Which size of images to download.
    """
    if img_row["media_url"]:
        save_dest: Path = images_dir / img_row["filename"]
        save_dest.parent.mkdir(exist_ok=True, parents=True)

        if not save_dest.exists():
            # logger.info(f"Saving image: {save_dest.name}")
            r = requests.get(img_row["media_url"] + ":" + size, stream=True)
            if r.status_code == 200:
                with open(save_dest, "wb") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            elif r.status_code in [403, 404]:
                pass
            else:
                print(f"Error on {idx}, tweet_id:{img_row['tweet_id']}, url:{img_row['media_url']}")
                print(r.headers)
                print(r.status_code, ", ", r.reason)
                print(r.text)
            if r.status_code in [429]:
                sleep_seconds = 15 * 60
                logger.error(f"Rate limit hit... Will retry in {sleep_seconds} seconds...")
                time.sleep(sleep_seconds)
        else:
            # print(f"Skipping {save_dest}: already downloaded")
            pass


@rate_limited(3)
def fake_save_image(idx, img_row, images_dir: Path, size="large"):
    """
    This is just for testing purposes, when we don't want to hit the twitter servers.
    """
    import random

    r = float(random.randrange(420)) / 1000.0
    time.sleep(r)
    pass


def dl_images(df_media: pd.DataFrame, images_dir: Path) -> None:
    """
    Single process, just download one images at a time.
    """
    for idx, row in df_media.iterrows():
        save_image(idx, row, images_dir, size="orig")


def dl_images_mp(df_media: pd.DataFrame, images_dir: Path, num_processes: int) -> None:
    """
    Split the `df_media` `DataFrame` into N equal parts and use python multiprocessing to download
    the images for each part. N = `num_processes`.
    """
    TaskPool = []
    df_media_splits = np.array_split(df_media, num_processes)

    for process_num in range(1, num_processes + 1):
        Task = multiprocessing.Process(
            target=dl_images_mp_helper,
            args=(process_num, df_media_splits[process_num - 1], images_dir),
        )
        TaskPool.append(Task)
        Task.start()

    logger.info(f"Started {num_processes} ({len(TaskPool)}) processes to download images")

    for process_num in TaskPool:
        process_num.join()
        print(
            "==={!s} (is alive: {!s}).exitcode = {!s}".format(
                process_num.name, process_num.is_alive(), process_num.exitcode
            )
        )


def dl_images_mp_helper(process_num: int, df_media: pd.DataFrame, images_dir: Path) -> None:
    logger.info(f"process_num:{process_num}, df_media shape: {df_media.shape}")
    for idx, img_row in tqdm(df_media.iterrows(), total=len(df_media), position=process_num - 1):
        save_dest: Path = images_dir / img_row["filename"]
        save_dest.parent.mkdir(exist_ok=True, parents=True)

        if not save_dest.exists():
            save_image(idx, img_row, images_dir, size="orig")


def main(args):
    # Prepare paths:
    data_dir: Path = args.data_dir.resolve()
    logger.info(f"Data_dir: {data_dir}")
    input_file: Path = (data_dir / args.input_file).resolve()
    logger.info(f"input_file: {input_file}")
    assert data_dir.exists, str(data_dir)
    assert input_file.exists(), str(input_file)
    images_dir: Path = data_dir / "images" / input_file.stem
    logger.info(f"images_dir: {images_dir}")
    images_dir.mkdir(exist_ok=True, parents=True)

    # Load url's from twitter json
    df_media = get_photo_urls(input_file)
    # Remove images that are already downloaded:
    print("Checking for already downloaded images. Images_dir: ", images_dir)
    df_media["is_downloaded"] = df_media.apply(
        lambda x: (images_dir / x["filename"]).exists(), axis=1
    )
    df_media = df_media[(~df_media.is_downloaded)].copy(deep=True)

    num_processes = 10
    if num_processes < 2:
        dl_images(df_media, images_dir)
    else:
        dl_images_mp(df_media, images_dir, num_processes)


def load_tweets(json_path: Path) -> pd.DataFrame:
    assert json_path.exists(), str(json_path)
    df = pd.read_json(
        json_path,
        lines=True,
        precise_float=True,
        dtype={"id": int},
    )
    # Note: id_str matches the tweet_id's that are passed into hydrator:
    df["tweet_id"] = df.id.astype(int)
    df = df.drop_duplicates("tweet_id")
    df.set_index(
        "tweet_id",
        drop=False,
        inplace=True,
        verify_integrity=True,
    )
    df["country"] = df.geo.apply(
        lambda x: x["country"] if isinstance(x, dict) and "country" in x else None
    )
    return cast(pd.DataFrame, df)


def pre_json_normalize(
    row, parent_col_name: str, target_col_name: str, child_properties: list = None
) -> dict:
    """
    Prepares a column of a dataframe (`target_col_name`) to be run through
    `json_normalize()`. To achieve this it takes a row of a dataframe containing tweet
    data, and:

    1. Adds the `parent_col_name: row[parent_col_name]` as a key-value pair to the dict
        object contained in `row[target_col_name]`. This helps link the rows of the
        original DataFrame to those of the DataFrame that is output when the target
        column is run thru `json_normalize()`.

    2. Adds a `"media": []` key-value pair if no media key is in the target dict.

    3. If the target dict is null, a new one is created.
    """
    target_dict = row[target_col_name]
    if not isinstance(target_dict, dict):
        target_dict = {}
    if parent_col_name not in target_dict:
        target_dict[parent_col_name] = row[parent_col_name]
    if child_properties:
        for prop_name, prop_type in child_properties:
            if prop_name not in target_dict:
                target_dict[prop_name] = prop_type()
    return target_dict


def get_photo_urls(json_path: Path, media_type: str = "photo") -> pd.DataFrame:
    """
    Returns a DataFrame of media info from the give json file. The input file should be a twitter
    json file that came from the Twitter v2 Search API.

    Example output:

        >       height              id_str   type                                              url  width  duration_ms preview_image_url  public_metrics.view_count alt_text             tweet_id             filename
        > 0       1920  3_1427530554480619521  photo  https://pbs.twimg.com/media/E8-bedXVcAEqkXA.jpg   1080          NaN               NaN                        NaN      NaN  1427531793771622400    xx/<filename>.jpg
        > 1        409  3_1427531788591771661  photo  https://pbs.twimg.com/media/E8-cmSyXMA0ETDr.jpg    615          NaN               NaN                        NaN      NaN  1427531789392883727    xx/<filename>.jpg
        > 2       1000  3_1427531783868878850  photo  https://pbs.twimg.com/media/E8-cmBMVkAIcD4a.jpg   1000          NaN               NaN                        NaN      NaN  1427531786746163202    xx/<filename>.jpg
        > 3        546  3_1427531482029903875  photo  https://pbs.twimg.com/media/E8-cUcwUUAMRefa.jpg    728          NaN               NaN                        NaN      NaN  1427531786477740034    xx/<filename>.jpg
        > 4        375  3_1427526863543578632  photo  https://pbs.twimg.com/media/E8-YHnjXsAgRpIu.jpg    500          NaN               NaN                        NaN      NaN  1427531785458659334    xx/<filename>.jpg
        > ...      ...                    ...    ...                                              ...    ...          ...               ...                        ...      ...                  ...                  ...
    """
    df = load_tweets(json_path)
    if "attachments" in df.columns:
        df["attachments"] = df.apply(
            lambda row: pre_json_normalize(row, "tweet_id", "attachments", [("media", list)]), axis=1
        )
        df_media = pd.json_normalize(df.attachments, record_path="media", meta=["tweet_id"])
    else:
        df["entities"] = df.apply(
            lambda row: pre_json_normalize(row, "tweet_id", "entities", [("media", list)]), axis=1
        )
        df_media = pd.json_normalize(df.entities, record_path="media", meta=["tweet_id"])
    df_media = df_media[(df_media.type == media_type) & ~df_media.media_url.isna()]
    df_media.reset_index(inplace=True)
    df_media.index.name = "id"

    def _get_filename(row):
        extension = Path(row["media_url"]).suffix if row["media_url"] and not pd.isna(row["media_url"]) else None
        filename = f"{row['id_str'][-2:]}/{row['tweet_id']}-{row['id_str']}{extension}"
        return filename

    df_media["filename"] = df_media.apply(lambda row: _get_filename(row), axis=1)
    logger.info(f"Found {len(df_media)} media urls of type: '{media_type}'")
    print(df_media)
    return cast(pd.DataFrame, df_media)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--data_dir",
        type=Path,
        default=Path("../data/original").resolve(),
        help=(
            "Path to the data. This path should contain the twitter json inputs. "
            "The images will be downloaded into this path as well (into sub-folder(s)). "
            "The default path is relative to this script."
        ),
    )
    parser.add_argument("--input_file", type=Path, default="twitter_comms_dataset.json")
    args = parser.parse_args()
    main(args.input_file)
