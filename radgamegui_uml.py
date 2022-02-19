'''The radgamegui module (UML)'''

from tkinter import Canvas
from radgame_uml import Game, Walker, Room, Cell, Door

##############################################################################
### BoundingBox ###
###################
class BoundingBox:  # UML [data type]
	'''The BoundingBox data type'''


##############################################################################
### DoorStyle ###
#################
class DoorStyle:  # UML [data type]
	'''The DoorStyle data type'''


##############################################################################
### CellStyle ###
#################
class CellStyle:  # UML [data type]
	'''The CellStyle data type'''


##############################################################################
### RoomStyle ###
#################
class RoomStyle:  # UML [data type]
	'''The RoomStyle data type'''


##############################################################################
### WalkerStyle ###
###################
class WalkerStyle:  # UML [data type]
	'''The WalkerStyle data type'''


##############################################################################
### Layout ###
##############
class Layout:  # UML [data type]
	'''The Layout data type'''


##############################################################################
### LayoutExtractor ###
#######################
class LayoutExtractor:  # UML [class]
	'''The LayoutExtractor class'''

	def extract(self, game: Game) -> Layout:  # UML [method]
		pass


##############################################################################
### Displayer ###
#################
class Displayer:  # UML [class]
	'''The Displayer class'''

	def __init__(self, canvas: Canvas, bbox: BoundingBox):  # UML [attribute]
		self.__canvas = canvas
		self.__bbox = bbox

	def display(self, layout: Layout):  # UML [method]
		pass


##############################################################################
### Announcer ###
#################
class Announcer:  # UML [class]
	'''The Announcer class'''

	def announce(self, canvas: Canvas, bbox: BoundingBox, text: str):  # UML [method]
		pass


##############################################################################
### GUI ###
###########
class GUI:  # UML [class]
	'''The GUI class'''
