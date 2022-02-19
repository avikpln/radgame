'''The radgame module'''

# --- IMPORTS --- #
from collections import namedtuple
from enum import Enum
import random

import graph

# --- VALIDATION --- #
def VALIDATE_TYPE(obj, type_):
	if not isinstance(obj, type_):
		expected = type_.__name__
		got = type(obj).__name__
		raise TypeError(
			f'expected {expected} object, got {got} instead: {obj}'
		)

def VALIDATE_TYPE_OR_NONE(obj, type_):
	if obj:
		VALIDATE_TYPE(obj, type_)

def VALIDATE_TYPE_POSINT(value):
	VALIDATE_TYPE(value, int)
	if value <= 0:
		raise ValueError(f'value {value} is not a positive integer')

def VALIDATE_TYPE_INRANGE(value, type_, range_):
		VALIDATE_TYPE(value, type_)
		if not range_[0] <= value <= range_[1]:
			raise ValueError(f'value {value} is out of range {range_}')

##############################################################################
### Location ###
################
Location = namedtuple('Location', 'x y')  # UML [data type]


##############################################################################
### Direction ###
#################
class Direction(Enum):  # UML [data type]
	'''The Direction data type'''
	LEFT = 'LEFT'
	RIGHT = 'RIGHT'
	UP = 'UP'
	DOWN = 'DOWN'


##############################################################################
### Topology ###
################
Topology = \
	namedtuple('Topology', 'graph entry exit rows columns')  # UML [data type]


##############################################################################
### Enterable ###
#################
class Enterable:  # UML [interface]
	'''The Enterable interface'''


##############################################################################
### Door ###
############
class Door:  # UML [class]
	'''The Door class'''

	def __init__(self, owner: Enterable):  # UML [attribute]
		VALIDATE_TYPE(owner, Enterable)
		self.__owner = owner

	def open(self) -> Enterable:  # UML [method]
		return self.__owner


##############################################################################
### ExitDoor ###
################
class ExitDoor(Door):  # UML [class]
	'''The ExitDoor class'''


##############################################################################
### Cell ###
############
class Cell:  # UML [class]
	'''The Cell class'''

	def __init__(self):  # UML [attribute]
		self.__door = None
		self.__marked = False

	def attach(self, door: Door):  # UML [method]
		self.__door = door

	def get_door(self) -> Door:  # UML [method]
		return self.__door

	# this method will be useful in breaking circular references
	def detach(self):  # UML [method]
		self.__door = None

	def toggle_mark(self):  # UML [method]
		self.__marked = not self.__marked

	def is_marked(self) -> bool:  # UML [method]
		return self.__marked


##############################################################################
### WelcomeCell ###
###################
class WelcomeCell(Cell):  # UML [class]
	'''The WelcomeCell class'''

	def attach(self, door):
		raise NotImplementedError('cannot attach doors to welcome cell')


