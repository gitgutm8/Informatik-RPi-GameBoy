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
        self.hints = [[0] * self.columns for _ in range(self.rows)]
        cells = list(range(self.columns * self.rows))
        cells.remove(unavailable)
        for cell_num in random.choices(cells, k=self.mines):
            row, column = divmod(cell_num, self.columns)
            self.cells[row][column] = CellState.MINED
            for x, y in self._get_neighbors(column, row):
                self.hints[y][x] += 1

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
        if self[row][col] == CellState.OPEN_MINE:
            self.alive = False
            return
        if self.get_hint((col, row)) == 0:
            for neighbor in self._get_neighbors(col, row):
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
        if state & CellState.OPEN == CellState.OPEN:
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

    def get_hint(self, pos):
        x, y = pos
        return self.hints[y][x]

    def enumerate(self):
        for y in range(self.rows):
            for x in range(self.columns):
                yield Vector2(x, y), self[y][x]

    def __getitem__(self, item):
        return self.cells[item]


class MineSweeperDrawer:

    def __init__(self, state_to_color, grid_line_color, crosshair_color, font, num_colors, game):
        self.state_to_color = state_to_color
        self.grid_line_color = grid_line_color
        self.crosshair_color = crosshair_color
        self.screen = game.screen
        self.game = game
        self.hint_surfaces = [font.render(str(num), 1, color)
                              for num, color
                              in zip(range(1, 10), num_colors)]

    def _block(self, pos):
        return pg.Rect(pos * self.game.block_size, (self.game.block_size, self.game.block_size))

    def _draw_cells(self):
        for pos, state in self.game.board.enumerate():
            pg.draw.rect(
                self.screen,
                self.state_to_color[state],
                self._block(pos)
            )
            if state == CellState.OPEN:
                self._draw_hint(pos)

    def _draw_hint(self, pos):
        hint = self.game.board.get_hint(pos)
        if hint == 0: return
        surf = self.hint_surfaces[hint-1]
        self.screen.blit(surf, pos * self.game.block_size)

    def _draw_grid_lines(self):
        for i in range(self.game.board.columns):
            start = i * self.game.block_size, 0
            end = i * self.game.block_size, self.game.board.rows * self.game.block_size
            pg.draw.line(self.screen, self.grid_line_color, start, end)
        for i in range(self.game.board.rows):
            start = 0, i * self.game.block_size
            end = self.game.board.columns * self.game.block_size, i * self.game.block_size
            pg.draw.line(self.screen, self.grid_line_color, start, end)

    def _draw_crosshair(self):
        center = self.game.block_size * self.game.selected_mine.get() + Vector2([self.game.block_size] * 2) // 2
        pg.draw.circle(
            self.screen,
            self.crosshair_color,
            center,
            2
        )

    def __call__(self):
        self._draw_cells()
        self._draw_grid_lines()
        self._draw_crosshair()


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

    FPS = 25
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
            crosshair_color=pg.Color('blue'),
            font=pg.font.SysFont('verdana.ttf', block_size),
            num_colors=[(  0,  65, 170),  # blue
                        ( 28, 122,   0),  # green
                        (183,  25,  25),  # red
                        (  3,  14,  76),  # blue
                        ( 76,   3,   3),  # darkred
                        ( 6, 111, 124),  # cyan
                        ( 10,  10,  10),  # black
                        (171, 186, 188)], # gray
            game=self
        )
        self.block_size = block_size

        self.board = MineSweeper(columns, rows, mines)
        self.selected_mine = _2dSelector(Vector2(0, 0), Vector2(columns, rows))

    def game_loop(self):
        self.drawer()
        pg.display.update()
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
    pg.init()
    MineSweeperGame(10, 10, 16, 80).game_loop()
