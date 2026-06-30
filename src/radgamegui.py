'''The radgamegui module'''

# --- IMPORTS --- #
import tkinter as tk
from tkinter import ttk
from collections import namedtuple
import random
from datetime import timedelta

from radgame import *
from library import X11COLORS
from library import QUOTES

# --- MACROS --- #
COLORS = list(X11COLORS.keys())
GET_RANDOM_COLOR = lambda: random.choice(COLORS)
GET_RANDOM_QUOTE = lambda: random.choice(QUOTES)

##############################################################################
### BoundingBox ###
###################
BoundingBox = namedtuple('BoundingBox', 'x0 y0 width height')


##############################################################################
### DoorStyle ### # TODO: Create common interface Style?
#################
DoorStyle = namedtuple('DoorStyle', 'outline frontfill windowfill handlefill')


##############################################################################
### CellStyle ###
#################
CellStyle = \
	namedtuple('CellStyle', 'outline cascadeoutline cascadeshape mark')


##############################################################################
### RoomStyle ###
#################
RoomStyle = namedtuple('RoomStyle', 'outline background')


##############################################################################
### WalkerStyle ###
###################
WalkerStyle = namedtuple('WalkerStyle', 'scale outline fill')


##############################################################################
### Layout ###
##############
# NOTE: No type validation.
Layout = \
	namedtuple('Layout','door_styles cell_styles room_style walker_styles')


##############################################################################
### LayoutExtractor ###
#######################
class LayoutExtractor:
	'''The LayoutExtractor class'''

	def __init__(self, game,
				 get_door_style = lambda door: DoorStyle(),
				 get_cell_style = lambda cell: CellStyle(),
				 get_room_style = lambda room: RoomStyle(),
				 get_walker_style = lambda walker: WalkerStyle()):
		VALIDATE_TYPE(game, Game)
		self.__game = game

		self.__get_cell_style = get_cell_style
		self.__get_door_style = get_door_style
		self.__get_room_style = get_room_style
		self.__get_walker_style = get_walker_style

	# TODO: Split into several methods, one per style.
	def extract(self):
		game = self.__get_game()
		player = game.get_player()
		randys = game.get_randys()
		
		# extract room style
		room = player.get_room()
		room_style = self.__get_room_style(room)

		# initialize displayables -> style dictionaries
		door_styles = dict()
		cell_styles = dict()
		walker_styles = dict()

		# extract room dimensions
		rows, columns = room.get_dimensions()

		# extract door and cell styles
		for x in range(columns):
			for y in range(rows):
				location = Location(x, y)
				cell = room.get_cell(location)
				cell_style = self.__get_cell_style(cell)
				door = cell.get_door()
				door_style = self.__get_door_style(door) if door else None
				cell_styles[location] = cell_style
				door_styles[location] = door_style

		# extract randy walker styles
		for randy in randys:
			if randy.get_room() != room:
				continue  # display only randys inside player's room
			randy_style = self.__get_walker_style(randy)
			if not randy_style: break;
			randy_location = randy.get_location()
			if not walker_styles.get(randy_location):
				walker_styles[randy_location] = list()
			walker_styles[randy_location].append(randy_style)

		# extract player walker style and give it (front display) priority
		player_style = self.__get_walker_style(player)
		player_location = player.get_location()
		if not walker_styles.get(player_location):
			walker_styles[player_location] = list()
		walker_styles[player_location].append(player_style)

		# finally, return layout
		return Layout(door_styles, cell_styles, room_style, walker_styles)

	def clear(self):
		pass  # nothing to do here...

	def __get_game(self):
		return self.__game