##############################################################################
### Room ###
############
class Room(Enterable):  # UML [class]
	'''The Room class'''

	def __init__(self, id, rows, columns, welcome_loc = None):  # UML [attribute]
		VALIDATE_TYPE_POSINT(rows)
		VALIDATE_TYPE_POSINT(columns)
		VALIDATE_TYPE_OR_NONE(welcome_loc, Location)
		self.__id = id
		self.__rows = rows
		self.__columns = columns

		self.__set_welcome_location(welcome_loc) # initial visitor/walker location
		self.__create_cells()

	def get_id(self) -> int:  # UML [method]
		return self.__id

	get_dimensions = lambda self: (self.__rows, self.__columns)
	get_welcome_location = lambda self: self.__welcome_loc

	get_available_locs = lambda self: self.__available_locs.copy()
	get_occupied_locs = lambda self: self.__occupied_locs.copy()

	get_cell = lambda self, location: self.__cells[location]

	def add_door(self, door: Door, location: Location=None):  # UML [method]
		'''It's a door management thingy'''
		VALIDATE_TYPE(door, Door)
		# TODO: Validate also location is in range (in all methods).
		VALIDATE_TYPE_OR_NONE(location, Location)

		if len(self.__available_locs) == 0:
			raise RuntimeError('no available locations')

		# FIXME: Input location is ignored.
		location = random.choice(self.__available_locs)

		self.__available_locs.remove(location)
		self.__occupied_locs.append(location)
		
		self.get_cell(location).attach(door)
		return True

	def peek(self, location: Location) -> Door:  # UML [method]
		VALIDATE_TYPE(location, Location)

		if self.is_occupied(location):
			return self.get_cell(location).get_door()
		else:
			return None

	def remove_door(self, location: Location):  # UML [method]
		VALIDATE_TYPE(location, Location)

		if self.is_occupied(location):
			self.get_cell(location).detach()
			
			self.__occupied_locs.remove(location)
			self.__available_locs.append(location)
		else:
			raise RuntimeError('cell in given location is not occupied')
		return True

	def toggle_mark(self, location: Location):  # UML [method]
		VALIDATE_TYPE(location, Location)
		if location == self.get_welcome_location():
			print('Cannot mark welcome location.')
		elif self.is_occupied(location):
			print('Cannot mark occupied locations.')
		else:
			self.get_cell(location).toggle_mark()
			return True
		return False

	def is_marked(self, location: Location) -> bool:  # UML [method]
		VALIDATE_TYPE(location, Location)
		return self.get_cell(location).is_marked()

	def clear(self):  # UML [method]
		for x in range(self.__columns):
			for y in range(self.__rows):
				location = Location(x, y)
				if self.is_occupied(location):
					self.remove_door(location)

	def is_available(self, location):
		VALIDATE_TYPE(location, Location)
		return location in self.__available_locs

	def is_occupied(self, location):
		VALIDATE_TYPE(location, Location)
		return location in self.__occupied_locs

	def is_exit_location(self, location):
		VALIDATE_TYPE(location, Location)
		return isinstance(self.get_cell(location).get_door(), ExitDoor)

	def __set_welcome_location(self, location=None):
		if not location:
			x = random.randint(0, self.__columns-1)
			y = random.randint(0, self.__rows-1)
			location = Location(x, y)
		self.__welcome_loc = location

	def __create_cells(self):
		self.__cells = dict()
		self.__available_locs = list()
		self.__occupied_locs = list()
		for x in range(self.__columns):
			for y in range(self.__rows):
				location = Location(x, y)
				if (x, y) == self.get_welcome_location():
					self.__cells[location] = WelcomeCell()
					# NOTE: Welcome location is reserved.
				else:
					self.__cells[location] = Cell()
					self.__available_locs.append(location)


