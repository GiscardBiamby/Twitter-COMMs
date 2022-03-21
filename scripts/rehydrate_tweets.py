"""
https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
"""
import json
import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

import pandas as pd
from searchtweets import ResultStream, gen_request_parameters, load_credentials
from tqdm import tqdm

logger = logging.getLogger()
logging.basicConfig(
    level=os.environ.get("LOGLEVEL", "INFO"),
    format="[%(asctime)s]:[%(processName)-11s]"
    + "[%(levelname)-s]:[%(name)s] %(message)s",
)


# PAGE_SIZE, value between 10 and 100, is passed into the "max_results" parameter of pagination
# (https://developer.twitter.com/en/docs/twitter-api/pagination)
PAGE_SIZE = 100
# MAX_TWEETS is a parameter specific to the search_tweets python library. It caps how many tweets
# for the entire session, i.e,, across multiple pages:
MAX_TWEETS = 135000


def main(args):
    # Prepare paths:
    config_path = Path("./search_tweets.yaml").resolve()
    csv_path = args.csv_path.resolve()
    logger.info(f"config_path: {config_path}")
    logger.info(f"csv_path: {csv_path}")
    assert config_path.exists, str(config_path)
    assert csv_path.exists(), str(csv_path)

    rehydrate_tweets(args)


def rehydrate_tweets(args: Namespace) -> None:
    """
    Rehydrate tweets from tweet_ids to json with data about each tweet, including
    embedded images, videos, etc.
    """
    config_path = (Path(__file__).parent / "search_tweets.yaml").resolve()
    assert config_path.exists(), str(config_path)
    filename = (args.output_dir / f"{args.name}.json").resolve()
    assert not filename.exists(), str(filename)
    search_args = load_credentials(filename=config_path)
    # load_credentials() fails to load the "endpoint" from the search_tweets.yaml file,
    # so set it manually here:
    search_args["endpoint"] = "https://api.twitter.com/2/tweets/search/all"
    logger.info(f"Search args: {search_args}")

    # Query
    # query_str = "context:123.1220701888179359745 lang:en -place_country:US has:media -is:retweet"
    query_str = f"""("{v_name}" AND "{v_type}") """
    search_query = gen_request_parameters(
        query_str,
        results_per_call=PAGE_SIZE,
        media_fields="media_key,type,duration_ms,height,preview_image_url,public_metrics,url,width,alt_text",
        place_fields="full_name,id,country,country_code,geo,name,place_type",
        tweet_fields="attachments,author_id,context_annotations,created_at,entities,geo,id,in_reply_to_user_id,lang,possibly_sensitive,public_metrics,referenced_tweets,source,text,withheld",
        user_fields="description,location,public_metrics",
        expansions="attachments.media_keys,author_id,geo.place_id",
        end_time="2021-08-16 00:00",
    )
    count_query = gen_request_parameters(
        query_str,
        results_per_call=PAGE_SIZE,
        granularity="day",
        end_time="2021-08-16 00:00",
    )
    logger.info(f"Search query: {search_query}")
    logger.info(f"Count query: {count_query}")
    # sys.exit()

    # Get Tweet Counts:
    rs = ResultStream(
        request_parameters=count_query,
        max_tweets=MAX_TWEETS,
        max_pages=2,
        **search_args,
    )
    tweet_count = 0
    for page_num, page in enumerate(rs.stream()):
        if page_num >= 0:
            break
        tweet_count += save_counts_page(page, args)
    logger.info(f"Total Tweets: {tweet_count}")
    logger.info("")

    # Get Tweets
    rs = ResultStream(
        request_parameters=search_query,
        max_tweets=MAX_TWEETS,
        max_pages=2,
        output_format="a",
        **search_args,
    )
    logger.info(f"ResultStream: {str(rs)}")
    logger.info("")
    for page_num, page in enumerate(rs.stream()):
        save_page(page, args, filename)


def save_counts_page(page, args):
    filename = (args.output_dir / f"{args.name}_counts.json").resolve()

    with open(filename, "a") as f:
        logger.info(type(page))
        logger.info(page)
        tweet_count = 0
        for count_per_day in page["data"]:
            tweet_count += count_per_day["tweet_count"]
            f.write(json.dumps(count_per_day, sort_keys=True) + "\n")
    return tweet_count


def save_page(page, args, filename: Path):
    with open(filename, "a") as f:
        # logger.info(f"keys: {page.keys()}")
        # for tweet in page["data"]:
        #     f.write(json.dumps(tweet, sort_keys=True) + "\n")
        f.write(json.dumps(page, sort_keys=True) + "\n")


def get_vehicles(csv_path: Path) -> pd.DataFrame:
    """
    Returns military_objs.csv as a pandas df.
    """
    assert csv_path.exists(), str(csv_path)
    df = cast(pd.DataFrame, pd.read_csv(csv_path))
    logger.info(f"Found {len(df)} military vehicles.")
    print(df)
    return cast(pd.DataFrame, df)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=Path,
        default=Path("../data/tweets").resolve(),
    )
    parser.add_argument("--name", type=str, default="twitter_comms_dataset", help="Used as part of output file name.")
    parser.add_argument("--csv_path", type=Path, default="../data/tweets/twitter_comms_dataset.csv", help="Path to .csv file containing tweet_id's to rehydrate.",)
    args = parser.parse_args()
    main(args)
