# File manifest

```bash
$ cd data
$ tree
.
├── DATA.md
├── train_val
│   ├── train.zip
│   └── val.zip
├── scripts
│   ├── download_images.py
└── tweets
    └── twitter_comms_dataset.csv
```

## Twitter Data

`tweets/twitter_comms_dataset.csv`:
This is a file containing all the tweet_id's for the 884K unique tweets of the TwitterCOMMs dataset. The file is comma delimited, with the following columns:

* `tweet_id` (string): tweet_id, which can be used to retrieve the tweet and its associated metadata and images/videos from the Twitter API.
* `topic` (string): covid|climate|military
* `possibly_sensitive` (boolean): Flag provided by Twitter API, indicating if the tweet may contain or link to possibly sensitive content, e.g., violence, nudity.
* `nsfw_prob` (float): A probability of whether or not the tweet image might contain nudity, which we computed using NudeNET (<https://github.com/notAI-tech/NudeNet>).

`scripts/download_images.py`:
Rehydrating only download the metadata for tweets into JSON format. This script uses the image URL's from this JSON to download the images. Depending on which tool or script you use to rehydrate, you may have to modify the script to point it to the image URL's.

## Falsified Data

`train_val/train.zip`: This is a zip archive for the file `train.csv` consisting of \~2M samples, corresponding to the training set used for model development.
`train_val/val.zip`: This is a zip archive for the file `val.csv` consisting of \~27k samples, corresponding to the "Dev" set used for evaluation.

These files contain pristine + random/hard negative samples derived from the unique tweets described above. We generated the random negatives by retrieving randomly within each topic. We generated the hard negatives using the Semantics / CLIP Text-Text method from [NewsCLIPpings](arxiv.org/abs/2104.05893).

The files are comma delimited, with the following columns:

* `id`: The `tweet_id` associated with the caption.
* `image_id`: The `tweet_id` associated with the image.
* `falsified`: A binary indicator if the caption / image pair is falsified (automatically generated).
* `topic`: The topic (climate, covid, military) and generation method (random, hard) used.

### Data Usage

To get started:

1. Hydrate the tweets using the tweet ID's from `tweets/twitter_comms_dataset.csv`. You should get a JSON file with the captions and image paths.
2. Unzip the files `train_val/train.zip` and `train_val/val.zip`.
3. For `train_val/train.csv` and `train_val/val.csv`, fill in the columns for `caption` and `image_path` based on the corresponding samples in `tweets/twitter_comms_dataset.csv`.

A sample ready for training would look like this:

```json
{
	"id": 1283577228320628736,
	"caption": "Gov. Brian Kemp renews COVID-19 restrictions in Georgia with no mask mandate http://dlvr.it/RbjLnx",
	"image_id": 1305956579896782848,
	"image_path": "<your_image_path>/1305956579896782848-3_1305956578101620736.jpg",
	"falsified": True,
	"topic": "covid_hard"
}
```

Please also note that we pre-processed the captions by running NLTK's TweetTokenizer, stripping the links, and removing punctuation before training.
