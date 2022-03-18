# File manifest

```bash
$ cd data
$ tree
.
├── news_clippings
│   ├── train.csv
│   └── val.csv
├── readme.md
├── train_val
│   ├── train.csv.zip
│   └── val.csv.zip
└── tweets
    └── twitter_comms_dataset.csv
```

## File Descriptions

`news_clippings/`:
The NewsCLIPpings style training and validation sets, which include both pristine and falsified samples used in the paper.

`train_val/train.csv.zip`:
The training set consisting of \~2M samples (pristine + hard/random negatives)

`train_val/val.csv.zip`:
The "Dev" set consisting of \~27K samples (pristine + hard/random negatives)

`tweets/twitter_comms_dataset.csv`:
This is a file containing all the tweet_id's for the 884K unique tweets of the TwitterCOMMs dataset. The file is comma delimited, with the following columns:

* `tweet_id` (string): tweet_id, which can be used to retrieve the tweet and its associated metadata and images/videos from the Twitter API.
* `topic` (string): covid|climate|military
* `possibly_sensitive` (boolean): Flag provided by Twitter API, indicating if the tweet may contain or link to possibly sensitive content, e.g., violence, nudity.
* `nsfw_prob` (float): A probability of whether or not the tweet image might contain nudity, which we computed using NudeNET (<https://github.com/notAI-tech/NudeNet>).

## `train.csv.zip` and `val.csv.zip` Data Format

The data is ordered such that every even sample is pristine, and the next sample is its associated falsified sample.

* `id`: the Tweet id associated with the caption
* `image_id`: the Tweet id associated with the image
* `falsified`: a binary indicator if the caption / image pair is falsified (automatically generated)
* `topic`: the topic (climate, covid, military) and generation method (random, hard) used

We generated the random mismatches by retrieving randomly within each topic. We generated the hard mismatches using the Semantics / CLIP Text-Text method from [NewsCLIPpings](arxiv.org/abs/2104.05893).

### Data Usage

To use this data, fill in the `caption` and `image_path` fields from the hydrated tweets. A sample ready for training would look like this:

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
