import curses
import time
import random

# Logging setup
LOG_FILE = "tetris_log.txt"


def clear_log():
	"""Clears the log file at the start of each game session."""
	with open(LOG_FILE, "w") as f:
		f.write("Tetris Screensaver Debug Log\n============================\n")


def log(message):
	"""Write log messages to the file."""
	with open(LOG_FILE, "a") as f:
		f.write(message + "\n")


# All 7 Tetris pieces
TETROMINOS = {
	'I': [[1, 1, 1, 1]],
	'O': [[1, 1], [1, 1]],
	'T': [[0, 1, 0], [1, 1, 1]],
	'L': [[0, 0, 1], [1, 1, 1]],
	'J': [[1, 0, 0], [1, 1, 1]],
	'S': [[0, 1, 1], [1, 1, 0]],
	'Z': [[1, 1, 0], [0, 1, 1]]
}

COLORS = {
	'I': curses.COLOR_CYAN,
	'O': curses.COLOR_YELLOW,
	'T': curses.COLOR_MAGENTA,
	'L': curses.COLOR_BLUE,
	'J': curses.COLOR_WHITE,
	'S': curses.COLOR_GREEN,
	'Z': curses.COLOR_RED
}

SPEED = 0.75  # Adjust speed for debugging


class TetrisScreensaver:
	def __init__(self, stdscr):
		self.stdscr = stdscr
		self.reset_game()

	def reset_game(self):
		"""Resets the game state and starts fresh."""
		curses.curs_set(0)
		self.max_y, self.max_x = self.stdscr.getmaxyx()
		self.board = [[0] * self.max_x for _ in range(self.max_y)]
		self.init_colors()
		clear_log()  # Clear the log on restart
		log("🔄 Restarting Game!")
		self.run()

	def init_colors(self):
		"""Initializes color pairs for rendering."""
		curses.start_color()
		for i, (key, color) in enumerate(COLORS.items(), start=1):
			curses.init_pair(i, color, curses.COLOR_BLACK)

	def draw_board(self):
		"""Redraws the board with colors and logs board state."""
		self.stdscr.clear()
		log("\nBoard State:")
		for y in range(self.max_y):
			row_str = ""
			for x in range(self.max_x):
				if self.board[y][x]:
					self.stdscr.addch(y, x, '#', curses.color_pair(self.board[y][x]))
					row_str += "#"
				else:
					row_str += "."
			log(row_str)
		self.stdscr.refresh()

	def can_fall(self, shape, y, x):
		"""Checks if any block in the bottom-most row of the piece has something directly below."""
		log(f"\nChecking if piece can fall from y={y}, x={x}")

		lowest_blocks = {}  # Keep track of the lowest block in each column
		for dy, row in enumerate(shape):
			for dx, cell in enumerate(row):
				if cell:
					col_x = x + dx
					lowest_blocks[col_x] = max(lowest_blocks.get(col_x, y + dy), y + dy)

		for col_x, block_y in lowest_blocks.items():
			new_y = block_y + 1
			if new_y >= self.max_y or (new_y >= 0 and self.board[new_y][col_x]):
				log(f"❌ Block at y={block_y}, x={col_x} has something below. Stopping fall.")
				return False

		log("✅ Piece can fall")
		return True

	def place_piece(self, shape, y, x, color):
		"""Locks a tetromino into the board and logs placement."""
		log(f"\nPlacing piece at y={y}, x={x}")
		for dy, row in enumerate(shape):
			for dx, cell in enumerate(row):
				if cell:
					self.board[y + dy][x + dx] = color  # Store color index

	def remove_piece(self, shape, y, x):
		"""Erases the tetromino from the board before moving."""
		log(f"\nRemoving piece from y={y}, x={x}")
		for dy, row in enumerate(shape):
			for dx, cell in enumerate(row):
				if cell and 0 <= y + dy < self.max_y and 0 <= x + dx < self.max_x:
					self.board[y + dy][x + dx] = 0

	def drop_tetrimino(self):
		"""Handles piece falling using per-block collision detection."""
		piece_key = random.choice(list(TETROMINOS.keys()))
		shape = TETROMINOS[piece_key]
		color = list(COLORS.keys()).index(piece_key) + 1  # Get color index

		x = random.randint(2, self.max_x - len(shape[0]) - 2)  # Randomized spawn position
		y = 0

		log(f"\n--- SPAWNED PIECE ({piece_key}) at x={x}, y={y} ---")

		# Ensure spawn is valid
		if not self.can_fall(shape, y, x):  # If it cannot even fall initially, stop spawning
			log("❌ PIECE CANNOT FALL FROM SPAWN! STACK FULL")
			return False  # Stop spawning if the board is full

		while True:
			log(f"\nAttempting to move piece from y={y} to y={y + 1}")
			if self.can_fall(shape, y, x):  # If any block in the piece can fall, move the whole thing down
				self.remove_piece(shape, y, x)  # Remove old position
				y += 1
				self.place_piece(shape, y, x, color)
				self.draw_board()
				time.sleep(SPEED)
			else:
				log(f"🔽 Piece ({piece_key}) landed at y={y}")
				break  # Piece has landed

		self.place_piece(shape, y, x, color)  # Lock the piece
		self.draw_board()  # Final render

		return True  # Indicate successful landing

	def run(self):
		"""Continuously spawns pieces until the board is full, then restarts."""
		while True:
			success = self.drop_tetrimino()

			if not success:
				log("🛑 STACKED TO THE TOP! RESTARTING GAME...")
				time.sleep(2)  # Pause before restarting
				self.reset_game()  # Restart the game
				return  # Prevent further execution after reset

			time.sleep(1)  # Short delay before next piece


if __name__ == "__main__":
	curses.wrapper(TetrisScreensaver)
