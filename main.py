#!/usr/bin/env python3

import pygame, random, sys
from pygame.locals import *
from socket import *
import time
import threading
from ast import literal_eval
import select
from snake.snake import Snake

class game_main:
    def __init__(self):
        self.fps = 30
        self.fpsclock = pygame.time.Clock()

        self.view = View()

        self.snake_obj = Snake()

        pygame.time.set_timer(USEREVENT, 150)

        # ['base', 'menu', 'pause', 'ingame', 'gameover', 'locating_server', 'lan_game_mode']
        self.screen = 'menu'

        self.on_menu = True
        self.on_pause = False

        self.thread_list = []

        self.interface = Interface(main=self, view=self.view, snake=self.snake_obj)

    def main(self):
        fps = self.fps
        fpsclock = self.fpsclock
        view = self.view

        while True:
            view.show('base')

            if self.on_menu or self.on_pause:

                view.show(self.screen)

                for event in pygame.event.get():
                    self.event_parser(event)

            else:
                if self.snake_obj.game_over:
                    pygame.time.set_timer(USEREVENT, 0)
                    view.show('gameover')

                for event in pygame.event.get():
                    if event.type == KEYUP and event.key == K_ESCAPE:
                        self.change_screen('pause')
                    elif event.type == KEYDOWN and event.key == K_UP:
                        self.snake_obj.change_direction('U')
                    elif event.type == KEYDOWN and event.key == K_DOWN:
                        self.snake_obj.change_direction('D')
                    elif event.type == KEYDOWN and event.key == K_LEFT:
                        self.snake_obj.change_direction('L')
                    elif event.type == KEYDOWN and event.key == K_RIGHT:
                        self.snake_obj.change_direction('R')
                    elif event.type == KEYDOWN and event.key == K_SPACE:
                        if self.snake_obj.game_over:
                            self.interface.change_snake()
                            pygame.time.set_timer(USEREVENT, 200)
                    elif event.type == USEREVENT:
                        self.snake_obj.move_snake()
                    elif event.type == USEREVENT+2:
                        self.snake_obj.item_effect_countdown()

                view.show_ingame()

            pygame.display.update()
            fpsclock.tick(fps)

    def event_parser(self, event):
        view = self.view
        conn = self.interface.conn

        if event.type == pygame.QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            if self.screen == 'locating_server':
                self.change_screen('menu')
            else:
                if conn:
                    conn.close()
                pygame.quit()
                sys.exit()

        elif event.type == USEREVENT+1:
            view.cll_locating_server.set_next_true()
            if conn.is_connected():
                pygame.time.set_timer(USEREVENT+1, 0)
                self.screen = 'lan_game_mode'

        elif event.type == KEYDOWN and event.key == K_UP:
            view.current_menu.set_prev_true()

        elif event.type == KEYDOWN and event.key == K_DOWN:
            view.current_menu.set_next_true()

        elif event.type == KEYDOWN and event.key == K_RETURN:
            current_selection = view.current_menu.get_true()
            if current_selection.data[0] == "PLAY" or current_selection.data[0] == "RESUME":
                self.change_screen('ingame')
            elif current_selection.data[0] == "JOIN SERVER":
                if conn is None:
                    self.interface.set_connection(Connection(client=True))
                    conn_thread = threading.Thread(target=self.interface.conn.client.find_server)
                    conn_thread.start()
                    self.thread_list.append(conn_thread)

                self.screen = 'locating_server'
                pygame.time.set_timer(USEREVENT+1, 250)
            elif current_selection.data[0] == "BACK TO MENU" or current_selection.data[0] == "RESTART":
                self.interface.change_snake()
                pygame.time.set_timer(USEREVENT, 200)
                self.change_screen('menu')
                if current_selection.data[0] == "RESTART":
                    self.change_screen('ingame')
            elif current_selection.data[0] == "QUIT":
                if conn:
                    conn.close()
                pygame.quit()
                sys.exit()

    def change_screen(self, screen):
        if screen == 'menu':
            self.on_menu = True
            self.on_pause = False
        elif screen == 'pause':
            self.on_menu = False
            self.on_pause = True
        else:
            self.on_menu = False
            self.on_pause = False

        self.screen = screen

