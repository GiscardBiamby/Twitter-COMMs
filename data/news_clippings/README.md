# Falsified Samples

## Data Format
The data is ordered such that every even sample is pristine, and the next sample is its associated falsified sample. 

- `id`: the Tweet id associated with the caption
- `image_id`: the Tweet id associated with the image
- `falsified`: a binary indicator if the caption / image pair is falsified (automatically generated)
- `topic`: the topic (climate, covid, military) and generation method (random, hard) used

We generated the random mismatches by retrieving randomly within each topic. We generated the hard mismatches using the Semantics / CLIP Text-Text method from [NewsCLIPpings](arxiv.org/abs/2104.05893).
