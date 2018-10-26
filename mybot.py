import random

from bot_template.lightningbot import Direction, Bot


class MyBot(Bot):
    """
    Use this class to get started. Just fill in the move method
    """

    def __init__(self, mode: str = 'test'):
        super(MyBot, self).__init__(mode)

    def move(self, current_turn: int, api_directions: list, directions: dict) -> Direction:
        """
        :param current_turn: the current turn
        :param api_directions: the bots' current directions (before moving), as given by the API
        :param directions: the bots' current directions, as a dictionnary
            ex : {'player1': Direction.DOWN, 'player2': Direction.RIGHT
        :return: the wanted Direction
        """
        # TODO fill in your code here
        # use Direction.UP, Direction.DOWN, Direction.LEFT or Direction.RIGHT
        # for example go down :
        # direction = Direction.DOWN

        # or choose a random direction (spoiler : it will die quickly):
        # direction = random.choice([d for d in Direction])

        # or choose a random direction expect the opposite one :
        direction = random.choice([d for d in Direction if Direction.valid(d)
                                   and d != Direction.opposite(directions[self.pseudo])])

        print("[" + self.pseudo + "]", "turn", current_turn, ": moving", direction)
        return direction


if __name__ == '__main__':
    b: Bot = MyBot()
    turn = 1
    while b.send_move(turn):
        turn += 1
