import os.path

import PyPDF2
import requests
from tqdm import tqdm

STCCED_LOCAL_PATH = '/tmp/stcced2022.pdf'
STCCED_2022_URL = 'https://file.go.gov.sg/stcced2022.pdf'


def download_file(url: str, local_filename: str):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def download_if_stcced_not_present():
    if not os.path.exists(STCCED_LOCAL_PATH):
        download_file(STCCED_2022_URL, STCCED_LOCAL_PATH)


def main():
    download_if_stcced_not_present()
    reader = PyPDF2.PdfReader(STCCED_LOCAL_PATH)

    with open('stcced.txt', 'w') as f:
        for page in tqdm(reader.pages[15:]):
            f.write(page.extract_text())


if __name__ == '__main__':
    main()