##############################################################################
### Displayer ###
#################
class Displayer:
	'''The Displayer class'''

	# NOTE: For now, the given bounding box is ignored. The question is how to
	# use the bounding box; for example, we could force the displayer to
	# resize its drawing space to fit the given bounding box. We'll see...
	def __init__(self, canvas, bbox, cellwidth, cellheight):
		VALIDATE_TYPE(canvas, tk.Canvas)
		VALIDATE_TYPE(bbox, BoundingBox)
		VALIDATE_TYPE_POSINT(cellwidth)  # reasonable check
		VALIDATE_TYPE_POSINT(cellheight)  # reasonable check
		self.__canvas = canvas
		self.__bbox = bbox
		self.__cellwidth = cellwidth
		self.__cellheight = cellheight

	def display(self, layout):
		self.__display_room(layout)
		self.__display_cells_and_doors(layout)
		self.__display_walkers(layout)

	def __display_room(self, layout):
		style = layout.room_style
		x0, y0 = self.__bbox.x0, self.__bbox.y0
		x1 = x0 + self.__bbox.width - 1
		y1 = y0 + self.__bbox.height - 1
		self.__canvas.create_rectangle(x0, y0, x1, y1, outline=style.outline,
									   fill=style.background)

	def __display_cells_and_doors(self, layout):
		for location, cell_style in layout.cell_styles.items():
			x0 = self.__bbox.x0 + location.x*self.__cellwidth
			y0 = self.__bbox.y0 + location.y*self.__cellheight
			cell_bbox = \
				BoundingBox(x0, y0, self.__cellwidth, self.__cellheight)
			self.__display_cell(cell_bbox, cell_style)

			if layout.door_styles[location]:
				door_style = layout.door_styles[location]
				self.__display_door(cell_bbox, door_style)

	def __display_cell(self, bbox, style):
		x0, y0, width, height = bbox
		x1 = x0 + width - 1
		y1 = y0 + height - 1

		# display cell outline
		self.__canvas.create_rectangle(x0, y0, x1, y1, outline=style.outline)

		if style.cascadeoutline:
			# display cascading appearance
			for i in range(2, min(width, height)//2-1, 4):
				cx0, cy0 = x0 + i, y0 + i
				cx1, cy1 = x1 - i, y1 - i
				outline = style.mark if style.mark else style.cascadeoutline
				if style.cascadeshape == 'rectangle':
					self.__canvas.create_rectangle(cx0, cy0, cx1, cy1,
												   outline=outline)
				elif style.cascadeshape == 'oval':
					self.__canvas.create_oval(cx0, cy0, cx1, cy1,
											  outline=outline)
				else:
					assert False  # What?

	def __display_door(self, bbox, style):
		# TODO: Differet outlines for different door parts?
		outline = style.outline

		# display front
		x0 = bbox.x0 + bbox.width//5
		y0 = bbox.y0 + bbox.height//25
		x1 = bbox.x0 + bbox.width-1 - bbox.width//5
		y1 = bbox.y0 + bbox.height-1 - bbox.height//25
		self.__canvas.create_rectangle(x0, y0, x1, y1, outline=outline)
		self.__canvas.create_rectangle(x0+1, y0+1, x1-1, y1-1,
									   outline=outline, fill=style.frontfill)

		# display window
		x0 += bbox.width//12
		y0 += bbox.height//12
		x1 -= bbox.width//12
		y1 = y0 + bbox.height//3
		self.__canvas.create_rectangle(x0, y0, x1, y1, outline=outline)
		self.__canvas.create_rectangle(x0+1, y0+1, x1-1, y1-1,
									   outline=outline, fill=style.windowfill)

		# display handle
		x1 = x0 + bbox.width//8  # x0 doesn't change
		y0 = y1 + bbox.height//12
		y1 = y0 + bbox.height//8
		self.__canvas.create_oval(x0, y0, x1, y1, outline=outline,
								  fill=style.handlefill)

	def __display_walkers(self, layout):
		for location, styles in layout.walker_styles.items():
			assert len(styles) > 0  # sanity check

			x0 = self.__bbox.x0 + location.x*self.__cellwidth
			y0 = self.__bbox.y0 + location.y*self.__cellheight
			walker_bbox = \
				BoundingBox(x0, y0, self.__cellwidth, self.__cellheight)
			if len(styles) == 1:
				self.__display_walker(walker_bbox, styles[0])
			# [COLLISION] elif len(styles) == 2:
			# 	self.__display_walker_collision(walker_bbox, styles)
			else:
				self.__display_walker_crowd(walker_bbox, styles)

	def __draw_walker(self, bbox, scale, outline, fill, offset):
		x0, y0, width, height = bbox

		walkerwidth = round(scale * width)
		walkerheight = round(scale * height)

		x0 += (width - walkerwidth)//2 + offset[0]
		y0 += (3*(height - walkerheight))//4 + offset[1]
		x1 = x0 + walkerwidth
		y1 = y0 + walkerheight
		self.__canvas.create_oval(x0, y0, x1, y1, outline=outline, fill=fill)

	def __display_walker(self, bbox, style, offset=(0,0)):
		# self.__display_walker1(bbox, style, offset)
		self.__display_walker2(bbox, style, offset)

	def __display_walker1(self, bbox, style, offset):
		scale, outline, fill = style
		self.__draw_walker(bbox, scale, outline, fill[0], offset)

	def __display_walker2(self, bbox, style, offset):
		# draw walker with primary color first
		self.__display_walker1(bbox, style, offset)

		if not style.fill[1]:
			return

		# draw mixture of primary and secondary colors
		width = round(style.scale * bbox.width)
		height = round(style.scale * bbox.height)
		widthrange = range(width-4, 1, -1)
		heightrange = range(height-4, 1, -1)
		for drawwidth, drawheight in zip(widthrange, heightrange):
			i = drawwidth % 2
			scale = (drawwidth / width) * style.scale
			outline = style.fill[i]
			self.__draw_walker(bbox, scale,  outline, style.fill[i], offset)

	# [COLLISION] def __display_walker_collision(self, bbox, styles):
	# 	assert len(styles) == 2  # sanity check
	# 	# TODO: For now, we define a collision to inolve 2 walkers, and a
	# 	# crowd to be 3 walkers or more. How about making this threshold a
	# 	# parameter?

	# 	# display bigger walker first (prioritize second walker)
	# 	if styles[1].scale >= styles[0].scale:
	# 		self.__display_walker(bbox, styles[1])
	# 	else:
	# 		self.__display_walker(bbox, styles[0])

	# 	# display collision
	# 	walkerwidth = [None]*2
	# 	walkerheight = [None]*2
	# 	for i in (0, 1):
	# 		walkerwidth[i] = round(styles[i].scale * bbox.width)
	# 		walkerheight[i] = round(styles[i].scale * bbox.height)
	# 	minwidth = min(walkerwidth)
	# 	minheight = min(walkerheight)
	# 	widthrange = range(minwidth-4, 1, -1)
	# 	heightrange = range(minheight-4, 1, -1)
	# 	for walkerwidth, walkerheight in zip(widthrange, heightrange):
	# 		i = walkerwidth % 2
	# 		scale = (walkerwidth / minwidth) * styles[i].scale
	# 		outline = styles[i].fill
	# 		fill = styles[i].fill
	# 		style = WalkerStyle(scale, outline, fill)
	# 		self.__display_walker(bbox, style)

	def __display_walker_crowd(self, bbox, styles):
		assert len(styles) > 1  # sanity check
		for style in styles[:-1]:
			offset = (random.randint(-5, 5), random.randint(-5, 5))
			self.__display_walker(bbox, style, offset=offset)
		self.__display_walker(bbox, styles[-1])


##############################################################################
### Announcer ###
#################
class Announcer:  # UML [class]
	'''The Announcer class'''

	def announce(self, canvas: tk.Canvas, bbox: BoundingBox, text: str):  # UML [method]
		pass


##############################################################################
### GUIRandy ###
################
class GUIRandy():
	'''The GUIRandy class'''

	def __init__(self, randy):
		VALIDATE_TYPE(randy, Randy)
		self.randy = randy

	def start(self, game_frame, delay, refresh_callback):
		# TODO: Type validation of game_frame, delay?
		self.randy.start()
		self.set_refresh_request(False)
		self.__game_frame = game_frame
		self.__delay = delay
		self.__refresh_callback = refresh_callback
		self.__job = game_frame.after(delay, self.step)

	def step(self):
		self.randy.step()

		if self.randy.get_state() == Randy.State.CHOOSING:
			self.set_refresh_request(True)
		self.__refresh_callback(self)

		if self.randy.get_state() != Randy.State.IDLE:
			self.__job = self.__game_frame.after(self.__delay, self.step)

	def halt(self):
		self.__game_frame.after_cancel(self.__job)
		self.randy.halt()
		self.set_refresh_request(False)

	def get_refresh_request(self):
		return self.__refresh_request

	def set_refresh_request(self, value):
		VALIDATE_TYPE(value, bool)
		self.__refresh_request = value

##############################################################################
### GUI ###
###########
class GUI(ttk.Frame):
	'''The GUI class'''

# --- DEFAULTS --- #
	__CELLWIDTH_RANGE = (10, 100)
	__CELLHEIGHT_RANGE = (10, 100)

	__DEFAULT_CONFIGURATION = {
		'cellwidth': 50,
		'cellheight': 50,
		'backtrack': True,  # undo
		'mark': True,
		'timer': True,
		'randy': True
	}
	# TODO: Define defaults for the Game object as well? (full control)

# --- GAME STYLE DEFAULTS --- #
	# TODO: Remove the DEFAULT_ prefix?
	__DEFAULT_CELL_STYLE_ARGS = dict(
		outline='black',
		cascadeoutline='lightgray',
		cascadeshape='rectangle',
		mark=None)

	__DEFAULT_WELCOME_CELL_STYLE_ARGS = dict(
		outline='black',
		cascadeoutline='indigo',
		cascadeshape='oval',
		mark=None)

	__DEFAULT_DOOR_STYLE_ARGS = dict(
		outline = 'black',
		# frontfill = 'sienna',
		frontfill = None,  # for random door colors
		windowfill = 'white',
		handlefill = 'white')

	__DEFAULT_EXIT_DOOR_STYLE_ARGS = dict(
		outline = 'black',
		frontfill = 'gold',
		windowfill = 'goldenrod',
		handlefill = 'goldenrod')

	__DEFAULT_ROOM_STYLE_ARGS = dict(outline = 'black', background = 'aliceblue')

	__DEFAULT_PLAYER_STYLE_ARGS = dict(
		# scale=0.5, outline='black', fill='gold')
		scale=0.5, outline='black', fill=('gold', 'goldenrod'))

	__DEFAULT_RANDY_STYLE_ARGS = dict(
		# scale=0.5, outline='black', fill='olive')
		scale=0.5, outline='black', fill=('olive', 'royalblue'))

	__DEFAULT_MARKER_COLOR = 'lime'

# --- WIDGET CONSTANTS --- #
	__MAIN_FRAME_BG = '#3399ff'#'royalblue'

	__HEADER_TEXT = 'The RAD Game'
	__HEADER_FRAME_BG = 'saddlebrown'
	__HEADER_LABEL_BG = 'honeydew'
	__HEADER_TEXT_FG = 'black'

	__PANEL_FRAME_BG = 'saddlebrown'
	__PANEL_TEXT_FG = 'indigo'

	__GAME_FRAME_BG = 'saddlebrown'
	__GAME_CANVAS_BG = '#f0f0f0'  # (240, 240, 240)

	__TIMER_START_TIME = 60  # in seconds
	__TIMER_ALERT_TIME = 5  # in seconds
	__TIMER_FRAME_BG = 'saddlebrown'
	__TIMER_LABEL_BG = 'black'
	__TIMER_COUNT_FG = 'lime'
	__TIMER_ALERT_FG = 'red'
	__TIMER_IDLE_FG = 'gray'

	__RANDY_DELAY = 400  # in milliseconds

	__QUOTE_WIDTH = 400
	__QUOTE_HEIGHT = 300
	__QUOTE_BG = 'white'
	__QUOTE_TEXT_WIDTH = 380
	__QUOTE_TEXT_FILL = 'black'

	__ANNOUNCEMENT_WIDTH = 400
	__ANNOUNCEMENT_HEIGHT = 100
	__ANNOUNCEMENT_BG = __HEADER_LABEL_BG
	__ANNOUNCEMENT_TEXT_WIDTH = 380
	__ANNOUNCEMENT_TEXT_FILL = 'black'

# --- CONFIGURATION --- #
	def __init__(self, master, **kwargs):
		# master
		if not isinstance(master, (tk.Tk, tk.Frame, ttk.Frame)):
			raise TypeError('master should be a Tk or a Frame object')
		super().__init__(master=master)
		self.__master = master

		# game
		self.__game = Game()

		if isinstance(master, tk.Tk):
			# configure root Tk object
			master.title(f"{self.__game.get_numrooms()} Rooms")
			master.resizable(False, False)

		# configuration and defaults values
		self.__parse_arguments(**kwargs)

		self.__create_widgets()
		self.__bind_events()
		self.__game_focus_set()

		# timer and randy
		cfgn = self.__get_configuration()
		if cfgn['timer']:
			self.__timer = None
		if cfgn['randy']:
			self.__guirandys = []
			for randy in self.__get_game().get_randys():
				self.__guirandys.append(GUIRandy(randy))

		# layout and display
		self.__set_layout()
		self.__displayer = None

	def __parse_arguments(self, **kwargs):
		# default values
		self.__configuration = GUI.__DEFAULT_CONFIGURATION.copy()

		# parsing user arguments
		for key, value in kwargs.items():
			if key == 'cellwidth':
				VALIDATE_TYPE_INRANGE(value, int, GUI.__CELLWIDTH_RANGE)
			if key == 'cellheight':
				VALIDATE_TYPE_INRANGE(value, int, GUI.__CELLHEIGHT_RANGE)
			if key in ('backtrack', 'mark', 'timer', 'randy'):
				VALIDATE_TYPE(value, bool)
			else:
				raise KeyError(f"invalid keyword argument '{key}'")
			self.__configuration[key] = value

		# dependency
		rows, columns = self.__get_game().get_dimensions()
		self.__width = columns * self.__configuration['cellwidth']
		self.__height = rows * self.__configuration['cellheight']

# --- GETTERS --- #
	__get_master = lambda self: self.__master

	__get_game = lambda self: self.__game
	__get_game_state = lambda self: self.__get_game().get_state()

	__get_configuration = lambda self: self.__configuration

	__get_width = lambda self: self.__width
	__get_height = lambda self: self.__height

	__get_main_frame = lambda self: self.__main_frame
	__get_game_frame = lambda self: self.__game_frame
	__get_game_canvas = lambda self: self.__game_canvas
	__get_timer_label = lambda self: self.__timer_label

	__get_layout_extractor = lambda self: self.__layout_extractor
	# __get_displayer = lambda self: self.__displayer

	__get_guirandys = lambda self: self.__guirandys

# --- PRSQ --- #
	def __play(self):
		if self.__get_game().play():
			self.__set()
			self.__refresh()

	def __reset(self):
		if self.__get_game_state() == Game.State.PLAYING:
			self.__stop()
		self.__play()

	def __stop(self):
		if self.__get_game().stop():
			self.__unset()
			self.__refresh()

	def __quit(self):
		self.__get_game().quit()
		# TODO: Implement a destory function? Should we call it here?
		# TODO: Implement a forget function? When to call it?
		master = self.__get_master()
		if isinstance(master, tk.Tk):
			master.quit()
		else:
			master.forget()

	# TODO: Merge button command callbacks into one method.
	def __play_btn(self):
		self.__play()
		self.__game_focus_set()

	def __reset_btn(self):
		self.__reset()
		self.__game_focus_set()

	def __stop_btn(self):
		self.__stop()
		self.__game_focus_set()

	def __quit_btn(self):
		self.__quit()
		self.__game_focus_set()

	def __exit(self):
		self.__quit()  # TODO: Keep this method?

# --- PLAYER --- #
	def __player_move(self, event):
		if self.__get_game_state() != Game.State.PLAYING: return

		if event.keysym == 'Left':
			direction = Direction.LEFT
		elif event.keysym == 'Right':
			direction = Direction.RIGHT
		elif event.keysym == 'Up':
			direction = Direction.UP
		elif event.keysym == 'Down':
			direction = Direction.DOWN
		else:
			assert False  # sanity check

		self.__get_game().player_move(direction)
		self.__refresh()

	def __player_inspect(self):
		if self.__get_game_state() != Game.State.PLAYING: return

		self.__get_game().player_inspect()
		if self.__get_game_state() == Game.State.TRIUMPH:
			self.__stop()
			self.__player_won()
		else:
			self.__refresh()

	def __player_undo(self):
		if self.__get_game_state() != Game.State.PLAYING: return

		self.__get_game().player_undo()
		self.__refresh()

	def __player_toggle_mark(self):
		if self.__get_game_state() != Game.State.PLAYING: return

		if self.__get_game().player_toggle_mark():
			self.__refresh()

	def __player_won(self):
		self.__reward_player()

	def __reward_player(self):
		self.__display_random_quote()

# --- SETTING --- #
	def __set(self):
		self.__set_display()
		cfgn = self.__get_configuration()
		if cfgn['timer']:
			self.__timer_set()		
		if cfgn['randy']:
			self.__randy_start()

	def __unset(self):
			cfgn = self.__get_configuration()
			if cfgn['randy']:
					self.__randy_stop()
			if cfgn['timer']:
					self.__timer_stop()
			self.__get_layout_extractor().clear()
			self.__displayer = None

# --- TIMER --- #
	def __timer_set(self):
		self.__timer = timedelta(seconds=GUI.__TIMER_START_TIME)
		timer_label = self.__get_timer_label()  # TODO: pass events to containing frame
		timer_label.configure(text=str(self.__timer)[2:],
							  foreground=GUI.__TIMER_COUNT_FG)
		self.__timer_job = timer_label.after(1000, self.__timer_callback)
	
	def __timer_stop(self):
		timer_label = self.__get_timer_label()
		timer_label.after_cancel(self.__timer_job)

		timer_label.configure(text='00:00',
							  foreground=GUI.__TIMER_IDLE_FG)
		self.__timer = None
	
	def __timer_callback(self):
		if not self.__timer: return  # TODO: Is it realy needed?
		self.__timer -= timedelta(seconds=1)

		timer_label = self.__get_timer_label()
		timer_label.configure(text = str(self.__timer)[2:])
		if self.__timer == timedelta(seconds=0):  # or simply timedelta()
			print("Time's Up!")
			self.__stop() # TODO: What is the correct state to be in when announcing?
			self.__time_is_up()
		else:
			if self.__timer <= timedelta(seconds=GUI.__TIMER_ALERT_TIME):
				timer_label.configure(foreground=GUI.__TIMER_ALERT_FG)
			self.__timer_job = timer_label.after(1000, self.__timer_callback)

	def __time_is_up(self):
		self.__announce("Time's Up!")

# --- RANDY --- #
	def __randy_start(self):
		game_frame = self.__get_game_frame()
		for guirandy in self.__get_guirandys():
			guirandy.start(game_frame, GUI.__RANDY_DELAY,
						   self.__randy_refresh_callback)
			# TODO: Should the GUI be responsible for creating Randys and
			# placing them in the maze?
			# self.game.get_network().accept(randy)

	def __randy_stop(self):
		for guirandy in self.__get_guirandys():
			guirandy.halt()

	# TODO: What exactly is the purpose of this callback?
	def __randy_refresh_callback(self, guirandy):
		player_room = self.__get_game().get_player().get_room()
		if guirandy.randy.get_room() == player_room:
			self.__refresh()
		elif guirandy.get_refresh_request():
			guirandy.set_refresh_request(False)
			if guirandy.randy.get_prev_room() == player_room:
				self.__refresh()
		
		# check if randy is done
		if guirandy.randy.get_state() == Randy.State.DONE:
			print("Randy is done :()")
			self.__stop()
			self.__randy_is_done()

	def __randy_is_done(self):
		self.__announce("Randy is done :()")

# --- LAYOUT --- #
	def __set_layout(self):
		game = self.__get_game()

		self.__layout_extractor = \
			LayoutExtractor(game,
							get_door_style=self.__get_door_style(),
							get_cell_style=self.__get_cell_style(),
							get_room_style=self.__get_room_style(),
							get_walker_style=self.__get_walker_style())

	def __get_door_style(self):
		styled = dict()
		def get_door_style(door):
			if not door in styled:  # TODO: Door IDs? (see walker styles)
				if isinstance(door, ExitDoor):
					style_args = GUI.__DEFAULT_EXIT_DOOR_STYLE_ARGS
				else:
					assert isinstance(door, Door)  # sanity check
					style_args = GUI.__DEFAULT_DOOR_STYLE_ARGS.copy() 
					if not style_args['frontfill']:
						style_args['frontfill'] = GET_RANDOM_COLOR()
				styled[door] = DoorStyle(**style_args)
			return styled[door]
		return get_door_style

	def __get_cell_style(self):
		def get_cell_style(cell):
			if isinstance(cell, WelcomeCell):
				style_args = GUI.__DEFAULT_WELCOME_CELL_STYLE_ARGS.copy()
			else:
				assert isinstance(cell, Cell)  # sanity check
				style_args = GUI.__DEFAULT_CELL_STYLE_ARGS.copy()
			if cell.is_marked():
				style_args['mark'] = GUI.__DEFAULT_MARKER_COLOR
			return CellStyle(**style_args)
		return get_cell_style

	def __get_room_style(self):
		room_style = RoomStyle(**GUI.__DEFAULT_ROOM_STYLE_ARGS)
		def get_room_style(room):
			# NOTE: Constant room style for now...
			return room_style
		return get_room_style

	def __get_walker_style(self):
		styled = dict()
		def get_walker_style(walker):
			walker_id = walker.get_id()
			if not walker_id in styled:
				if isinstance(walker, Player):
					style_args = GUI.__DEFAULT_PLAYER_STYLE_ARGS
				else:
					assert isinstance(walker, Randy)  # sanity check
					if not self.__get_configuration()['randy']: return None
					style_args = GUI.__DEFAULT_RANDY_STYLE_ARGS.copy()
					if self.__get_game().get_numrandys() > 1:
						# more than 1 randy => random colors
						# fill = (GET_RANDOM_COLOR(), GET_RANDOM_COLOR())
						# fill = ('style_args['fill'][0]', GET_RANDOM_COLOR())
						fill = (GET_RANDOM_COLOR(), None)
						style_args['fill'] = fill
				styled[walker_id] = WalkerStyle(**style_args)
			return styled[walker_id]
		return get_walker_style

# --- DISPLAY --- #
	def __set_display(self):
		game_canvas = self.__get_game_canvas()

		# canvas
		game_canvas.configure(width=self.__width, height=self.__height,
							  bg=GUI.__GAME_CANVAS_BG)

		# displayer
		bbox = BoundingBox(0, 0, self.__get_width(), self.__get_height())
		cfgn = self.__get_configuration()
		cellwidth, cellheight = cfgn['cellwidth'], cfgn['cellheight']
		self.__displayer = Displayer(game_canvas, bbox, cellwidth, cellheight)

	def __refresh(self):
		self.__clear_display()
		self.__display()

	def __clear_display(self):
		self.__get_game_canvas().delete('all')  # clear canvas contents

	def __display(self):  # TODO: Draw outline? grid?
		# (re-)configure canvas  # TODO: Move to a method.
		# game_canvas = self.__get_game_canvas()
		# game_canvas.configure(width=self.__width, height=self.__height,
		# 					  bg=GUI.__GAME_CANVAS_BG)

		if self.__get_game_state() != Game.State.PLAYING: return
		# TODO: Display something nice during game idle (quit?) state.	

		layout = self.__layout_extractor.extract()
		self.__displayer.display(layout)

	def __display_random_quote(self):
		author, text = GET_RANDOM_QUOTE()

		# EM DASH: U+2014 —
		# HORIZONTAL BAR: U+2015 ―
		author = '\u2015 ' + author

		# text = '"' + text + '"' 
		# LEFT DOUBLE QUOTATION MARK: U+201C “
		# RIGHT DOUBLE QUOTATION MARK: U+201D ”
		text = '\u201c' + text + '\u201d'

		quote = text + '\n\n    ' + author

		self.__clear_display()
		game_canvas = self.__get_game_canvas()
		game_canvas.configure(width=GUI.__QUOTE_WIDTH,
							  height=GUI.__QUOTE_HEIGHT,
							  bg=GUI.__QUOTE_BG)
		game_canvas.create_text(15, 15, text=quote, anchor='nw',
								width=GUI.__QUOTE_TEXT_WIDTH,
								fill=GUI.__QUOTE_TEXT_FILL,
								font=('Times', 17, 'italic bold'))

	def __announce(self, message):  # TODO: Merge with __display_random_quote?
		self.__clear_display()
		game_canvas = self.__get_game_canvas()
		game_canvas.configure(width=GUI.__ANNOUNCEMENT_WIDTH,
							  height=GUI.__ANNOUNCEMENT_HEIGHT,
							  bg=GUI.__ANNOUNCEMENT_BG)
		game_canvas.create_text(25, 25, text=message, anchor='nw',
								width=GUI.__ANNOUNCEMENT_TEXT_WIDTH,
								fill=GUI.__ANNOUNCEMENT_TEXT_FILL,
								font=('Calibri', 30, 'bold'))

# --- EVENTS --- #
	def __game_focus_set(self):
		self.__get_game_frame().focus_set()

	def __bind_events(self):
		# master events TODO: What is this?
		# master = self.__get_master()
		# master.bind('<Control-c>', lambda e: self.__exit())
		game_frame = self.__get_game_frame()

		# gui events
		game_frame.bind('<Escape>', lambda e: self.__exit())

		# game events
		for key in ('<Left>', '<Right>', '<Up>', '<Down>'):
			game_frame.bind(key, lambda e: self.__player_move(e))
		game_frame.bind('<Return>', lambda e: self.__player_inspect())
		if self.__get_configuration()['backtrack']:
			game_frame.bind('<BackSpace>', lambda e: self.__player_undo())
		if self.__get_configuration()['mark']:
			game_frame.bind('<space>', lambda e: self.__player_toggle_mark())

		# keyboard shortcuts
		game_frame.bind('p', lambda e: self.__play())
		game_frame.bind('r', lambda e: self.__reset())
		game_frame.bind('s', lambda e: self.__stop())
		game_frame.bind('q', lambda e: self.__quit())

		# TODO: key to pause game (space?)

# --- WIDGETS --- #
	def __create_widgets(self):
		# styles
		self.__configure_styles()
		
		# main frame
		master = self.__get_master()
		self.__create_main(master)
		
		# haader, panel, timer, game window
		main_frame = self.__get_main_frame()
		self.__create_header(main_frame)
		self.__create_panel(main_frame)
		if self.__get_configuration()['timer']:
			self.__create_timer(main_frame)
		self.__create_game_window(main_frame)

	def __configure_styles(self):
		self.__style = ttk.Style()

		# TODO: What is this?
		# # main
		# mainbg = self.___get_config()['bg']
		# self.__style.configure('Main.TFrame', background=mainbg,
		# 					   highlightbackground='brown', highlightthickness=1)
		
		# header
		self.__style.configure('Header.TFrame',
							   background = GUI.__HEADER_FRAME_BG)
		self.__style.configure('Header.TLabel',
							   background = GUI.__HEADER_LABEL_BG,
							   foreground = GUI.__HEADER_TEXT_FG,
							   font = ('Algerian', 24, 'bold'))

		# panel
		self.__style.configure('Panel.TFrame',
							   background = GUI.__PANEL_FRAME_BG)
		self.__style.configure('Panel.TButton',
							   foreground = GUI.__PANEL_TEXT_FG,
							   font = ('Arial', 14, 'bold'), width=8)

		# timer
		self.__style.configure('Timer.TFrame',
							   background = GUI.__TIMER_FRAME_BG)
		self.__style.configure('Timer.TLabel',
							   background=GUI.__TIMER_LABEL_BG,
							   font=('Arial', 14, 'bold'))

		# game
		self.__style.configure('Game.TFrame',
							   background = GUI.__GAME_FRAME_BG)


	def __create_main(self, master):
		# main frame (not themed) # TODO: What is this?
		# self.__main_frame = ttk.Frame(master, style='Main.TFrame')
		cfgn = self.__get_configuration()
		self.__main_frame = tk.Frame(master,
									 bg = GUI.__MAIN_FRAME_BG,
									 relief='ridge', bd=5)
		self.__main_frame.pack(padx=5, pady=5)

	def __create_header(self, master):
		# header frame
		self.__header_frame = ttk.Frame(master, style='Header.TFrame')
		self.__header_frame.pack(padx=5, pady=5)

		# header label
		self.__header_label = ttk.Label(self.__header_frame,
										style = 'Header.TLabel',
										text = self.__HEADER_TEXT,
										anchor = 'center')
		self.__header_label.pack(padx=5, pady=5, ipadx=15)

	def __create_panel(self, master):
		# panel frame
		self.__panel_frame = ttk.Frame(master, style='Panel.TFrame',
									   cursor='hand2')
		self.__panel_frame.pack(padx=5, pady=5)

		# button play
		self.__button_play = ttk.Button(self.__panel_frame,
										style='Panel.TButton', text='Play',
										command=lambda: self.__play_btn())
		self.__button_play.pack(padx=5, pady=5, side='left')

		# button reset
		self.__button_reset = ttk.Button(self.__panel_frame,
										 style='Panel.TButton', text='Reset',
										 command=lambda: self.__reset_btn())
		self.__button_reset.pack(padx=5, pady=5, side='left')

		# button stop
		self.__button_stop = ttk.Button(self.__panel_frame,
										style='Panel.TButton', text='Stop',
										command=lambda: self.__stop_btn())
		self.__button_stop.pack(padx=5, pady=5, side='left')

		# button exit
		self.__button_exit = ttk.Button(self.__panel_frame,
										style='Panel.TButton', text='Quit',
										command=lambda: self.__quit_btn())
		self.__button_exit.pack(padx=5, pady=5, side='left')

	def __create_timer(self, master):
		# timer frame
		self.__timer_frame = ttk.Frame(master, style='Timer.TFrame')
		self.__timer_frame.pack(padx=5, pady=5)

		# timer label
		self.__timer_label = ttk.Label(self.__timer_frame, 
									   style='Timer.TLabel', width=5,
									   foreground=GUI.__TIMER_IDLE_FG,
									   anchor='center', text='00:00')
		self.__timer_label.grid(padx=5, pady=5)

	def __create_game_window(self, master):
		# game frame
		self.__game_frame = ttk.Frame(master, style='Game.TFrame')
		self.__game_frame.pack(padx=5, pady=5)

		# game canvas
		self.__game_canvas = tk.Canvas(self.__game_frame,
									   bg = GUI.__GAME_CANVAS_BG,
									   width = self.__get_width(),
									   height = self.__get_height(),
									   bd=0, highlightthickness=0)
		self.__game_canvas.grid(padx=5, pady=5)


##############################################################################
### RADGame ###
###############
class RADGame:
	'''The RADGame class'''

	def __init__(self, **gui_kwargs):
		root = tk.Tk()
		GUI(root, **gui_kwargs)
		root.mainloop()


##############################################################################
### main ###
############

def main():
	RADGame()

if __name__ == '__main__': main()
