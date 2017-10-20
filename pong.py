import math
import time
import random
import pygame as pg
from utils import Vector2, DIRECTION, Timer


class Paddle:

    UP = -1
    STAND = 0
    DOWN = 1

    def __init__(self, x, y, width, height, min_y, max_y, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_y = max_y - height
        self.min_y = min_y
        self.speed = speed
        self.direction = Paddle.STAND

    def update(self, dt):
        dy = self.speed * self.direction * dt
        self.y = max(min(self.max_y, self.y + dy), self.min_y)

    def add_direction(self, dir):
        self.direction += dir

    def center_y(self):
        return self.y + self.height // 2

    @property
    def pos(self):
        return self.x, self.y

    @property
    def rect(self):
        return pg.Rect(self.pos, (self.width, self.height))

    @property
    def top(self):
        return self.y

    @property
    def bottom(self):
        return self.y + self.height


class AIPaddle(Paddle):

    def __init__(self, ball, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ball = ball

    def update(self, dt):
        if self.center_y() < self.ball.y:
            self.direction = self.DOWN
        else:
            self.direction = self.UP
        super().update(dt)


class Ball:

    def __init__(self, pos, radius, speed, direction, min_y, max_y, colliders):
        self.pos = pos
        self.radius = radius
        self.speed = speed
        self.direction = direction
        self.min_y = min_y
        self.max_y = max_y - self.rect.height
        self.colliders = colliders

    def update(self, dt):
        dx, dy = self.speed * self.direction * dt
        test_rect = self.rect
        test_rect.x += dx
        test_rect.y += dy
        if test_rect.y <= self.min_y + 2*self.radius or test_rect.y >= self.max_y - 2*self.radius:
            self.direction = self.direction.deflect_y()
        else:
            collide_idx = test_rect.collidelist(self.colliders)
            if collide_idx != -1:
                collide_with = self.colliders[collide_idx]
                if self.top >= collide_with.bottom or self.bottom <= collide_with.top:
                    dy = -dy
                    self.direction = self.direction.deflect_y()
                else:
                    dx = -dx
                    self.direction = self.direction.deflect_x()
        self.pos += Vector2(dx, dy)
        if self.bottom > 900 or self.top < 0:
            print(locals())

    def add_collideable(self, collable):
        self.colliders.append(collable)

    def change_speed(self, amount):
        self.speed += amount

    def dir_x(self):
        return self.direction[0]

    def dir_y(self):
        return self.direction[1]

    def jump_to(self, pos):
        self.pos = pos

    @property
    def rect(self):
        return pg.Rect(self.pos - Vector2(self.radius, self.radius), (self.radius * 2, self.radius * 2))

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    @property
    def top(self):
        return self.y - self.radius

    @property
    def bottom(self):
        return self.y + self.radius


class PongDrawer:

    def __init__(self, bg_color, paddle_color, ball_color, game):
        self.bg_color = bg_color
        self.paddle_color = paddle_color
        self.ball_color = ball_color
        self.screen = game.screen
        self.game = game

    def fill_screen(self, rects):
        for rect in rects:
            self.screen.fill(self.bg_color, rect)

    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def __call__(self):
        self.screen.fill(self.bg_color)
        for paddle in [self.game.player, self.game.enemy]:
            pg.draw.rect(
                self.screen,
                self.paddle_color,
                paddle.rect
            )
            pg.draw.rect(
                self.screen,
                pg.Color('black'),
                paddle.rect,
                1
            )
        pg.draw.circle(
            self.screen,
            self.ball_color,
            math.floor(self.game.ball.pos),
            self.game.ball.radius
        )


class PongGame:

    FPS = 60
    SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = 1600, 900

    def __init__(self):
        self.screen = pg.display.set_mode(self.SCREEN_SIZE, pg.FULLSCREEN)
        paddle_width = self.SCREEN_WIDTH // 90
        paddle_height = self.SCREEN_HEIGHT // 3
        self.player = Paddle(
            x=10,
            y=self.SCREEN_HEIGHT // 2,
            width=paddle_width,
            height=paddle_height,
            min_y=0,
            max_y=self.SCREEN_HEIGHT,
            speed=400
        )
        self.ball = Ball(
            Vector2(
                self.SCREEN_WIDTH // 2,
                self.SCREEN_HEIGHT // 2
            ),
            radius=8,
            speed=820,
            direction=DIRECTION['LEFT_UP'],
            min_y=0,
            max_y=self.SCREEN_HEIGHT,
            colliders=[self.player],
        )
        self.enemy = AIPaddle(
            self.ball,
            x=self.SCREEN_WIDTH - (paddle_width + 10),
            y=self.SCREEN_HEIGHT // 2,
            width=paddle_width,
            height=paddle_height,
            min_y=0,
            max_y=self.SCREEN_HEIGHT,
            speed=380
        )
        self.ball.add_collideable(self.enemy)
        self.drawer = PongDrawer(
            pg.Color('gray34'),
            pg.Color('gray20'),
            pg.Color('floralwhite'),
            self
        )
        self.points = {'player': 0, 'enemy': 0}
        self.clock = pg.time.Clock()
        self.updateables = [
            self.player,
            self.enemy,
            self.ball,
            Timer(5, self.randomize_ball)
        ]
        self.dirty_rects = []

    def game_loop(self):
        self.drawer.draw_bg()
        pg.display.update()
        running = True
        while running:
            #dt = min(self.clock.tick(self.FPS) / 1000, 1/self.FPS + 0.002)
            self.clock.tick(self.FPS)
            dt = 1/self.FPS
            for ev in pg.event.get():
                if ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_ESCAPE:
                        running = False
                    elif ev.key == pg.K_w:
                        self.player.add_direction(Paddle.UP)
                    elif ev.key == pg.K_s:
                        self.player.add_direction(Paddle.DOWN)
                    elif ev.key == pg.K_SPACE:
                        print(vars(self.ball))
                if ev.type == pg.KEYUP:
                    if ev.key == pg.K_w:
                        self.player.add_direction(Paddle.DOWN)
                    elif ev.key == pg.K_s:
                        self.player.add_direction(Paddle.UP)
            self.update(dt)
            self.drawer()
            pg.display.update(self.dirty_rects)
            self.dirty_rects = []

    def update(self, dt):
        self.dirty_rects += [
            r.copy()
            for r in (
                self.player.rect,
                self.enemy.rect,
                self.ball.rect
            )
        ]
        for up in self.updateables:
            up.update(dt)
        self.check_for_points()
        self.dirty_rects += [
            self.player.rect,
            self.enemy.rect,
            self.ball.rect
        ]

    def check_for_points(self):
        if self.ball.x <= 0:
            self.points['player'] += 1
            self.reset_ball()
        elif self.ball.x >= self.SCREEN_WIDTH:
            self.points['enemy'] += 1
            self.reset_ball()

    def reset_ball(self):
        self.ball.jump_to(Vector2(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2))
        self.ball.direction = DIRECTION['NONE']
        self.updateables.append(
            Timer(1.5, lambda: setattr(self.ball, 'direction', DIRECTION['LEFT_UP']), once=True)
        )

    def randomize_ball(self):
        pi4 = math.pi / 4
        self.ball.direction = (
            self.ball.direction + Vector2(
                random.uniform(-pi4, pi4),
                random.uniform(-pi4, pi4)
            )
        ).normalize()
        self.ball.change_speed(random.randrange(20))


if __name__ == '__main__':
    pg.init()
    pg.mouse.set_visible(False)
    PongGame().game_loop()