##############################################################################
### Walker ###
##############
class Walker:  # UML [class]
	'''The Walker class'''

	__id_counter = 1

	def __init__(self):  # UML [attribute]
		self.__id = Walker.__generate_id()
		self._clear()

	def get_id(self) -> int:  # UML [method]
		return self.__id

	def get_room(self) -> Room:  # UML [method]
		return self._room

	def get_location(self) -> Location:  # UML [method]
		return self._location

	def get_prev_room(self):
		return self._prev_room

	def get_prev_location(self):
		return self._prev_location

	def enter(self, room: Room, location: Location=None):  # UML [method]
		VALIDATE_TYPE(room, Room)
		# TODO: Validate also location is in range.
		VALIDATE_TYPE_OR_NONE(location, Location)
		if self.get_room():
			raise RuntimeError('cannot be in two rooms at the same time')
		elif not isinstance(room, Room):  # FIXME: We already validate Room type.
			raise RuntimeError('walker can only enter rooms')
		else:
			self.__set_room(room)
			if not location:
				location = room.get_welcome_location()
			self.__set_location(location)

	def inspect(self):  # UML [method]
		location = self.get_location()
		door = self.get_room().peek(location)
		if door != None:
			self.exit()
			self.enter(door.open())

	def toggle_mark(self):  # UML [method]
		location = self.get_location()
		self.get_room().toggle_mark(location)

	def move(self, direction: Direction):  # UML [method]
		VALIDATE_TYPE(direction, Direction)
		rows, columns = self.get_room().get_dimensions()
        
		location = self.get_location()
		if direction == Direction.LEFT:
			if location.x > 0:
				location = Location(location.x - 1, location.y)
		elif direction == Direction.RIGHT:
			if location.x < columns - 1:
				location = Location(location.x + 1, location.y)
		elif direction == Direction.UP:
			if location.y > 0:
				location = Location(location.x, location.y - 1)
		elif direction == Direction.DOWN:
			if location.y < rows - 1:
				location = Location(location.x, location.y + 1)
		else:
			assert False  # sanity check

		self.__set_location(location)

	def exit(self):  # UML [method]
		location, room = self.get_location(), self.get_room()
		if not room:
			raise RuntimeError('not in a room to exit from')
		self._clear()
		self.__set_prev_room(room)
		self.__set_prev_location(location)

	def _clear(self):
		self.__set_room(None)
		self.__set_location(None)
		self.__set_prev_room(None)
		self.__set_prev_location(None)

	def __set_room(self, room):
		self._room = room

	def __set_location(self, location):
		self._location = location

	def __set_prev_room(self, prev_room):
		self._prev_room = prev_room

	def __set_prev_location(self, prev_location):
		self._prev_location = prev_location

	@staticmethod
	def __generate_id():
		id = Walker.__id_counter
		Walker.__id_counter += 1
		return id


##############################################################################
### Player ###
##############
class Player(Walker):  # UML [class]
	'''The Player class'''

	# FIXME: Move to Walker.
	# TODO: Rename State to Position.
	State = namedtuple('State', 'room location')

	def __init__(self):  # UML [attribute]
		super().__init__()
		self.__trace = None

	def inspect(self):  # UML [method]
		if self.get_location() == self.get_room().get_welcome_location():
			self.undo()
		else:
			super().inspect()

	def exit(self):  # UML [method]
		# FIXME: invoke super.exit(), then use get_prev_location
		# TODO: Change prev_location to last_exit_location
		room, location = self.get_room(), self.get_location()
		super().exit()
		self.__trace.append(Player.State(room, location))

	def play(self):  # UML [method]
		self.__set()

	def undo(self):  # UML [method]
		if len(self.__trace) > 0:
			state = self.__trace.pop()
			super().exit()
			self.enter(state.room, state.location)
		else:
			print("Source room cannot be exited. You are stuck here FOREVER.")

	def stop(self):  # UML [method]
		self.__unset()

	def __set(self):
		self.__trace = list()

	def __unset(self):
		self._clear()
		self.__trace.clear()