class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class CLL:
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def add_first(self, data):
        if self.count == 0:
            self.head = Node(data)
            self.tail = self.head
            self.head.next = self.head
            self.count += 1

        else:
            n = Node(data)
            n.next = self.head
            self.head = n
            self.tail.next = n
            self.count += 1

    def remove_first(self):
        if self.count == 0:
            return
        else:
            old = self.head
            self.head = self.head.next
            self.tail.next = self.head
            old = None
            self.count -= 1

    def add_last(self, data):
        if self.count == 0:
            self.add_first(data)
        else:
            n = Node(data)
            self.tail.next = n
            n.next = self.head
            self.tail = n
            self.count += 1

    def remove_last(self):
        if self.count == 0:
            return
        else:
            old = self.tail

            t = self.head
            while t.next != self.tail:
                t = t.next

            self.tail = t
            t.next = self.head
            self.count -= 1

    def remove(self, data):
        t = self.head
        while True:
            if t.next.data == data:
                temp = t.next
                t.next = t.next.next
                temp = None
                self.count -= 1
                break

            if t.next == self.head:
                break

            t = t.next

    def print_all(self):
        t = self.head
        while True:
            print(t.data, end='')

            if t.next == self.head:
                print()
                break

            print(" -> ", end='')

            t = t.next

    def get_all(self):
        t = self.head
        retr = []

        while True:
            if t == self.head:
                break
            retr.append(t.data)
            t = t.next

    def get_true(self):
        t = self.head

        while True:
            if t.data[1]:
                return t

            t = t.next

    def set_next_true(self):
        t = self.head

        while True:
            if t.data[1]:
                break

            t = t.next

        t.data[1] = False
        t.next.data[1] = True

    def set_prev_true(self):
        t = self.head

        while True:
            if t.next.data[1]:
                break

            t = t.next

        t.data[1] = True
        t.next.data[1] = False

class Server:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # self.server.settimeout(0.2)
        self.server.bind(("", 8000))
        self.message = b"snake_server"

        self.stop = False

    def send(self, thread):
        while True and not self.stop:
            self.server.sendto(self.message, ('<broadcast>', 8080))
            time.sleep(0.5)

    def listen(self, thread):
        while True and not self.stop:
            data, addr = self.server.recvfrom(1024)

class Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.client.setblocking(0)

        self.client.bind(("", 8080))

        self.server = ()

        self.stop = False

    def find_server(self):
        while True and not self.stop:
            ready = select.select([self.client], [], [], 5)
            if ready[0]:
                data, addr = self.client.recvfrom(1024)

                if (data, addr[1]) == (b'snake_server', 8000):
                    self.server = addr
                    break

    def send(self, data):
        client.sendto(data, self.server)

    def listen(self, thread):
        while True and not self.stop:
            data, addr = self.client.recvfrom(1024)

class Connection:
    def __init__(self, client=True, server=False):
        self.server = Server() if server else None
        self.client = Client()
        self.enemy_obj = Snake()
        self.interface = None

    def send_snake_to_server(self):
        while True:
            self.client.send(str(snake_obj))

    def is_connected(self):
        return self.client.server != ()

    def close(self):
        print('closing connection')
        self.client.stop = True
        if self.server is not None:
            self.server.stop = True

