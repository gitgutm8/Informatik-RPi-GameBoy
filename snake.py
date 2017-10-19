import random
import itertools
from collections import deque
import pygame as pg
from utils import DIRECTION, Vector2, Timer, millis


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

    def add_head(self, head):
        self.parts.appendleft(head)

    def remove_tail(self):
        self.parts.pop()

    def grow(self):
        self.growth_left += self.growth_per_food

    def check_for_food(self, food_position):
        if self.head == food_position:
            self.grow()
            return True

    def change_direction(self, dir):
        if self.head + dir != self.parts[1]:
            self.direction = dir

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

    def block(self, pos):
        return pg.Rect(
            pos * self.game.block_size,
            (self.game.block_size, self.game.block_size)
        )

    def draw(self):
        self.screen.fill(self.bg_color)
        for part in self.game.snake.parts:
            pg.draw.rect(
                self.screen,
                self.snake_color,
                self.block(part)
            )
        pg.draw.rect(
            self.screen,
            self.food_color,
            self.block(self.game.food_pos)
        )


class SnakeGame:

    FPS = 60
    SCREEN_SIZE = Vector2(1600, 900)

    def __init__(self, block_size, snake_blocks_per_second):
        self.screen = pg.display.set_mode(self.SCREEN_SIZE, pg.FULLSCREEN)
        self.drawer = SnakeDrawer(
            pg.Color('gray45'),
            pg.Color('chartreuse4'),
            pg.Color('brown3'),
            self
        )
        self.width, self.height = self.SCREEN_SIZE // block_size
        self.block_size = block_size
        self.snake = Snake(
            start_pos=Vector2(
                self.height // 2,
                self.width // 2
            ),
            edges=Vector2(self.width, self.height),
            growth_per_food=15
        )
        self.snake_move_timer = Timer(
            interval=1/snake_blocks_per_second,
            callback=self.snake.move
        )
        self.score = 0
        self.food_pos = self.generate_food()
        self.clock = pg.time.Clock()
        self.game_loop()

    def game_loop(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000
            for ev in pg.event.get():
                if ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_ESCAPE:
                        running = False
                    elif ev.key == pg.K_w:
                        self.snake.change_direction(DIRECTION['UP'])
                    elif ev.key == pg.K_a:
                        self.snake.change_direction(DIRECTION['LEFT'])
                    elif ev.key == pg.K_s:
                        self.snake.change_direction(DIRECTION['DOWN'])
                    elif ev.key == pg.K_d:
                        self.snake.change_direction(DIRECTION['RIGHT'])
            self.snake_move_timer.update(dt)
            if self.snake.check_for_food(self.food_pos):
                self.food_pos = self.generate_food()
                self.score += 1
            self.drawer.draw()
            pg.display.update()

    def generate_food(self):
        pos = Vector2(
            random.randrange(self.width),
            random.randrange(self.height)
        )
        while pos in self.snake.body:
            pos = Vector2(
                random.randrange(self.width),
                random.randrange(self.height)
            )
        return pos


if __name__ == '__main__':
    pg.init()
    pg.mouse.set_visible(False)
    SnakeGame(50, 10)


