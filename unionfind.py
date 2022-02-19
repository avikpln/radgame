'''The unionfind module'''

##############################################################################
### WQUPC ###
#############
class WQUPC:
	'''Implementation of the union-find DS: weighted QU + path compression'''

	def __init__(self, N: int) -> None:
		'''Initialize union-find data structure with N objects (0 to N-1).'''
		if not isinstance(N, int):
			raise TypeError(f'argument should be of type int')
		if N <= 0:
			raise ValueError('argument should be positive')

		self.id = [i for i in range(N)]
		self.size = [1] * N

	def __str__(self) -> str:
		return str(self.get_connected_components())

	def union(self, p: int, q: int) -> None:
		'''Add connection between p and q.'''
		i, j = self.root(p), self.root(q)
		if i == j: return
		if self.size[i] <= self.size[j]:
			self.id[i] = j
			self.size[j] += self.size[i]
		else:
			self.id[j] = i
			self.size[i] += self.size[j]

	def find(self, p: int) -> int:
		'''Component identifier for p (0 to N-1).'''
		return self.root(p)

	def connected(self, p: int, q: int) -> bool:
		'''Are p and q in the same component?'''
		return self.find(p) == self.find(q)

	def root(self, i):
		# Two-pass implementation.
		j = i  # save original
		while i != self.id[i]:
			i = self.id[i]

		while j != i:
			temp = self.id[j]
			self.id[j] = i
			j = temp

		# # Simpler one-pass variant. (OK in practice)
		# while i != self.id[i]:
		# 	self.id[i] = self.id[self.id[i]]
		# 	i = self.id[i]

		return i
	
	def count(self) -> int:
		'''Number of components.'''
		return len(self.get_connected_components())

	def get_connected_components(self) -> list:
		disjoint_sets = dict()
		for p in range(len(self.id)):
			i = self.find(p)
			if disjoint_sets.get(i):
				disjoint_sets[i].add(p)
			else:
				disjoint_sets[i] = {p}
		return list(disjoint_sets.values())


##############################################################################
### main ###
############

def main():
	pass  # TODO: Testing.

if __name__ == '__main__': main()
