'''The radgame module (UML)'''

##############################################################################
### Location ###
################
class Location:  # UML [data type]
	'''The Location data type'''


##############################################################################
### Direction ###
#################
class Direction:  # UML [data type]
	'''The Direction data type'''


##############################################################################
### Topology ###
################
class Topology:  # UML [data type]
	'''The Topology data type'''


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
		self.__owner = owner

	def open(self) -> Enterable:  # UML [method]
		pass


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
		pass

	def get_door(self) -> Door:  # UML [method]
		pass

	def detach(self):  # UML [method]
		pass

	def toggle_mark(self):  # UML [method]
		pass

	def is_marked(self) -> bool:  # UML [method]
		pass


##############################################################################
### WelcomeCell ###
###################
class WelcomeCell(Cell):  # UML [class]
	'''The WelcomeCell class'''


##############################################################################
### Room ###
############
class Room(Enterable):  # UML [class]
	'''The Room class'''

	def __init__(self, id):  # UML [attribute]
		self.__id = id

	def get_id(self) -> int:  # UML [method]
		pass

	def add_door(self, door: Door, location: Location):  # UML [method]
		pass

	def peek(self, location: Location) -> Door:  # UML [method]
		pass

	def remove_door(self, location: Location):  # UML [method]
		pass

	def toggle_mark(self, location: Location):  # UML [method]
		pass

	def is_marked(self, location: Location) -> bool:  # UML [method]
		pass

	def clear(self):  # UML [method]
		pass


##############################################################################
### Walker ###
##############
class Walker:  # UML [class]
	'''The Walker class'''

	def __init__(self):  # UML [attribute]
		self.__id = None
		self._room = None
		self._location = None

	def get_id(self) -> int:  # UML [method]
		pass

	def get_room(self) -> Room:  # UML [method]
		pass

	def get_location(self) -> Location:  # UML [method]
		pass

	def enter(self, room: Room):  # UML [method]
		pass

	def inspect(self):  # UML [method]
		pass

	def toggle_mark(self):  # UML [method]
		pass

	def move(self, direction: Direction):  # UML [method]
		pass

	def exit(self):  # UML [method]
		pass


##############################################################################
### Player ###
##############
class Player(Walker):  # UML [class]
	'''The Player class'''

	def __init__(self):  # UML [attribute]
		self.__trace = list()

	def play(self):  # UML [method]
		pass

	def undo(self):  # UML [method]
		pass

	def stop(self):  # UML [method]
		pass


##############################################################################
### Randy ###
#############
class Randy(Walker):  # UML [class]
	'''Randy March – The Random Walker'''

	def start(self):  # UML [method]
		pass

	def step(self):  # UML [method]
		pass

	def halt(self):  # UML [method]
		pass


##############################################################################
### Network ###
###############
class Network:  # UML [class]
	'''The Network class'''

	def __init__(self):  # UML [attribute]
		self.__visitors = None

	def build(self, topology: Topology):  # UML [method]
		pass

	def accept(self, walker: Walker):  # UML [method]
		pass

	def exists(self, walker: Walker) -> bool:  # UML [method]
		pass

	def finished(self, walker: Walker) -> bool:  # UML [method]
		pass

	def release(self, walker: Walker):  # UML [method]
		pass

	def destroy(self):  # UML [method]
		pass


##############################################################################
### Game ###
############
class Game:  # UML [class]
	'''The Game class'''

	def __init__(self):  # UML [attribute]
		self.__maze = None

	def play(self):  # UML [method]
		pass

	def reset(self):  # UML [method]
		pass

	def stop(self):  # UML [method]
		pass

	def quit(self):  # UML [method]
		pass

	def player_move(self, direction: Direction):  # UML [method]
		pass

	def player_inspect(self):  # UML [method]
		pass

	def player_undo(self):  # UML [method]
		pass

	def player_toggle_mark(self):  # UML [method]
		pass
