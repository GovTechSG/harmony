import json
import os
from typing import Tuple

import pandas as pd
import streamlit as st
from networkx import DiGraph
from openai import OpenAI
from streamlit.runtime.uploaded_file_manager import UploadedFile

from harmony.traversal import load_pickle

if 'graph' not in globals():
    graph: DiGraph = load_pickle('./graph.pickle')


def get_best_candidate(choices: str, target: str) -> Tuple[str, int]:
    try:
        assert st.session_state.get('openai_api_key')
        client = OpenAI(
            base_url=st.session_state['openai_base_url'],
            api_key=st.session_state['openai_api_key']
        )
    except (KeyError, AssertionError) as e:
        st.error("Please setup the API Key and/or Base URL.")
        raise e

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


def find_product_hs_code(description: str, silent: bool = False):
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
            if not silent:
                st.markdown(f"## Possible HS Code: {current_node}")
            break

        # Use get_best_candidate to determine the next node based on the description
        next_node, token_use = get_best_candidate(json.dumps(possible_successors), description)
        total_token_use += token_use

        if not silent:
            with st.expander(label=f"⚡️ **{level}: {next_node}** - {graph.nodes[next_node]['description']}"):
                st.dataframe(possible_successors)

        # If we're at the last hierarchy level, we don't expect further successors
        if level == hierarchy_levels[-1]:
            if not silent:
                st.markdown(f"## Possible HS Code: {next_node}")

        # Update current_node to move down the hierarchy
        current_node = next_node

    if not silent:
        st.code(f'Tokens Used: {total_token_use}\nCost: ${0.01 / 1000 * total_token_use}')

    return current_node


# UI Setup
st.set_page_config(
    page_title='Harmony',
    page_icon='📦',
    initial_sidebar_state='expanded'
)

with st.sidebar:
    st.markdown("""
    Please paste your credentials before proceeding. You may obtain your own API Key directly from
    [OpenAI](https://platform.openai.com/api-keys).
    """.strip())

    st.session_state['openai_api_key'] = st.text_input(label='OpenAI* API Key', type='password',
                                                       value=os.environ.get('OPENAI_API_KEY', ''))

    st.session_state['openai_base_url'] = st.text_input(label='OpenAI* Base URL',
                                                        value=os.environ.get('OPENAI_BASE_URL',
                                                                             'https://api.openai.com/v1'))
    st.markdown('> `*` OpenAI Compatible')

st.title("📦 Harmony")
st.markdown("Find HS Codes against a product description.")

single_tab, batch_tab = st.tabs(["Single", "Batch Processing"])

with single_tab:
    if description := st.text_input(
            label='Product Description (type, press enter)',
            help="Type in the textbox below and press enter/return",
            placeholder="Xbox 360 Motherboard"):
        try:
            with st.spinner("🔎 Looking it up..."):
                find_product_hs_code(description=description, silent=False)
        except KeyError:
            st.error("The dataset appears to be corrupted for this particular section.", icon='😱')

with batch_tab:
    uploaded_file = st.file_uploader(label="CSV File", accept_multiple_files=False)
    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        if 'description' not in df.columns or 'hs_code' not in df.columns:
            st.error("CSV file does not have a `description` and `hs_code` column.", icon='⚠️')
        else:
            df = df[['description', 'hs_code']]
            df_placeholder = st.empty()
            with df_placeholder.container():
                st.dataframe(df)
            df['matched'] = ''  # Initialize the matched column with empty strings
            if st.button(label='Start', type='primary'):
                with st.spinner("Processing..."):
                    for index, row in df.iterrows():
                        result = find_product_hs_code(description=row['description'], silent=True)
                        df.at[index, 'result'] = result
                        df.at[index, 'matched'] = 'pass' if row['hs_code'] == result else 'fail'
                        with df_placeholder.container():
                            st.dataframe(df)
                st.success("Processing complete!")