##############################################################################
### Randy ###
#############
class Randy(Walker):  # UML [class]
	'''Randy March – The Random Walker'''

	class State(Enum):
		IDLE = 'IDLE'
		CHOOSING = 'CHOOSING'
		WALKING = 'WALKING'
		DONE = 'DONE'

	def __init__(self):
		super().__init__()
		self.__set_state(Randy.State.IDLE)

	get_state = lambda self: self.__state

	def start(self):  # UML [method]
		self.__set()

	def step(self):  # UML [method]
		state = self.get_state()
		if state == Randy.State.CHOOSING:
			self.__choose()
		elif state == Randy.State.WALKING:
			self.__walk()
		elif state == Randy.State.DONE:
			print('Randy is done, no more steps for Randy.')
		elif state == Randy.State.IDLE:
			raise RuntimeError('Randy is idle')
		else:
			assert False  # What?

	def halt(self):  # UML [method]
		self.__unset()

	def get_state(self):
		return self.__state

	def __set(self):
		self.__goingto = None
		self.__set_state(Randy.State.CHOOSING)

	def __unset(self):
		self._clear()
		self.__set_state(Randy.State.IDLE)

	def __set_state(self, state):
		self.__state = state

	def __choose(self):
		room = self.get_room()
		occupied_locs = room.get_occupied_locs()

		self.__goingto = None
		for location in occupied_locs:
			# NOTE: I guess Randy is not that stupid/random. However, this has
			# no effect if the target is a leaf.
			if room.is_exit_location(location):
				self.__goingto = location

		if not self.__goingto:
			# NOTE: This is another non-random behavior by Randy; he will not
			# go back to the room he just came from.
			prev_room = self.get_prev_room()
			if prev_room and len(occupied_locs) > 1:
				for location in occupied_locs:
					if room.peek(location).open() == prev_room:
						occupied_locs.remove(location)
						break
			self.__goingto = random.choice(occupied_locs)

		self.__set_state(Randy.State.WALKING)

	def __walk(self):
		location, curr_room = self.get_location(), self.get_room()

		if location == self.__goingto:
			if curr_room.is_exit_location(self.__goingto):
				# Randy found the golden door!
				self.__set_state(Randy.State.DONE)
			else:
				self.__set_state(Randy.State.CHOOSING)
			self.inspect()
		else:
			# FIXME: Why location[0] and not location.x?
			if location[0] == self.__goingto[0]:
				axis = 1
			elif location[1] == self.__goingto[1]:
				axis = 0
			else:
				axis = random.randint(0, 1)  # coin flip

			if axis == 0:
				if location[0] < self.__goingto[0]:
					self.move(Direction.RIGHT)
				else:
					self.move(Direction.LEFT)
			else:  # axis == 1
				if location[1] < self.__goingto[1]:
					self.move(Direction.DOWN)
				else:
					self.move(Direction.UP)


##############################################################################
### Network ###
###############
class Network:  # UML [class]
	'''The Network class'''

	class State(Enum):
		ACTIVE = 'ACTIVE'
		DISABLED = 'DISABLED'

	def __init__(self):  # UML [attribute]
		self.__set_state(Network.State.DISABLED)  # disable network on startup
		self.__rooms = None  # network rooms
		self.__visitors = None  # visitor registry

	get_state = lambda self: self.__state
	get_visitors = lambda self: self.__visitors.copy()

	def build(self, topology: Topology):  # UML [method]
		if self.get_state() == Network.State.ACTIVE:
			raise RuntimeError('network is active')
		VALIDATE_TYPE(topology, Topology)
		
		# create rooms
		self.__rooms = dict()
		for u in topology.graph.V():
			self.__rooms[u] = Room(u, topology.rows, topology.columns)

		# add doors to rooms
		for u in topology.graph.V():
			if u == topology.exit:
				continue  # no doors in exit room
			for v in topology.graph.nhood(u):
				if v == topology.exit:
					DoorType = ExitDoor
				else:
					DoorType = Door
				door = DoorType(self.__rooms[v])
				self.__rooms[u].add_door(door)
		
		# entry and exit rooms
		self.__entry_room = self.__rooms[topology.entry]
		self.__exit_room = self.__rooms[topology.exit]

		# initialize visitors
		self.__visitors = set()

		self.__activate()  # activate netork

	def accept(self, walker: Walker):  # UML [method]
		self.__assert_active()
		VALIDATE_TYPE(walker, Walker)
		if self.exists(walker):
			raise RuntimeError('walker already inside network')

		self.__register_visitor(walker)
		walker.enter(self.__get_entry_room())

	def exists(self, walker: Walker) -> bool:  # UML [method]
		self.__assert_active()
		VALIDATE_TYPE(walker, Walker)
		return walker in self.__visitors

	def finished(self, walker: Walker) -> bool:  # UML [method]
		self.__assert_active()
		VALIDATE_TYPE(walker, Walker)
		return walker.get_room() == self.__get_exit_room()

	def release(self, walker: Walker):  # UML [method]
		self.__assert_active()
		VALIDATE_TYPE(walker, Walker)
		if not self.exists(walker):
			raise RuntimeError('walker is not inside network')

		walker.exit()
		self.__unregister_visitor(walker)

	def destroy(self):  # UML [method]
		self.__assert_active()

		self.__disable()  # disable network

		self.__visitors = None

		# clear rooms (door detachments prevent circular references)
		for room in self.__rooms.values():
			room.clear()
		self.__rooms = None

	def __set_state(self, state):
		self.__state = state

	def __get_entry_room(self):
		return self.__entry_room

	def __get_exit_room(self):
		return self.__exit_room

	def __activate(self):
		self.__set_state(Network.State.ACTIVE)
		self.__visitors = set()  # visitor registry

	def __assert_active(self):
		if self.get_state() != Network.State.ACTIVE:
			raise RuntimeError('network is not active')

	def __disable(self):
		self.__set_state(Network.State.DISABLED)
		self.__visitors = None

	def __register_visitor(self, visitor):
		self.__visitors.add(visitor)

	def __unregister_visitor(self, visitor):
		self.__visitors.remove(visitor)


