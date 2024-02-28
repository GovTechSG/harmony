import os
from concurrent.futures import ThreadPoolExecutor
from glob import glob

from openai import OpenAI
from tqdm import tqdm

client = OpenAI()

PROMPT = """
Convert this description into a graph dot file. 

HS Codes should be the `id`, the description should go as the metadata. Just return the dot file code. HS Codes and Chapter numbers  (numeric with the dots) should be the ID, the description should go as the metadata. Do not include the word "Chapter" "Section" etc in the ID.

Remember, AA is the parent of AA.BB, AA.BB.CC is the child of AA.BB. vice-versa.

Always prefer the deepest granularity. So for
```
 18.04 1804.00.00  Cocoa butter, fat and oil.
```
Choose 1804.00.00

Add the "notes" as the chapter notes property

Example Output:

strict digraph "" {
	18	[description="Cocoa and cocoa preparations", notes="...."];
	18.01	[description="Cocoa beans, whole or broken, raw or roasted."];
	18 -> 18.01;
	"1802.00.00"	[description="Cocoa shells, husks, skins and other cocoa waste."];
	18 -> "1802.00.00";
""".strip()


def construct_graph_file(chapter_content: str):
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant who converts Descriptions of HS Codes into NetworkX Dotfile "
                       "Graphs."
        },
        {
            "role": "user",
            "content": chapter_content + '\n\n' + PROMPT
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0,
        max_tokens=4096,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response.choices[0].message.content


def process_file(file_path):
    try:
        with open(file_path, 'r') as file:
            chapter_content = file.read()
        dot_content = construct_graph_file(chapter_content)
        dot_file_path = file_path.rsplit('.', 1)[0] + '.dot'
        with open(dot_file_path, 'w') as file:
            file.write(dot_content)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


if __name__ == '__main__':
    all_files = sorted(glob('Section_*_Chapter_*_Subchapter_*.txt'))
    files = [f for f in all_files if not os.path.exists(f.rsplit('.', 1)[0] + '.dot')]
    with ThreadPoolExecutor(max_workers=10) as executor:
        list(tqdm(executor.map(process_file, files), total=len(files), desc="Processing files", unit="file", miniters=1))
