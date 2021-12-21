# Train / Val Samples

This folder contains metadata for the training and validation samples used to train our classifier for out-of-context images.

## Data Format
The data is ordered such that every even sample is pristine, and the next sample is its associated falsified sample.

- `id`: the Tweet id associated with the caption
- `image_id`: the Tweet id associated with the image
- `falsified`: a binary indicator if the caption / image pair is falsified (automatically generated)
- `topic`: the topic (climate, covid, military) and generation method (random, hard) used

We generated the random mismatches by retrieving randomly within each topic. We generated the hard mismatches using the Semantics / CLIP Text-Text method from [NewsCLIPpings](arxiv.org/abs/2104.05893).

## Data Usage
To use this data, fill in the `caption` and `image_path` fields from the hydrated tweets. A sample ready for training would look like this:

```
{
	"id": 1283577228320628736,
	"caption": "Gov. Brian Kemp renews COVID-19 restrictions in Georgia with no mask mandate http://dlvr.it/RbjLnx",
	"image_id": 1305956579896782848,
	"image_path": "<your_image_path>/1305956579896782848-3_1305956578101620736.jpg",
	"falsified": True,
	"topic": "covid_hard"
}
```

Please also note that we preprocessed the captions by running NLTK's TweetTokenizer, stripping the links, and removing punctuation before training.