##############################################################################
### Game ###
############
class Game:  # UML [class]
	'''The Game class'''

	class State(Enum):
		IDLE = 'IDLE'
		PLAYING = 'PLAYING'
		TRIUMPH = 'TRIUMPH'
		QUIT = 'QUIT'

# --- DEFAULTS --- #
	__ROWS_RANGE = (2, 5)
	__COLUMNS_RANGE = (2, 5)
	__NUMROOMS_RANGE = (2, __ROWS_RANGE[1] * __COLUMNS_RANGE[1])
	__NUMRANDYS_RANGE = (0, 50)

	__DEFAULT_ROWS = 5
	__DEFAULT_COLUMNS = 5
	__DEFAULT_NUMROOMS = __DEFAULT_ROWS * __DEFAULT_COLUMNS
	__DEFAULT_NUMRANDYS = 5

# --- CONFIGURATION --- #
	def __init__(self, **kwargs):  # UML [attribute]
		self.__parse_arguments(**kwargs)  # configuration and defaults values
		
		self.__set_state(Game.State.IDLE)
		self.__maze = Network()
		self.__player = Player()
		self.__randys = []
		for _ in range(self.get_numrandys()):
			self.__randys.append(Randy())

	# TODO: Move these arguments to the constructor?
	def __parse_arguments(self, **kwargs):
		# default values
		self.__rows = Game.__DEFAULT_ROWS
		self.__columns = Game.__DEFAULT_COLUMNS
		self.__numrooms = Game.__DEFAULT_NUMROOMS
		self.__numrandys = Game.__DEFAULT_NUMRANDYS

		# parse user arguments
		for key, value in kwargs.items():
			if key == 'rows':
				VALIDATE_TYPE_INRANGE(value, int, Game.__ROWS_RANGE)
				self.__rows = kwargs['rows']
			if key == 'columns':
				VALIDATE_TYPE_INRANGE(value, int, Game.__COLUMNS_RANGE)
				self.__columns = kwargs['columns']
			if key == 'numrooms':
				VALIDATE_TYPE_INRANGE(value, int, Game.__NUMROOMS_RANGE)
				self.__numrooms = kwargs['numrooms']
			if key == 'numrandys':
				VALIDATE_TYPE_INRANGE(value, int, Game.__NUMRANDYS_RANGE)
				self.__numrandys = kwargs['numrandys']
			else:
				raise KeyError(f"invalid keyword argument '{key}'")

		# consistency
		if self.__numrooms > self.__rows * self.__columns:
			raise ValueError(
				f'inconsistent number of rooms: {self.__numrooms}'
		)

