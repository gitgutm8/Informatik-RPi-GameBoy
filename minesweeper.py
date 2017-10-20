import random
from enum import Flag
import pygame as pg
from utils import Vector2


class CellState(Flag):
    EMPTY = 0
    MINED = 1
    FLAGGED = 2
    OPEN = 4
    OPEN_MINE = MINED | OPEN
    FLAGGED_MINE = MINED |FLAGGED


class MineSweeper:

    def __init__(self, columns, rows, mines):
        self.columns = columns
        self.rows = rows
        self.cells = [[CellState.EMPTY] * self.columns for _ in range(self.rows)]
        self.mines = mines
        self.cells_to_open = self.columns * self.rows - self.mines
        self.mines_left = self.mines
        self.alive = True
        self.first_click = True

    def _generate_mines(self, unavailable):
        cells = list(range(self.columns * self.rows))
        cells.remove(unavailable)
        for cell_num in random.choices(cells, k=self.mines):
            row, column = divmod(cell_num, self.columns)
            self.cells[row][column] = CellState.MINED

    def reveal_click(self, col, row):
        if self.first_click:
            self.first_click = False
            self._generate_mines(col * row)

        state = self[row][col]
        if state & CellState.FLAGGED == CellState.FLAGGED or state == CellState.OPEN:
            return
        self._open(col, row)

    def _open(self, col, row):
        self[row][col] |= CellState.OPEN
        if self[row][col] == CellState.MINED:
            self.alive = False
            return
        neighbors = self._get_neighbors(col, row)
        if not any(self[ny][nx] is CellState.MINED for nx, ny in neighbors):
            for neighbor in neighbors:
                self.reveal_click(*neighbor)

    def _get_neighbors(self, col, row):
        neighbors = [
            Vector2(delta) for delta in
            [
                (-1, -1), (-1, 0), (-1, 1),
                (0, -1),           (0, 1),
                (1, -1),  (1, 0),  (1, 1)
            ]
        ]
        output = []
        for neighbor in neighbors:
            x, y = neighbor + Vector2(col, row)
            if 0 <= x < self.columns and 0 <= y < self.rows:
                output.append((x, y))
        return output

    def flag_click(self, col, row):
        state = self[row][col]
        if state == CellState.OPEN:
            return
        self[row][col] ^= CellState.FLAGGED
        if state == CellState.MINED:
            self.mines_left -= 1
        elif self[row][col] == CellState.MINED:
            self.mines_left += 1

    def is_won(self):
        return self.mines_left == 0 or self.cells_to_open == 0

    def is_lost(self):
        return not self.alive

    def enumerate(self):
        for y in range(self.rows):
            for x in range(self.columns):
                yield Vector2(x, y), self[y][x]

    def __getitem__(self, item):
        return self.cells[item]


class MineSweeperDrawer:

    def __init__(self, state_to_color, grid_line_color, game):
        self.state_to_color = state_to_color
        self.grid_line_color = grid_line_color
        self.screen = game.screen
        self.game = game

    def _block(self, pos):
        return pg.Rect(pos * self.game.block_size, (self.game.block_size, self.game.block_size))

    def _draw_grid_lines(self):
        pass

    def __call__(self):
        for pos, state in self.game.board.enumerate():
            pg.draw.rect(
                self.screen,
                self.state_to_color[state],
                self._block(pos)
            )
        self._draw_grid_lines()


class _2dSelector:

    def __init__(self, init_pos, edges):
        self.pos = init_pos
        self.edges = edges

    def get(self):
        return self.pos

    def __iadd__(self, other):
        self.pos = (self.pos + other) % self.edges
        return self

    def __isub__(self, other):
        self.pos = (self.pos - other) % self.edges
        return self

class MineSweeperGame:

    FPS = 60
    SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900
    SCREEN_SIZE = Vector2(SCREEN_WIDTH, SCREEN_HEIGHT)

    def __init__(self, columns, rows, mines, block_size):
        self.screen = pg.display.set_mode(self.SCREEN_SIZE, pg.FULLSCREEN)
        self.clock = pg.time.Clock()

        self.drawer = MineSweeperDrawer(
            state_to_color={
                CellState.EMPTY: pg.Color('gray67'),
                CellState.MINED: pg.Color('gray67'),
                CellState.OPEN:  pg.Color('gray100'),
                CellState.FLAGGED: pg.Color('greenyellow'),
                CellState.FLAGGED_MINE: pg.Color('greenyellow'),
                CellState.OPEN_MINE: pg.Color('darkred')
            },
            grid_line_color=pg.Color('black'),
            game=self
        )
        self.block_size = block_size

        self.board = MineSweeper(columns, rows, mines)
        self.selected_mine = _2dSelector(Vector2(0, 0), Vector2(columns, rows))

    def game_loop(self):
        running = True
        while running:
            self.clock.tick(self.FPS)
            for ev in pg.event.get():
                if ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_w:
                        self.selected_mine += Vector2(0, -1)
                    elif ev.key == pg.K_a:
                        self.selected_mine += Vector2(-1, 0)
                    elif ev.key == pg.K_s:
                        self.selected_mine += Vector2(0, 1)
                    elif ev.key == pg.K_d:
                        self.selected_mine += Vector2(1, 0)
                    elif ev.key == pg.K_o:
                        self.board.reveal_click(*self.selected_mine.get())
                    elif ev.key == pg.K_p:
                        self.board.flag_click(*self.selected_mine.get())
                    elif ev.key == pg.K_ESCAPE:
                        running = False
            self.drawer()
            pg.display.update()

if __name__ == '__main__':
    MineSweeperGame(10, 10, 16, 30).game_loop()
