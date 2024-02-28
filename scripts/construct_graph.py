from glob import glob
from tqdm import tqdm
from count_tokens import num_tokens_from_messages

from openai import OpenAI

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
    messages = construct_messages(chapter_content)

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


def construct_messages(chapter_content: str):
    return [
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


if __name__ == '__main__':
    for file_path in tqdm(sorted(glob('*.txt')), desc="Processing files", unit="file"):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            messages = construct_messages(content)
            num_tokens = num_tokens_from_messages(messages)
            print(f'File: {file_path}, Num Tokens: {num_tokens}')
        except Exception as e:
            print(f'An error occurred while processing {file_path}:', str(e))
        # dot_content = construct_graph_file(chapter_content)
        # dot_file_path = file_path.rsplit('.', 1)[0] + '.dot'
        # with open(dot_file_path, 'w') as file:
        #     file.write(dot_content)
