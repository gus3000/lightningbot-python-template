import random
import sys

from bot_template.lightningbot import Direction, Bot
from grid.grid import Grid


class MyBot(Bot):
    """
    Use this class to get started. Just fill in the move method
    """

    def __init__(self, mode: str = 'test'):
        super(MyBot, self).__init__(mode)
        self.grid = Grid(info=self.api_handler.info)
        self.grid.start(positions=self.api_handler.info)

    def move(self, current_turn: int, api_directions: list, directions: dict) -> Direction:
        """
        :param current_turn: the current turn
        :param api_directions: the bots' current directions (before moving), as given by the API
        :param directions: the bots' current directions, as a dictionnary
            ex : {'player1': Direction.DOWN, 'player2': Direction.RIGHT}
        :return: the wanted Direction
        """
        # TODO fill in your code here
        direction = directions[self.pseudo]
        self.grid.update(directions)
        if Direction.valid(direction):
            if self.grid.left(self.pseudo) == 0:
                direction = Direction.left_from(direction)
            elif self.grid.forward(self.pseudo) == 0:
                pass
            else:
                direction = Direction.right_from(direction)
        else: # choose at random
            direction = random.choice([d for d in Direction if Direction.valid(d)])

        print("[" + self.pseudo + "]", "turn", current_turn, ": moving", direction.name)
        return direction


if __name__ == '__main__':
    b: Bot = MyBot(mode='ranked')
    turn = 1
    while b.send_move(turn):
        turn += 1
