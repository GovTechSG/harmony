import json
from typing import Tuple

import streamlit as st
from networkx import DiGraph
from openai import OpenAI

from harmony.traversal import load_pickle

if 'graph' not in globals():
    graph: DiGraph = load_pickle('./graph.pickle')


def get_best_candidate(choices: str, target: str) -> Tuple[str, int]:
    client = OpenAI()
    response = client.chat.completions.create(
        model='gpt-4-1106-preview',
        messages=[
            {
                "role": "system",
                "content": "You are an helpful assistant."
            },
            {
                "role": "user",
                "content": f"given the following choices: {choices}, which is the best category to represent:"
                           f"\n\n{target} return the `id` as JSON category: string"
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
        top_p=1,
    )

    message = json.loads(response.choices[0].message.content)

    return message['category'], response.usage.total_tokens


def find_product_hs_code():
    hierarchy_levels = ['Section', 'Chapter', 'Subchapter', 'Dash', 'Double Dash']
    current_node = 'root'
    total_token_use = 0

    for level in hierarchy_levels:
        # Fetch possible successors for the current node
        possible_successors = [{
            'description': graph.nodes[key]['description'],
            'id': key
        } for key in graph.successors(current_node)]

        # If there are no successors (possible_successors is empty), we've reached the end
        if not possible_successors:
            st.markdown(f"## Possible HS Code: {current_node}")
            break

        # Use get_best_candidate to determine the next node based on the description
        next_node, token_use = get_best_candidate(json.dumps(possible_successors), description)
        total_token_use += token_use

        with st.expander(label=f"⚡️ **{level}: {next_node}** - {graph.nodes[next_node]['description']}"):
            st.dataframe(possible_successors)

        # If we're at the last hierarchy level, we don't expect further successors
        if level == hierarchy_levels[-1]:
            st.markdown(f"## Possible HS Code: {next_node}")

        # Update current_node to move down the hierarchy
        current_node = next_node

    st.code(f'Tokens Used: {total_token_use}\nCost: ${0.01 / 1000 * total_token_use}')

# UI Setup
st.set_page_config(
    page_title='Harmony',
    page_icon='📦',
)

st.title("📦 Harmony")

if description := st.text_input(label="Product Description", placeholder="Xbox 360 Motherboard"):
    try:
        find_product_hs_code()
    except KeyError:
        st.error("The dataset appears to be corrupted for this particular section.", icon='😱')