class View:
    def __init__(self):
        self.fps = 30
        self.fpsclock = pygame.time.Clock()

        self.bgcolor = (255, 255, 255)
        self.boxcolor = (0, 0, 0)
        self.applecolor = (255, 0, 0)
        self.golden_applecolor = (255, 215, 0)
        self.poisoncolor = (0, 128, 0)
        self.speedcolor = (0, 0, 255)

        self.boxmove = 20
        self.boxborder = 5

        self.windowwidth = 500 + self.boxborder
        self.windowheight = 500 + self.boxborder

        self.displaysurf = pygame.display.set_mode((self.windowwidth, self.windowheight))

        pygame.display.set_caption("SNAKE")

        pygame.init()

        self.cll_menu = CLL()
        self.cll_menu.add_first(["PLAY", True])
        self.cll_menu.add_last(["JOIN SERVER", False])
        self.cll_menu.add_last(["QUIT", False])

        self.cll_pause = CLL()
        self.cll_pause.add_first(["RESUME", True])
        self.cll_pause.add_last(["RESTART", False])
        self.cll_pause.add_last(["BACK TO MENU", False])

        self.cll_locating_server = CLL()
        self.cll_locating_server.add_first(["LOCATING SERVER", True])
        self.cll_locating_server.add_last(["LOCATING SERVER.", False])
        self.cll_locating_server.add_last(["LOCATING SERVER..", False])
        self.cll_locating_server.add_last(["LOCATING SERVER...", False])

        self.cll_lan_game_mode = CLL()
        self.cll_lan_game_mode.add_first(["PvP", True])
        self.cll_lan_game_mode.add_last(["BACK TO MENU", False])

        self.current_menu = self.cll_menu

        self.font = pygame.font.Font('RobotoMono-Regular.ttf', 18)
        self.gameover = self.font.render('GAME OVER', True, self.boxcolor)
        self.restart = self.font.render('PRESS SPACE TO restart', True, self.bgcolor, self.boxcolor)

        self.known_screen = ['base', 'menu', 'pause', 'ingame', 'gameover', 'locating_server', 'lan_game_mode']

        self.interface = None

        self.item_color = [self.applecolor, self.golden_applecolor, self.poisoncolor, self.speedcolor]

    def show(self, screen):
        if screen not in self.known_screen:
            self.show_text(screen)
        else:
            if screen == 'base':
                self.displaysurf.fill(self.bgcolor)
            elif screen == 'menu':
                self.current_menu = self.cll_menu
                self.show_menu()
            elif screen == 'pause':
                self.current_menu = self.cll_pause
                self.show_pause()
            elif screen == 'ingame':
                self.show_ingame()
            elif screen == 'gameover':
                self.show_gameover()
            elif screen == 'locating_server':
                self.show_locating_server()
            elif screen == 'lan_game_mode':
                self.current_menu = self.cll_lan_game_mode
                self.show_lan_game_mode()

    def show_text(self, text):
        font = self.font
        displaysurf = self.displaysurf
        windowwidth = self.windowwidth
        windowheight = self.windowheight
        boxcolor = self.boxcolor
        bgcolor = self.bgcolor

        text_render = font.render(text, True, boxcolor, bgcolor)
        text_size = font.size(text)

        displaysurf.blit(text_render, (windowwidth/2 - text_size[0]/2, windowheight/2 - text_size[1]/2))

    def show_lan_game_mode(self):
        font = self.font
        displaysurf = self.displaysurf
        windowwidth = self.windowwidth
        windowheight = self.windowheight
        boxcolor = self.boxcolor
        bgcolor = self.bgcolor

        text = 'CONNECTED TO ' + str(self.interface.conn.client.server)

        text_render = font.render(text, True, boxcolor, bgcolor)
        text_size = font.size(text)

        is_pvp = self.cll_lan_game_mode.get_true().data[0] == 'PvP'
        is_btm = not is_pvp

        pvp = font.render('PvP', True, (bgcolor if is_pvp else boxcolor),
                (boxcolor if is_pvp else bgcolor))
        btm = font.render('BACK TO MENU', True, (bgcolor if is_btm else boxcolor),
                (boxcolor if is_btm else bgcolor))

        pvp_size = font.size('PvP')
        btm_size = font.size('BACK TO MENU')

        displaysurf.blit(text_render, (windowwidth/2 - text_size[0]/2,
                            windowheight/2 - pvp_size[1]/2 - 2*text_size[1]))
        displaysurf.blit(pvp, (windowwidth/2 - pvp_size[0]/2,
                            windowheight/2 - pvp_size[1]/2))
        displaysurf.blit(btm, (windowwidth/2 - btm_size[0]/2,
                            windowheight/2 - pvp_size[1]/2 + 2*btm_size[1]))

    def show_locating_server(self):
        font = self.font
        displaysurf = self.displaysurf
        windowwidth = self.windowwidth
        windowheight = self.windowheight
        cll_locating_server = self.cll_locating_server
        boxcolor = self.boxcolor
        bgcolor = self.bgcolor

        current = cll_locating_server.get_true().data[0]

        LOCATING_SERVER = font.render(current, True, bgcolor, boxcolor)
        locating_server_size = font.size(current)

        displaysurf.blit(LOCATING_SERVER, (windowwidth/2 - locating_server_size[0]/2,
                            windowheight/2 - locating_server_size[1]/2))

    def show_gameover(self):
        font = self.font
        displaysurf = self.displaysurf
        gameover = self.gameover
        restart = self.restart
        windowwidth = self.windowwidth
        windowheight = self.windowheight

        gameover_size = font.size("GAME OVER")
        restart_size = font.size("PRESS SPACE TO restart")
        displaysurf.blit(gameover, (windowwidth - gameover_size[0] - 5, windowheight - gameover_size[1]))
        displaysurf.blit(restart, (windowwidth/2 - restart_size[0]/2, restart_size[1]))

    def show_ingame(self):
        displaysurf = self.displaysurf
        boxcolor = self.boxcolor
        snake_obj = self.interface.main.snake_obj

        if len(snake_obj.item_effect) != 0:
            for i in range(0, len(snake_obj.item_effect)):
                effect = snake_obj.item_effect[i]
                effect_name = effect.item_name
                effect_color = self.item_color[3] if effect_name == 'frenzy' else self.item_color[2]

                snake_status = effect_name.upper() + ' ' + str(effect.count)
                snake_status_render = self.font.render(snake_status, True, effect_color)

                displaysurf.blit(snake_status_render, (5, 480 - (24 * (i+1))))

        SCORE = self.font.render('SCORE '+str(snake_obj.score), True, boxcolor)
        displaysurf.blit(SCORE, (5,480))

        for rect in snake_obj.snakes:
            pygame.draw.rect(displaysurf, boxcolor, rect)

        snake_obj.spawn_item()

        itemcolor = self.item_color[snake_obj.known_item_type.index(snake_obj.item_type)]

        pygame.draw.rect(displaysurf, itemcolor, snake_obj.item)

    def show_menu(self):
        cll_menu = self.cll_menu
        boxcolor = self.boxcolor
        bgcolor = self.bgcolor
        windowwidth = self.windowwidth
        windowheight = self.windowheight
        displaysurf = self.displaysurf
        font = self.font

        is_play = False
        is_quit = False
        is_jserver = False

        current_selection = cll_menu.get_true()

        if current_selection.data[0] == "PLAY":
            is_play = True
        elif current_selection.data[0] == "JOIN SERVER":
            is_jserver = True
        elif current_selection.data[0] == "QUIT":
            is_quit = True

        PLAY = font.render('PLAY', True, (bgcolor if is_play else boxcolor),
                (boxcolor if is_play else bgcolor))
        JOIN_SERVER = font.render('JOIN SERVER', True, (bgcolor if is_jserver else boxcolor),
                (boxcolor if is_jserver else bgcolor))
        QUIT = font.render('QUIT', True, (bgcolor if is_quit else boxcolor),
                (boxcolor if is_quit else bgcolor))

        play_size = font.size("PLAY")
        join_server_size = font.size("JOIN SERVER")
        quit_size = font.size("QUIT")

        displaysurf.blit(PLAY, (windowwidth/2 - play_size[0]/2, windowheight/2 - 3 * play_size[1]))
        displaysurf.blit(JOIN_SERVER, (windowwidth/2 - join_server_size[0]/2,
                            windowheight/2 - join_server_size[1]))
        displaysurf.blit(QUIT, (windowwidth/2 - quit_size[0]/2, windowheight/2 + quit_size[1]))

    def show_pause(self):
        cll_pause = self.cll_pause
        boxcolor = self.boxcolor
        bgcolor = self.bgcolor
        windowwidth = self.windowwidth
        windowheight = self.windowheight
        displaysurf = self.displaysurf
        font = self.font

        is_resume = False
        is_restart = False
        is_btm = False

        current_selection = cll_pause.get_true()

        if current_selection.data[0] == "RESUME":
            is_resume = True
        elif current_selection.data[0] == "RESTART":
            is_restart = True
        elif current_selection.data[0] == "BACK TO MENU":
            is_btm = True

        RESUME = font.render("RESUME", True, (bgcolor if is_resume else boxcolor),
                (boxcolor if is_resume else bgcolor))
        restart = font.render("RESTART", True, (bgcolor if is_restart else boxcolor),
                (boxcolor if is_restart else bgcolor))
        BTM = font.render('BACK TO MENU', True, (bgcolor if is_btm else boxcolor),
                (boxcolor if is_btm else bgcolor))

        resume_size = font.size("RESUME")
        restart_size = font.size("restart")
        btm_size = font.size("BACK TO MENU")

        displaysurf.blit(RESUME, (windowwidth/2 - resume_size[0]/2,
                            windowheight/2 - (resume_size[1] + btm_size[1])))
        displaysurf.blit(restart, (windowwidth/2 - restart_size[0]/2,
                            windowheight/2 - restart_size[1]/2))
        displaysurf.blit(BTM, (windowwidth/2 - btm_size[0]/2, windowheight/2 + btm_size[1]))

class Interface:
    def __init__(self, main, view, snake):
        self.main = main
        self.view = view
        self.view.interface = self
        self.snake = snake
        self.snake.interface = self
        self.conn = None

    def set_connection(self, conn):
        self.conn = conn
        self.conn.interface = self

    def change_snake(self):
        self.snake = Snake()
        self.main.snake_obj = self.snake
        self.snake.interface = self

if __name__ == '__main__':
    game = game_main()
    game.main()
