# Twitter-COMMs

Coming soon! We plan to publish the dataset here by \__\_.

Our technical report can be found here: <https://arxiv.org/abs/2112.08594>

## Data

The NewsCLIPpings style training set, which includes both pristine and falsified samples, used in the paper are in the `./data/news_clippings/` folder.

The dataset of just the tweet_ids is in the `./data/tweets/twitter_comms_dataset.csv` file. Twitter restricts distribution of data pulled from their API, so we can only share the Tweet_id's. You can get the full data by "rehydrating" the tweet_ids. We provide scripts to rehydrate and also download the images in `./scripts/`.

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
