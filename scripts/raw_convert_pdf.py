import PyPDF2
from tqdm import tqdm


def main():
    reader = PyPDF2.PdfReader('/Users/aniruddha/Downloads/stcced_index.pdf')

    with open('stcced_index.txt', 'w') as f:
        for page in tqdm(reader.pages):
            text = page.extract_text()
            f.write(text)


main()