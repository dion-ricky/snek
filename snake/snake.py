import pygame, random, sys
from pygame.locals import *

class Snake():
    def __init__(self):
        self.snakes = Snake.generate_snake()
        self.direction = 'R'
        self.last_direction = 'L'
        self.moved = False
        self.game_over = False
        self.score = 0
        self.is_item_eaten = True
        self.known_item_type = ['apple', 'golden_apple', 'poison', 'speed']
        self.arbitrary_probability = [1, 1, 2, 1]
        self.item_type = 'apple'
        self.item = self.spawn_item()
        self.speed = 0
        self.interface = None
        self.item_effect = []

    def change_direction(self, direction):
        direction = Snake.get_inverse(direction) if self.is_poison_effect_applied() else direction

        if Snake.is_inverse(self.direction, direction):
            return
        if self.direction == direction:
            return
        if not self.moved:
            return

        self.last_direction = self.direction
        self.direction = direction
        self.moved = False

    def remove_effect(self, effect):
        self.item_effect.remove(effect)

        if effect.item_name == 'frenzy':
            self.speed = 10 * (self.score // 5)
            self.set_speed()

        if len(self.item_effect) == 0:
            pygame.time.set_timer(USEREVENT+2, 0)

    def item_effect_countdown(self):
        for i in self.item_effect:
            i.countdown()

    def change_speed(self, speed=None):
        old_speed = self.speed

        if not self.is_frenzy_effect_applied():
            if speed:
                self.speed = speed
            elif self.score % 5 == 0:
                self.speed = 10 * (self.score // 5)

        if self.item_type != 'apple':
            if self.item_type == 'speed':
                self.apply_frenzy_effect()

            elif self.item_type == 'poison':
                self.apply_poison_effect()

            pygame.time.set_timer(USEREVENT+2, 1000)

        if self.speed != old_speed:
            self.set_speed()

    def apply_poison_effect(self):
        existing_item_effect = self.is_poison_effect_applied()

        if existing_item_effect:
            existing_item_effect.add_time()
        else:
            self.item_effect.append(Item('poisoned', self))

    def is_poison_effect_applied(self):
        for i in self.item_effect:
            if i.item_name == 'poisoned':
                return i

        return None

    def apply_frenzy_effect(self):
        existing_item_effect = self.is_frenzy_effect_applied()
        if existing_item_effect:
            existing_item_effect.add_time()
        else:
            self.item_effect.append(Item('frenzy', self))
            self.speed = 100

    def is_frenzy_effect_applied(self):
        for i in self.item_effect:
            if i.item_name == 'frenzy':
                return i

        return None

    def set_speed(self):
        pygame.time.set_timer(USEREVENT, 150 - self.speed)

    def move_snake(self):
        boxmove = self.interface.view.boxmove
        direction = self.direction

        if self.game_over:
            return

        temp = self.move(self.snakes[-1], direction, boxmove)

        if self.is_snake_colliding(temp):
            self.game_over = True
            return

        if self.is_snake_eating_item(temp):
            self.change_snake_score()

        self.snakes.append(self.move(self.snakes[-1], direction, boxmove))
        self.snakes = self.snakes[1:]
        self.moved = True

    def change_snake_score(self):
        boxmove = self.interface.view.boxmove
        add_score = 5 if self.item_type == 'golden_apple' else 1

        self.score += add_score
        self.is_item_eaten = True

        for i in range(0, add_score):
            self.snakes.insert(0, self.move(self.snakes[0], Snake.get_inverse(self.last_direction), boxmove))

        self.change_speed()

    def move(self, rect, direction, boxmove):
        x = 0
        y = 0
        if direction == 'L' or direction == 'R':
            x = boxmove * (-1 if direction == 'L' else 1)
        elif direction == 'U' or direction == 'D':
            y = boxmove * (-1 if direction == 'U' else 1)

        if rect.x + x > 500:
            x -= 500
        elif rect.x + x < 0:
            x += 500
        elif rect.y + y > 500:
            y -= 500
        elif rect.y + y < 0:
            y += 500

        return rect.move(x,y)

    def spawn_item(self):
        if not self.is_item_eaten:
            return self.item

        self.is_item_eaten = False

        self.item_type = self.random_with_probability()

        print(self.item_type)

        random_x = 5 + random.randint(0,24)*20
        random_y = 5 + random.randint(0,24)*20

        while [random_x, random_y] in self.get_snake_xy():
            random_x = 5 + random.randint(0,24)*20
            random_y = 5 + random.randint(0,24)*20

        self.item = Rect( random_x, random_y, 15, 15 )

        return self.item

    def is_snake_eating_item(self, rect):
        if rect.collidelistall([self.item]) == []:
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

    def random_with_probability(self):
        prefix = []
        sum = 0

        for i in self.arbitrary_probability:
            sum += i
            prefix.append(sum)

        rand = random.randint(0, sum)

        for i in prefix:
            if rand < i:
                rand = i
                break

        return self.known_item_type[prefix.index(rand)]

class Item:
    def __init__(self, item_name, snake):
        self.item_name = item_name
        self.count = 5
        self.finished = False
        self.snake = snake

    def countdown(self):
        if self.count > 0:
            self.count -= 1
        else:
            self.finished = True

        if self.finished:
            self.clear_effect()

    def clear_effect(self):
        self.snake.remove_effect(self)

    def add_time(self, time=5):
        self.count += time
