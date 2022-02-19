'''The radgame_testing module'''

# --- IMPORTS --- #
from graph import Graph
import graph


##############################################################################
### GameSetting ###
###################
class GameSetting:
	'''The GameSetting (abstract) class'''

	def get_graph(self, size: int) -> Graph:
		raise NotImplementedError()
	
	def get_endpoints(self, G: Graph) -> tuple[int, int]:
		raise NotImplementedError()


##############################################################################
### PathGraph ###
#################
class PathGraph(GameSetting):
	'''The PathGraph class'''

	def get_graph(self, size):
		G = Graph(size)
		for u in range(size - 1):
			G.add_edge(u, u + 1)
		return G

	def get_endpoints(self, G):
		return (0, G.n - 1)


##############################################################################
### CandyGraph ###
##################
class CandyGraph(GameSetting):
	'''The CandyGraph class'''

	def __init__(self, k=15):
		self.__k = k

	def get_graph(self, size):
		G = Graph(size)
		for u in range(self.__k):
			for v in range(u + 1, self.__k):
				G.add_edge(u, v)
		for u in range(self.__k - 1, size - 1):
			G.add_edge(u, u + 1)
		return G

	def get_endpoints(self, G):
		return (0, G.n - 1)


##############################################################################
### RandomTreeDiameter ###
##########################
class RandomTreeDiameter(GameSetting):
	'''The RandomTreeDiameter class'''

	def get_graph(self, size):
		return graph.get_random_tree(size)

	def get_endpoints(self, G):
		return graph.find_tree_diameter_endpoints(G)[0]


##############################################################################
### RandomTreeDiameterCliqueNaive ###
#####################################
class RandomTreeDiameterCliqueNaive(GameSetting):
	'''The RandomTreeDiameterCliqueNaive class'''

	def __init__(self, from_level=0, to_level=9):
		self.__from_level = from_level
		self.__to_level = to_level
		# TODO: Test for to_level values > 0.

	def get_graph(self, size):
		G = graph.get_random_tree(size)
		# G = graph.get_random_connected_graph(size, p=0.0)
		(s, t), _ = graph.find_tree_diameter_endpoints(G)

		_, dists = graph.BFS_shortest_paths(G, s)

		for u in G.V():
			for v in G.V():
				if u >= v or G.is_edge(u, v):
						continue
				minlvl = min(dists[u], dists[v])
				maxlvl = max(dists[u], dists[v])
				if self.__from_level <= minlvl and maxlvl <= self.__to_level:
					G.add_edge(u, v)

		self.__endpoints = (s, t)
		return G

	def get_endpoints(self, G):
		return self.__endpoints


##############################################################################
### RandomTreeDiameterCliqueWise ###
####################################
class RandomTreeDiameterCliqueWise(GameSetting):
	'''The RandomTreeDiameterCliqueWise class'''

	def __init__(self, cliquesize=17):
		self.__cliquesize = cliquesize

	def get_graph(self, size):
		G = graph.get_random_tree(size)
		# G = graph.get_random_connected_graph(size, p=0.0)
		# (s, t), _ = graph.find_tree_diameter_endpoints(G)
		(t, s), _ = graph.find_tree_diameter_endpoints(G)  # [SWAP]

		_, dists = graph.BFS_shortest_paths(G, s)
		# TODO: Is there a bias caused by ignoring vertices from nearests with
		# distance equal to the distance of some vertex in nearests?
		nearests = sorted(dists, key=dists.get)[:self.__cliquesize]

		# build clique
		for u in nearests:
			for v in nearests:
				if u < v and not G.is_edge(u, v):
					G.add_edge(u, v)

		self.__endpoints = (s, t)
		return G

	def get_endpoints(self, G):
		return self.__endpoints


##############################################################################
### RandomConnectedGraphDiameter ###
####################################
class RandomConnectedGraphDiameter(GameSetting):
	'''The RandomConnectedGraphDiameter class'''

	def get_graph(self, size):
		return graph.get_random_connected_graph(size, p=0.0)
		# E[p=0.0] = ?
		# E[p=0.01] = ?
		# E[p=0.1] = ?
		# E[p=0.25] = ?
		# E[p=0.5] = ?
		# E[p=0.75] = ?
		# E[p=0.99] = ?
		# E[p=1.0] = ?

	def get_endpoints(self, G):
		return graph.find_graph_diameter_endpoints(G)[0]


##############################################################################
### GameSettingTester ###
#########################
class GameSettingTester:
	'''The GameSettingTester class'''

	@staticmethod
	def test(game_setting, graph_size, num_experiments):
		num_steps_sum = 0
		for _ in range(num_experiments):
			G = game_setting.get_graph(graph_size)
			(s, t) = game_setting.get_endpoints(G)
			num_steps = graph.random_walk(G, s, t)
			num_steps_sum += num_steps
		num_steps_avg = num_steps_sum / num_experiments
		print('Estimated expected number of steps:', num_steps_avg)
		# TODO: Estimate the variance as well.


##############################################################################
### main ###
############

def main():
	
	# find_tree_diameter_endpoints vs find_graph_diameter_endpoints
	# (25, 1E6) -> 265.566976 vs 274.069031  # TODO: Why? [SWAP]
	# CLIQUE-NAIVE: 771.434172
	# PATH: 575.573726  (of course, Randy is smarter than that)
	# CANDY: 2257.462491
	# CLIQUE-WISE: 976.265241
	# CLIQUE-WISE-SWAP: 1051.905525

	n = 25
	num_expr = 10000
	# GameSettingTester.test(RandomTreeDiameter(), n, num_expr)
	# GameSettingTester.test(RandomConnectedGraphDiameter(), n, num_expr)
	# GameSettingTester.test(RandomTreeDiameterCliqueNaive(), n, num_expr)
	GameSettingTester.test(RandomTreeDiameterCliqueWise(), n, num_expr)
	# GameSettingTester.test(PathGraph(), n, num_expr)
	# GameSettingTester.test(CandyGraph(), n, num_expr)

	# for _ in range(10000):
	# 	T = graph.get_random_tree(10)
	# 	diameter = graph.find_tree_diameter_endpoints(T)[1]
	# 	assert graph.find_graph_diameter_endpoints(T)[1] == diameter

if __name__ == '__main__': main()
