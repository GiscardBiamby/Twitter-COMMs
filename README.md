# Twitter-COMMs: Detecting Climate, COVID, and Military Multimodal Misinformation

This repository contains a large-scale multimodal
dataset with 884k tweets relevant to the topics of Climate Change, COVID-19, and Military Vehicles. Our technical report can be found here: <https://arxiv.org/abs/2112.08594>

## Getting Started

1. Download our dataset of multimodal tweets from `./data/original/twitter_comms_dataset.csv`. To obtain captions and images, we provide scripts to rehydrate tweets and download the images in `./scripts/`.

<!-- Twitter restricts distribution of data pulled from their API, so we can only share the Tweet_id's.  -->
2. Consider using our automatically generated random and hard mismatches provided in `./data/train_val` for training.

## Cite Our Work

```bib
@article{biamby2021twitter,
  title={Twitter-COMMs: Detecting Climate, COVID, and Military Multimodal Misinformation},
  author={Biamby, Giscard and Luo, Grace and Darrell, Trevor and Rohrbach, Anna},
  journal={arXiv preprint arXiv:2112.08594},
  year={2021}
}
```
