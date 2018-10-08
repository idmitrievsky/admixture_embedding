# Admixture Embedding

## Prerequisites

This script requires **Python 3** to run.

You have to have the following packages installed to run the script:

- altair
- pandas
- sklearn

You can install them using `pip`:

```
pip install altair pandas sklearn
```

## Usage

```
python main.py path/to/fam.fam path/to/fractions.Q PCA > PCA_embedding.html
```

Also TSNE can be used instead of PCA to embed multidimensinal data into two dimensions.
