import random
import requests
import json
import time


class Bot:
    pass


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
            print("connect :", connect)
            self.token = connect['token']

        else:
            print('Init Ranked mode')
            connect = None
            print("Not implemented yet.")  # TODO
            exit(0)

        time.sleep(connect['wait'] / 1000)  # wait for the end of the connect phase
        self.info = json.loads(requests.get('/'.join([self.url, 'info', self.token])).text)  # fetch info
        self.nextMove = time.perf_counter() + (self.info['wait'] / 1000)

    def get_directions(self, current_turn) -> dict:
        res = requests.get('/'.join([self.url, 'directions', self.token, str(current_turn)]))
        return json.loads(res.text)

    def move(self, direction, current_turn) -> dict:
        if time.perf_counter() < self.nextMove:  # if we moved too soon
            time.sleep(self.nextMove - time.perf_counter())

        res = requests.get('/'.join([self.url, 'move', self.token, str(direction), str(current_turn)]))
        resd = json.loads(res.text)
        while 'error' in resd and resd['error'] == 3:  # this shouldn't happen, but you never know
            print('Still early ? debug info :', current_turn, self.nextMove, time.perf_counter(), resd)
            time.sleep(resd['wait'] / 1000)
            res = requests.get('/'.join([self.url, 'move', self.token, str(direction), str(current_turn)]))
            resd = json.loads(res.text)
        self.nextMove = time.perf_counter() + (resd['wait'] / 1000)
        return resd


h: ApiHandler = ApiHandler()
running = True
turn = 1
while running:
    result = h.move(1, turn)  # Move the bot and store the result of the request in a variable
    running = result['success']
    print('turn:', turn, "\tresult:", result)
    turn += 1

# print(h.get_directions(turn)['description'])
print(h.get_directions(turn))
