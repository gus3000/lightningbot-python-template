import sys
import random
import requests
import json
import os
import time
from enum import IntEnum


class Direction(IntEnum):
    DEAD = -2
    INIT = -1
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3

    @staticmethod
    def opposite(direction):
        if direction == Direction.RIGHT:
            return Direction.LEFT
        elif direction == Direction.LEFT:
            return Direction.RIGHT
        elif direction == Direction.DOWN:
            return Direction.UP
        elif direction == Direction.UP:
            return Direction.DOWN

    @staticmethod
    def left_from(direction):
        if direction == Direction.RIGHT:
            return Direction.UP
        elif direction == Direction.LEFT:
            return Direction.DOWN
        elif direction == Direction.DOWN:
            return Direction.RIGHT
        elif direction == Direction.UP:
            return Direction.LEFT
        return direction

    @staticmethod
    def right_from(direction):
        if direction == Direction.RIGHT:
            return Direction.DOWN
        elif direction == Direction.LEFT:
            return Direction.UP
        elif direction == Direction.DOWN:
            return Direction.LEFT
        elif direction == Direction.UP:
            return Direction.RIGHT
        return direction

    @staticmethod
    def valid(direction):
        return direction in [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]


class Bot:
    def __init__(self, mode: str = 'test'):
        self.api_handler: ApiHandler = ApiHandler(mode)
        self.pseudo = self.api_handler.pseudo

    def move(self, current_turn: int, api_directions: dict, directions: dict) -> Direction:
        return Direction.DOWN  # use Direction.UP, Direction.DOWN, Direction.LEFT or Direction.RIGHT

    def send_move(self, current_turn: int) -> bool:
        directions: dict = self.api_handler.get_directions(current_turn)
        if 'error' in directions:
            if directions['error'] == 201:
                print('This bot is dead.')
            elif directions['error'] == 200:
                print('You won !')
            else:
                print('directions are all wrong !', file=sys.stderr)
                print('exiting now, debug info :', '\ncurrent_turn', current_turn, '\ndirections', directions,
                      file=sys.stderr)
                exit(-1)
            return False

        direction = self.move(current_turn=current_turn, directions=Bot.better_directions(directions),
                              api_directions=directions)

        # print('moving', direction.name)
        move_result = self.api_handler.move(direction=direction, current_turn=current_turn)

        return True

    # Utility methods
    @staticmethod
    def better_directions(api_directions: dict) -> dict:
        dirs = {}
        directions = api_directions['directions']
        try:
            for d in directions:
                dirs[d['pseudo']] = Direction(int(d['direction']))
        except (TypeError, ValueError):
            print('failed better_directions on :', directions, file=sys.stderr)
            return None
        return dirs

    @staticmethod
    def better_positions(api_positions: dict) -> dict:
        pos = {}
        positions = api_positions['positions']
        try:
            for p in positions:
                pos[p['pseudo']] = {'x': p['x'], 'y': p['y']}
        except (TypeError, ValueError):
            print('failed better_positions on :', positions, file=sys.stderr)
            return None
        return pos


class ApiHandler:
    def __init__(self, mode: str = 'test', base_url: str = 'https://lightningbot.tk/api'):
        """Constructs an Lightningbot API handler. It handles connection, info and direction retrieving and move sending.

        :param mode: either "test" or "ranked"
        :param base_url: defaults to 'https://lightningbot.tk/api/', and shouldn't change, but you never know
        """
        self.url: str = base_url
        self.nextMove: time = time.perf_counter()
        self.pseudo: str
        self.token: str
        self.info: dict
        self.directions_cache: dict = {}

        if mode == 'test':
            print('Init Test mode')
            self.url = '/'.join([self.url, 'test'])
            # name + a random number so you can launch two bot to play alone.
            # If only one bot is connected the game will not start.
            self.pseudo = 'Python' + str(random.randint(0, 9999))
            response = requests.get(
                '/'.join([self.url, 'connect', self.pseudo]))  # Ask the server a token to play the game
            connect = json.loads(response.text)  # Get the answer as a dictionary to read it easily
            try:
                self.token = connect['token']
            except KeyError:
                print('[' + self.pseudo + ']', 'Error while retrieving token.', 'Code', connect['error'], ':',
                      connect['description'],
                      file=sys.stderr)
                exit(-1)

        elif mode == 'ranked':
            try:
                self.token = os.environ['TOKEN']
            except KeyError:
                print("environment varialbe 'TOKEN' not found.", file=sys.stderr)
                exit(-1)
            print('Init Ranked mode')
            response = requests.get(
                '/'.join([self.url, 'connect', self.token]))  # Ask the server to connect
            connect = json.loads(response.text)  # Get the answer as a dictionary to read it easily
            try:
                self.pseudo = connect['pseudo']
            except KeyError:
                print('Error while attempting to connect with token.', 'Code', connect['error'], ':',
                      connect['description'],
                      file=sys.stderr)
                exit(-1)
        else:
            print('choose either "ranked" or "test" mode')
            exit(0)

        print('Connected ! Waiting for info... (' + str(connect['wait'] / 1000) + ' s)')

        time.sleep(connect['wait'] / 1000)  # wait for the end of the connect phase
        self.info = json.loads(requests.get('/'.join([self.url, 'info', self.token])).text)  # fetch info

        try:
            print('Room name :', self.info['name'])
        except KeyError:
            print('Unable to fetch room name in info', self.info, file=sys.stderr)
            print('This is proably due to the fact that no one else connected. :c', file=sys.stderr)

            exit(-1)

        self.nextMove = time.perf_counter() + (self.info['wait'] / 1000)

    def get_directions(self, current_turn: int, force=False) -> dict:
        if not force and current_turn in self.directions_cache:
            return self.directions_cache[current_turn]

        res = requests.get('/'.join([self.url, 'directions', self.token, str(current_turn)]))
        current_directions = json.loads(res.text)
        while 'error' in current_directions and current_directions['error'] == 3:
            time.sleep(current_directions['wait'] / 1000)
            res = requests.get('/'.join([self.url, 'directions', self.token, str(current_turn)]))
            current_directions = json.loads(res.text)

        self.directions_cache[current_turn] = current_directions
        return current_directions

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
