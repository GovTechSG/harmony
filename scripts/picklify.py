import os.path
from pathlib import Path

import networkx as nx
import pickle

project_dir = Path(__file__).parent.parent
dot_file_path = os.path.join(project_dir, 'harmony', 'out.dot')
pickle_file_path = os.path.join(project_dir, 'graph.pickle')

print('reading...')
graph = nx.DiGraph(nx.nx_pydot.read_dot(dot_file_path))
print('reading done...')

with open(pickle_file_path, 'wb') as f:
    pickle.dump(graph, f)
