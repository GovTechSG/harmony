import pickle

import networkx as nx
from networkx import DiGraph


def load_pickle(path: str = '../graph.pickle') -> DiGraph:
    with open(path, 'rb') as f:
        return pickle.load(f)


def load_dot_file(path: str = './root.dot') -> DiGraph:
    return nx.DiGraph(nx.nx_pydot.read_dot(path))


