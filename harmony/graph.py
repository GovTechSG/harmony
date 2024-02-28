import networkx as nx
from tqdm import tqdm
import glob
from networkx.classes.reportviews import NodeView


def clean_file(path: str) -> None:
    """
    Remove OpenAI Code Block Markers
    """
    with open(path) as read_file:
        content = read_file.read()
    content = content.replace('```dot\n', '')
    content = content.replace('```', '')
    with open(path, 'w') as read_file:
        read_file.write(content)


def load_and_merge_graphs(pattern: str) -> nx.DiGraph:
    root_graph = nx.DiGraph()
    root_graph.add_node('root')
    for path in tqdm(glob.glob(pattern), desc="Loading and merging graphs"):
        clean_file(path)
        subgraph = nx.DiGraph(nx.nx_pydot.read_dot(path))
        for node in subgraph:
            if node in root_graph:
                root_graph.nodes[node].update(subgraph.nodes[node])
                for child in subgraph.successors(node):
                    root_graph.add_edge(node, child)
            else:
                root_graph.add_node(node, **subgraph.nodes[node])
                for child in subgraph.successors(node):
                    root_graph.add_edge(node, child)
        if subgraph.nodes:
            shortest_id_node = min(subgraph.nodes, key=lambda x: len(str(x)))
            node_parts = str(shortest_id_node).split('.')
            if len(node_parts) == 1:
                # Node ID is just an integer
                root_graph.add_edge('root', shortest_id_node)
            else:
                # Node ID has a decimal, take the integer part before the decimal
                parent_node = node_parts[0]
                if parent_node not in root_graph:
                    root_graph.add_node(parent_node)
                root_graph.add_edge(parent_node, shortest_id_node)
    return root_graph


if __name__ == '__main__':
    pass
    G = load_and_merge_graphs('../scripts/Section_*_Chapter_*_Subchapter_*.dot')
    nx.nx_pydot.write_dot(G, 'out.dot')
    # root = list(G.nodes.keys())[0]
    # bfs_successors = dict(nx.bfs_successors(G, root, depth_limit=1))
    # bfs_successors_with_metadata = {}
    # for node, successors in bfs_successors.items():
    #     bfs_successors_with_metadata[node] = {
    #         # 'metadata': G.nodes[node],
    #         'children': [{child: G.nodes[child]} for child in successors]
    #     }
    # print(bfs_successors_with_metadata)
