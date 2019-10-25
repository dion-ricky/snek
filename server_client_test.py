from socket import *
import time
import threading

class Server:
    def __init__(self):
        self.server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.server.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # self.server.settimeout(0.2)
        self.server.bind(("", 8000))
        self.message = b"snake_server"

    def send(self, thread):
        while True:
            self.server.sendto(self.message, ('<broadcast>', 8080))
            time.sleep(0.5)

    def listen(self, thread):
        while True:
            data, addr = self.server.recvfrom(1024)

class Client:
    def __init__(self):
        self.client = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.client.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        self.client.bind(("", 8080))

        self.server = ()

    def find_server(self):
        while True:
            data, addr = self.client.recvfrom(1024)

            print(data)

            if literal_eval(data) == ('snake_server', 8080):
                self.server = addr
                break

    def send(self, data):
        client.sendto(data, self.server)

    def listen(self, thread):
        while True:
            data, addr = self.client.recvfrom(1024)

class Connection:
    def __init__(self, snake):
        self.client = Client()
        self.enemy_obj = Snake()
        self.snake_obj = snake

    def send_snake_to_server(self):
        while True:
            self.client.send(str(snake_obj))

    def is_connected(self):
        return self.client.server != ()

if __name__ == '__main__':
    conn = Connection()
    threading.Thread
