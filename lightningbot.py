import random
import requests
import json
import time
from enum import IntEnum


class Bot:
    def __init__(self, mode: str = 'test'):
        self.api_handler: ApiHandler = ApiHandler(mode)

    def move(self, current_turn: int) -> bool:
        direction = Direction.DOWN  # use Direction.UP, Direction.DOWN, Direction.LEFT or Direction.RIGHT
        # TODO fill in your code here

        # stop right there
        print('moving', direction.name)
        move_result = self.api_handler.move(direction=direction, current_turn=current_turn)
        if 'error' in move_result:
            # print('error :', move_result)
            dirs: dict = self.api_handler.get_directions(current_turn=current_turn)
            if dirs['error'] == 201:
                print('This bot is dead.')
            elif dirs['error'] == 200:
                print('You won !')
            return False
        return True


class Direction(IntEnum):
    INIT = -1
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class ApiHandler:
    def __init__(self, mode: str = 'test', base_url: str = 'https://lightningbot.tk/api/'):
        self.url: str = base_url
        self.nextMove: time = time.perf_counter()
        self.pseudo: str
        self.token: str
        self.info: dict

        if mode == 'test':
            print('Init Test mode')
            self.url += 'test'
            # name + a random number so you can launch two bot to play alone.
            # If only one bot is connected the game will not start.
            self.pseudo = 'Python' + str(random.randint(0, 9999))
            response = requests.get(
                '/'.join([self.url, 'connect', self.pseudo]))  # Ask the server a token to play the game
            connect = json.loads(response.text)  # Get the answer as a json to read it easily
            self.token = connect['token']

        else:
            print('Init Ranked mode')
            connect = None
            print("Not implemented yet.")  # TODO
            exit(0)

        print('Connected ! Waiting for info...')

        time.sleep(connect['wait'] / 1000)  # wait for the end of the connect phase
        self.info = json.loads(requests.get('/'.join([self.url, 'info', self.token])).text)  # fetch info
        print('Room name :', self.info['name'])
        self.nextMove = time.perf_counter() + (self.info['wait'] / 1000)

    def get_directions(self, current_turn: int) -> dict:
        res = requests.get('/'.join([self.url, 'directions', self.token, str(current_turn)]))
        return json.loads(res.text)

    def move(self, direction: Direction, current_turn: int) -> dict:
        if time.perf_counter() < self.nextMove:  # if we moved too soon
            time.sleep(self.nextMove - time.perf_counter())

        res = requests.get('/'.join([self.url, 'move', self.token, str(direction.value), str(current_turn)]))
        resd = json.loads(res.text)
        while 'error' in resd and resd['error'] == 3:  # this shouldn't happen, but you never know
            print('Still early ? debug info :', current_turn, self.nextMove, time.perf_counter(), resd)
            time.sleep(resd['wait'] / 1000)
            res = requests.get('/'.join([self.url, 'move', self.token, str(direction.value), str(current_turn)]))
            resd = json.loads(res.text)
        self.nextMove = time.perf_counter() + (resd['wait'] / 1000)
        return resd


if __name__ == '__main__':
    b: Bot = Bot()
    turn = 1
    while b.move(turn):
        turn += 1
