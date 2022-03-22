# Twitter-COMMs: Detecting Climate, COVID, and Military Multimodal Misinformation

This repository contains a large-scale multimodal
dataset with 884k tweets relevant to the topics of Climate Change, COVID-19, and Military Vehicles. Our technical report can be found here: [https://arxiv.org/abs/2112.08594](https://arxiv.org/abs/2112.08594)

## Getting Started

1. Download our dataset of multimodal tweets from `./data/original/twitter_comms_dataset.csv`. Twitter restricts distribution of data pulled from their API, so we can only share the tweet ids. There are many tools that can be used to "rehydrate" the tweet id's into JSON containing the tweet data (including captions and image URL's), e.g., [Hydrator](https://github.com/DocNow/hydrator), [Twarc](https://github.com/docnow/twarc/). We also provide [a script](./data/scripts/download_images.py) to download the images, given such a JSON file. This script is provided as-is, and works on JSON downloaded from V2 of the Twitter API.
2. Consider using our automatically generated random and hard mismatches provided in `./data/train_val` for training.

## Cite Our Work

```bib
@misc{biamby2021twittercomms,
      title={Twitter-COMMs: Detecting Climate, COVID, and Military Multimodal Misinformation},
      author={Giscard Biamby and Grace Luo and Trevor Darrell and Anna Rohrbach},
      year={2021},
      eprint={2112.08594},
      archivePrefix={arXiv},
      primaryClass={cs.CV}
}
```
