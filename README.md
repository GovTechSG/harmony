# Harmony - HS Codes meet 2024

Harmony uses LLMs and Graph Databases to map Harmonised System Codes to product descriptions.

https://blog.adhikary.net/matching-hs-codes-in-2024-traversing-the-customs-space

## Initialising Dataset

### Installation

Ensure your system has Python 3.11+ and Poetry Package Manager installed.
`cd` into the project directory and run,

```shell
poetry install
```

### Preparing the dataset

1. Run `load_stcced.py` to download and process the 'Singapore Trade Classification Customs and Excise Duties (STCCED) 
   2022' file. This outputs `stcced.txt`.
2. Run `split_stcced.py` to split the `stcced.txt` file into Sections, Chapters and Subchapters.