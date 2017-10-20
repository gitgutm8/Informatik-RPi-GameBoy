import random
import itertools
from functools import partialmethod
from collections import deque
import pygame as pg
#from buttons import *
from utils import DIRECTION, Vector2, Timer


class Snake:

    def __init__(self, start_pos, edges, growth_per_food):
        self.edges = edges
        self.direction = DIRECTION['UP']
        self.parts = deque([start_pos + self.direction, start_pos, start_pos - self.direction])
        self.growth_per_food = growth_per_food
        self.growth_left = 0
        self.alive = True

    def move(self):
        if not self.alive:
            return
        new_head = (self.head + self.direction) % self.edges
        if new_head in self.body:
            self.alive = False
        else:
            self.add_head(new_head)
            if self.growth_left > 0:
                self.growth_left -= 1
            else:
                self.remove_tail()

    def grow(self):
        self.growth_left += self.growth_per_food

    def is_on_position(self, pos):
        return self.head == pos

    def change_direction(self, dir):
        if (self.head + dir) % self.edges != self.parts[1]:
            self.direction = dir

    look_up = partialmethod(change_direction, DIRECTION['UP'])
    look_down = partialmethod(change_direction, DIRECTION['DOWN'])
    look_left = partialmethod(change_direction, DIRECTION['LEFT'])
    look_right = partialmethod(change_direction, DIRECTION['RIGHT'])

    def add_head(self, head):
        self.parts.appendleft(head)

    def remove_tail(self):
        self.parts.pop()

    @property
    def head(self):
        return self.parts[0]

    @property
    def body(self):
        first = True
        for part in self.parts:
            if first:
                first = False
                continue
            yield part


class SnakeDrawer:

    def __init__(self, bg_color, snake_color, food_color, game):
        self.bg_color = bg_color
        self.snake_color = snake_color
        self.food_color = food_color
        self.game = game
        self.screen = game.screen

    def __call__(self):
        self.draw()

    def block(self, pos):
        return pg.Rect(
            pos * self.game.block_size,
            (self.game.block_size, self.game.block_size)
        )

    def draw_part(self, part):
        pg.draw.rect(
            self.screen,
            self.snake_color,
            self.block(part)
        )
        pg.draw.rect(
            self.screen,
            pg.Color('black'),
            self.block(part),
            1
        )

    def draw_food(self, pos):
        pg.draw.rect(
            self.screen,
            self.food_color,
            self.block(pos)
        )

    def draw(self):
        self.screen.fill(self.bg_color)
        for part in self.game.snake.parts:
            self.draw_part(part)
        self.draw_food(self.game.food_pos)


class SnakeGame:

    FPS = 60
    SCREEN_SIZE = Vector2(1600, 900)

    def __init__(self, block_size, snake_blocks_per_second):
        self.screen = pg.display.set_mode(self.SCREEN_SIZE, pg.FULLSCREEN)
        self.width, self.height = self.SCREEN_SIZE // block_size
        self.block_size = block_size
        self.drawer = SnakeDrawer(
            pg.Color('gray45'),
            pg.Color('chartreuse4'),
            pg.Color('brown3'),
            self
        )
        self.snake = Snake(
            start_pos=Vector2(
                self.height // 2,
                self.width // 2
            ),
            edges=Vector2(self.width, self.height),
            growth_per_food=1
        )
        self.snake_move_timer = Timer(
            interval=1/snake_blocks_per_second,
            callback=self.snake.move
        )
        self.score = 0
        self.food_pos = self.generate_food()
        self.clock = pg.time.Clock()

    def game_loop(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000
            for ev in pg.event.get():
                if ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_ESCAPE:
                        running = False
                    elif ev.key == pg.K_w:
                        self.snake.look_up()
                    elif ev.key == pg.K_a:
                        self.snake.look_left()
                    elif ev.key == pg.K_s:
                        self.snake.look_down()
                    elif ev.key == pg.K_d:
                        self.snake.look_right()
            self.update(dt)
            self.drawer()
            pg.display.update()

    def _game_loop(self):
        running = True
        while running:
            pg.event.pump()
            dt = self.clock.tick(self.FPS) / 1000
            for bp in get_button_presses():
                {
                    CROSS_UP: self.snake.look_up,
                    CROSS_DOWN: self.snake.look_down,
                    CROSS_LEFT: self.snake.look_left,
                    CROSS_RIGHT: self.snake.look_right
                }[bp]()

            self.update(dt)
            self.drawer()
            pg.display.update()

    def update(self, dt):
        self.snake_move_timer.update(dt)
        if self.snake.is_on_position(self.food_pos):
            self.snake.grow()
            self.food_pos = self.generate_food()
            self.score += 1

    def generate_food(self):
        while True:
            pos = Vector2(
                random.randrange(self.width),
                random.randrange(self.height)
            )
            if pos not in self.snake.body:
                return pos

    def pause(self):
        pass


if __name__ == '__main__':
    pg.init()
    pg.mouse.set_visible(False)
    SnakeGame(100, 6).game_loop()