# --- GETTERS --- #
	get_state = lambda self: self.__state

	get_dimensions = lambda self: (self.__rows, self.__columns)
	get_numrooms = lambda self: self.__numrooms
	get_numrandys = lambda self: self.__numrandys

	get_player = lambda self: self.__player
	get_randys = lambda self: self.__randys

# --- PRSQ = Play, Reset, Stop, Quit --- #
	# PLAY
	def play(self):  # UML [method]
		state = self.get_state()
		if state == Game.State.QUIT:
			raise RuntimeError('got play request while on quit state')
		elif state == Game.State.PLAYING:
			print('You are already playing my dude.')
			return False

		self.__set()

		player = self.get_player()
		network = self.__get_network()
		network.accept(player)
		for randy in self.get_randys():
			network.accept(randy)
		player.play()

		self.__set_state(Game.State.PLAYING)
		return True

	# RESET
	def reset(self):  # UML [method]
		state = self.get_state()
		if state == Game.State.QUIT:
			raise RuntimeError('got reset request while on quit state')

		if state == Game.State.PLAYING:
			if not self.stop():
				return False
		return self.play()

	# STOP
	def stop(self):  # UML [method]
		state = self.get_state()
		if state == Game.State.QUIT:
			raise RuntimeError('got stop request while on quit state')
		elif state == Game.State.IDLE:
			print('What are you trying to stop?')
			return False

		self.__set_state(Game.State.IDLE)
		self.get_player().stop()
		for randy in self.get_randys():
			randy.halt()
		self.__unset()
		return True

	# QUIT
	def quit(self):  # UML [method]
		state = self.get_state()
		if state == Game.State.QUIT:
			raise RuntimeWarning('got quit request while on quit state')
		
		if state == Game.State.PLAYING:
			if not self.stop():
				return False
		self.__set_state(Game.State.QUIT)
		return True

# --- PLAYER ACTIONS --- #
	def player_move(self, direction: Direction):  # UML [method]
		if self.get_state() != Game.State.PLAYING:
			print('You are not playing.')
			return False
		VALIDATE_TYPE(direction, Direction)
		self.get_player().move(direction)
		return True

	def player_inspect(self):  # UML [method]
		if self.get_state() != Game.State.PLAYING:
			print('You are not playing.')
			return False
		player = self.get_player()
		player.inspect()
		network = self.__get_network()
		if network.finished(player):
			print('Player has finished the game. Well done!')
			network.release(player)
			player.stop()
			self.__set_state(Game.State.TRIUMPH)
		return True

	def player_undo(self):  # UML [method]
		if self.get_state() != Game.State.PLAYING:
			print('You are not playing.')
			return False
		self.get_player().undo()
		return True

	def player_toggle_mark(self):  # UML [method]
		if self.get_state() != Game.State.PLAYING:
			print('You are not playing.')
			return False
		self.get_player().toggle_mark()
		return True

# --- SETTING --- #
	def __set_state(self, state):
		self.__state = state

	def __set(self):
		self.__create_network()

	def __unset(self):
		self.__destroy_network()

	def __create_network(self):
		G = self.__get_graph(self.get_numrooms())
		src, tgt = self.__get_endpoints(G)
		rows, columns = self.get_dimensions()
		self.__get_network().build(Topology(G, src, tgt, rows, columns))

	def __destroy_network(self):
		self.__get_network().destroy()

	__get_network = lambda self: self.__maze

	def __get_graph(self, n):
		return graph.get_random_tree(n)
	
	def __get_endpoints(self, G):
		return graph.find_tree_diameter_endpoints(G)[0]


##############################################################################
### main ###
############

def main():
	# TODO: Testing.

	# "c'tors"
	Door(Enterable())
	ExitDoor(Enterable())
	Cell()
	WelcomeCell()
	Room(0, 5, 5)
	Walker()
	Player()
	Randy()
	Network()
	Game()

if __name__ == '__main__': main()
