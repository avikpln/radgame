'''The graph module'''

from collections import deque
import random

import unionfind

##############################################################################
### GRAPH ###
#############
class Graph:  # undirected by default
	'''The Graph class'''

	def __init__(self, n, directed=False):
		Graph.__validate_posint(n)
		self.n = n
		self.directed = directed
		self.__adjlist = dict()
	
	def __str__(self):
		# TODO: Rethink what should be returned here.
		return self.__adjlist.__str__()
	
	def __len__(self):
		return len(self.__adjlist)
	
	# TODO: Reconsider whether a Graph should inherit from dictionary.
	def __getitem__(self, key):
		self.__validate_vertex_key(key)
		if key not in self.__adjlist:
			self.__adjlist[key] = list()
		return self.__adjlist[key]

	def active(self):  # u is active <=> self.__adjlist[u] != None
		return self.__adjlist.keys()
	
	def add_edge(self, u, v):
		self.__validate_vertex_key(u)
		self.__validate_vertex_key(v)
		if self.is_edge(u, v):
			if self.directed:
				edgesymbol = '\u2192'  # →
			else:
				edgesymbol = '\u2501'  # ━
			raise ValueError(f"edge {u} {edgesymbol} {v} already exists")

		self[u].append(v)
		if not self.directed:
			self[v].append(u)

	def remove_edge(self, u, v):
		self.__validate_vertex_key(u)
		self.__validate_vertex_key(v)
		if not self.connected(u, v):
			if self.directed:
				edgesymbol = '\u2192'  # ⟶
			else:
				edgesymbol = '\u2501'  # ━
			raise ValueError(f"edge {u} {edgesymbol} {v} doesn't exist")

		self[u].remove(v)
		if not self.directed:
			self[v].remove(u)
	
	def is_edge(self, u, v):
		self.__validate_vertex_key(u)
		self.__validate_vertex_key(v)
		return v in self[u]

	def V(self):
		for u in range(0, self.n):
			yield u
	
	def E(self):
		for u in self.active():
			for v in self[u]:
				if self.directed or (not self.directed and u < v):
					yield (u, v)

	def nhood(self, u):
		# NOTE: This method returns a snapshot of u's neighborhood, as opposed
		# to __getitem__.
		self.__validate_vertex_key(u)
		return self[u].copy()

	def __validate_vertex_key(self, obj):
		if not isinstance(obj, int) or (obj not in range(0, self.n)):
			raise TypeError(f'object {obj} is not a valid vertex key')
			
	@staticmethod
	def __validate_posint(value):
		if not isinstance(value, int):
			raise TypeError(f'value {value} is not an integer')
		if value <= 0:
			raise ValueError(f'integer {value} is not positive')


##############################################################################

def get_random_graph(n, p, directed=False):  # DIRECTED/UNDIRECTED
	# TODO: validate n and p
	G = Graph(n, directed)
	if p == 0.0: return G

	for u in G.V():
		for v in G.V():
			if G.directed:
				if random.uniform(0, 1) <= p:
					G.add_edge(u, v)
			else:
				if u < v and random.uniform(0, 1) <= p:
					G.add_edge(u, v)
	return G


def get_random_tree(n):  # UNDIRECTED
	# Kruskal's Algorithm: (from Wikipedia)
	######################################################################
	# 	algorithm Kruskal(G) is
	# 		F:= ∅
	# 		for each v ∈ G.V do
	# 			MAKE-SET(v)
	# 		for each (u, v) in G.E ordered by weight(u, v), increasing do
	# 			if FIND-SET(u) ≠ FIND-SET(v) then
	# 				F:= F ∪ {(u, v)} ∪ {(v, u)}
	# 				UNION(FIND-SET(u), FIND-SET(v))
	# 		return F
	######################################################################
	mst = Graph(n)
	vertices = unionfind.WQUPC(n)
	edges = [(u, v) for v in mst.V() for u in mst.V() if u < v]
	random.shuffle(edges)
	for (u, v) in edges:
		# TODO: Stop earlier if already found tree.
		if vertices.find(u) != vertices.find(v):
			mst.add_edge(u, v)
			vertices.union(u, v)
	return mst


def get_random_connected_graph(n, p):  # UNDIRECTED
	G = get_random_tree(n)
	if p == 0.0: return G
	edges = [(u, v) for v in G.V() for u in G.V() if u < v]
	for (u, v) in edges:
		if not G.is_edge(u, v) and random.uniform(0, 1) <= p:
			G.add_edge(u, v)
	return G


# TODO: Find distances using DFS as well?
def DFS(G, s, ondiscovery=lambda w, v: None):
	# TODO: Validate G (graph) and s (vertex), and ondiscovery.

	discovered = {s}
	ondiscovery(s, None)
	stack = [s]
	while len(stack) > 0:
		v = stack.pop()
		for w in G.nhood(v):
			if w not in discovered:
				discovered.add(w)
				ondiscovery(w, v)  # e.g., record discoverd -> parent relation
				stack.append(w)


def BFS(G, s, ondiscovery=lambda w, v: None):
	# TODO: Validate G (graph) and s (vertex), and ondiscovery.

	discovered = {s}
	ondiscovery(s, None)
	queue = deque()
	queue.append(s)
	while len(queue) > 0:
		v = queue.popleft()
		for w in G.nhood(v):
			if w not in discovered:
				discovered.add(w)
				ondiscovery(w, v)
				queue.append(w)


def BFS_shortest_paths(G, s):
	# TODO: Validate G (graph) and s (vertex).
	T = Graph(G.n, directed=True)  # shortest-paths tree (w.r.t s)
	dists = dict()  # map vertext v to dist(s, v)

	def ondiscovery(w, v):
		if w == s:
			dists[s] = 0
		else:
			T.add_edge(w, v)
			dists[w] = dists[v] + 1

	BFS(G, s, ondiscovery=ondiscovery)
	return (T, dists)


def find_farthest_vertex(G, s):
	# TODO: Validate G (graph) and s (vertex).
	dists = BFS_shortest_paths(G, s)[1]
	t = sorted(dists, key=dists.get)[-1]
	return (t, dists[t])


def find_graph_diameter_endpoints(G):
	# TODO: Validate G (CONNECTED graph). (and that G is not empty)

	diameter = 0
	endpoints = (None, None)
	for w in G.V():
		u, dist = find_farthest_vertex(G, w)  # BFS	
		# if (dist > diameter) \  # doesn't make a difference :()
		# 	or (dist == diameter and random.randint(0, 1) == 0):
		if dist > diameter:
			diameter = dist
			endpoints = (w, u)

			# endpoints = (u, w)
			# TODO: This swap affects performence (~ 1% difference). Why?
	return (endpoints, diameter)


def find_tree_diameter_endpoints(G):
	# TODO: Validate G (graph). (and that G is a non-empty tree?)
	
	# with two BFSs
	w = next(G.V())  # pick arbitrary vertex
	# w = random.randint(0, G.n - 1)  # doesn't make a difference :()
	u, _ = find_farthest_vertex(G, w)  # BFS 1
	v, dist = find_farthest_vertex(G, u)  # BFS 2
	return ((u, v), dist)


def random_walk(G, s, t):
	# TODO: Validate G (graph) and s,t (vertices). (and that t is reachable from s?)
	w = s
	num_steps = 0
	while w != t:
		w = random.choice(G.nhood(w))
		num_steps += 1
	return num_steps


##############################################################################
### main ###
############

def main():
	pass  # TODO: Testing.

if __name__ == '__main__': main()
