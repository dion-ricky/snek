#!/usr/bin/env python3

import pygame, random, sys
from pygame.locals import *

FPS = 30
FPSCLOCK = pygame.time.Clock()

BGCOLOR = (255, 255, 255)
BOXCOLOR = (0, 0, 0)
APPLECOLOR = (255, 0, 0)

BOXMOVE = 20
BOXBORDER = 5

WINDOWWIDTH = 500 + BOXBORDER
WINDOWHEIGHT = 500 + BOXBORDER

DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

pygame.display.set_caption('SNAKE')

def main():
    pygame.init()
    snake_obj = Snake()
    pygame.time.set_timer(USEREVENT, 200)
    FONT = pygame.font.Font('RobotoMono-Regular.ttf', 18)
    GAMEOVER = FONT.render('GAME OVER', True, BOXCOLOR)
    RESTART = FONT.render('PRESS SPACE TO RESTART', True, BGCOLOR, BOXCOLOR)

    while True:
        SCORE = FONT.render('SCORE '+str(snake_obj.score), True, BOXCOLOR)
        DISPLAYSURF.fill(BGCOLOR)
        DISPLAYSURF.blit(SCORE, (5,480))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit
            elif event.type == KEYDOWN and event.key == K_UP:
                snake_obj.change_direction('U')
            elif event.type == KEYDOWN and event.key == K_DOWN:
                snake_obj.change_direction('D')
            elif event.type == KEYDOWN and event.key == K_LEFT:
                snake_obj.change_direction('L')
            elif event.type == KEYDOWN and event.key == K_RIGHT:
                snake_obj.change_direction('R')
            elif event.type == KEYDOWN and event.key == K_SPACE:
                snake_obj = Snake()
                pygame.time.set_timer(USEREVENT, 200)
            elif event.type == USEREVENT:
                snake_obj.move_snake()

        if snake_obj.game_over:
            pygame.time.set_timer(USEREVENT, 0)
            DISPLAYSURF.blit(GAMEOVER, (400,480))
            DISPLAYSURF.blit(RESTART, (125,5))

        for rect in snake_obj.snakes:
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, rect)

        pygame.draw.rect(DISPLAYSURF, APPLECOLOR, snake_obj.spawn_apple())

        pygame.display.update()
        FPSCLOCK.tick(FPS)

class Snake():
    def __init__(self):
        self.apple = self.spawn_apple
        self.snakes = Snake.generate_snake()
        self.direction = 'R'
        self.last_direction = 'L'
        self.moved = False
        self.game_over = False
        self.is_apple_eaten = True
        self.score = 0

    def change_direction(self, direction):
        if Snake.is_inverse(self.direction, direction):
            return
        if self.direction == direction:
            return
        if not self.moved:
            return

        self.last_direction = self.direction
        self.direction = direction
        self.moved = False

    def change_speed(self):
        if self.score % 5 == 0:
            pygame.time.set_timer(USEREVENT, 200 - (10 * self.score // 5))

    def move_snake(self):
        direction = self.direction

        if self.game_over:
            return

        temp = self.move(self.snakes[-1], direction)

        if self.is_snake_colliding(temp):
            self.game_over = True
            return

        if self.is_snake_eating_apple(temp):
            self.score += 1
            self.is_apple_eaten = True
            self.snakes.insert(0, self.move(self.snakes[0], Snake.get_inverse(self.last_direction)))
            self.change_speed()

        self.snakes.append(self.move(self.snakes[-1], direction))
        self.snakes = self.snakes[1:]
        self.moved = True

    def move(self, rect, direction):
        x = 0
        y = 0
        if direction == 'L' or direction == 'R':
            x = BOXMOVE * (-1 if direction == 'L' else 1)
        elif direction == 'U' or direction == 'D':
            y = BOXMOVE * (-1 if direction == 'U' else 1)

        if rect.x + x > 500:
            x -= 500
        elif rect.x + x < 0:
            x += 500
        elif rect.y + y > 500:
            y -= 500
        elif rect.y + y < 0:
            y += 500

        return rect.move(x,y)

    def spawn_apple(self):
        if not self.is_apple_eaten:
            return self.apple

        self.is_apple_eaten = False

        random_x = 5 + random.randint(0,24)*20
        random_y = 5 + random.randint(0,24)*20

        while [random_x, random_y] in self.get_snake_xy():
            random_x = 5 + random.randint(0,24)*20
            random_y = 5 + random.randint(0,24)*20

        self.apple = Rect( random_x, random_y, 15, 15 )

        return self.apple

    def is_snake_eating_apple(self, rect):
        if rect.collidelistall([self.apple]) == []:
            return False

        return True

    def is_snake_colliding(self, rect):
        if rect.collidelistall(self.snakes) == []:
            return False

        return True

    def get_snake_xy(self):
        return [[rect.x, rect.y] for rect in self.snakes]

    def generate_snake():
        snake = []
        for i in range(4):
            snake.append(Rect( (5 + i*20), 5, 15, 15 ))

        return snake

    def get_inverse(direction):
        data = {'L': 'R', 'R':'L', 'U':'D', 'D':'U'}
        return data[direction]

    def is_inverse(direction, new_direction):
        data = {'L': 'R', 'R':'L', 'U':'D', 'D':'U'}
        return data[direction] == new_direction

if __name__ == '__main__':
    main()
