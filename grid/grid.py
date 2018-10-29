from pprint import pprint
import sys

from bot_template.lightningbot import Bot, Direction


class Grid:
    def __init__(self, size=0, info=None):
        self.players = {}

        if size == 0 and info is None:
            print('Error while initializing Grid, size and info not given.', file=sys.stderr)
            exit(-1)
        elif info is not None:
            try:
                size = info['dimensions']
            except KeyError:
                print('Error while retrieving dimensions.', 'Code', info['error'], ':', info['description'],
                      file=sys.stderr)
                exit(-1)
        print('size :', size)
        self.size = size
        self.grid = [[0] * size for i in range(size)]
        pprint(self.grid)

    def coords(self, pseudo: str) -> dict:
        return self.players[pseudo]

    def start(self, positions: dict) -> None:
        if 'success' in positions:  # if the raw API object is given
            positions = Bot.better_positions(positions)  # we make the positions easier to read

        i: int = 1
        for k, p in positions.items():
            p['x'] = p['x'] % self.size
            p['y'] = p['y'] % self.size

            self.players[k] = {
                'index': i,
                'x': p['x'],
                'y': p['y'],
                'direction': Direction.INIT
            }
            self.grid[p['y']][p['x']] = i
            i += 1
        print(self.players)
        pprint(self.grid)

    def update(self, directions: dict) -> None:
        if 'success' in directions:  # if the raw API object is given
            directions = Bot.better_directions(directions)  # we make the directions easier to read

        for pseudo, d in directions.items():
            old_x = self.players[pseudo]['x']
            old_y = self.players[pseudo]['y']
            x = old_x
            y = old_y

            if d is Direction.LEFT:
                x -= 1
            elif d is Direction.RIGHT:
                x += 1
            elif d is Direction.DOWN:
                y -= 1
            elif d is Direction.UP:
                y += 1

            # keep the coordinates in the grid
            x = (x + self.size) % self.size
            y = (y + self.size) % self.size

            # print('[' + pseudo + ']', 'old :', self.players[pseudo]['x'], self.players[pseudo]['y'], '\tnew :', x, y)

            self.grid[y][x] = self.players[pseudo]['index']
            self.players[pseudo]['x'] = x
            self.players[pseudo]['y'] = y
            self.players[pseudo]['direction'] = d

        # pprint(self.grid)

    def left(self, pseudo: str) -> int:
        p = self.players[pseudo]
        x, y = p['x'], p['y']
        direction = Direction.left_from(p['direction'])
        return self.next_coord(x, y, direction)

    def right(self, pseudo: str) -> int:
        p = self.players[pseudo]
        x, y = p['x'], p['y']
        direction = Direction.right_from(p['direction'])
        return self.next_coord(x, y, direction)

    def forward(self, pseudo: str) -> int:
        p = self.players[pseudo]
        x, y = p['x'], p['y']
        direction = p['direction']
        return self .next_coord(x, y, direction)

    def next_coord(self, x, y, direction):
        if direction is Direction.LEFT:
            x -= 1
        elif direction is Direction.RIGHT:
            x += 1
        elif direction is Direction.DOWN:
            y -= 1
        elif direction is Direction.UP:
            y += 1

        # keep the coordinates in the grid
        x = (x + self.size) % self.size
        y = (y + self.size) % self.size

        return self.grid[y][x]
