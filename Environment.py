import sys
from enum import Enum
import random
class States(Enum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
class Deck:
    def __init__(self):
        self._deck = []
        suits = ['C', 'D', 'S', 'H']
        for i in suits:
            for j in range(13):
                self._deck.append(Card(j, i))
        self._dealt_cards = []

    def shuffle(self):
        while len(self._dealt_cards) > 0:
            self._deck.append(self._dealt_cards.pop())
        random.shuffle(self._deck)

    def deal_card(self):
        card  = self._deck.pop()
        self._dealt_cards.append(card)
        return card

class Player:
    def __init__(self, id):
        self.id = id
        self.chips = 0
        self.hand = []
        self.action = None
class Environment:
    def __init__(self):

        self.state = States.PREFLOP
        self.pot = 0
        self.board = []
        self.blinds = [2, 4]

    def action_handler(self, action):
        match self.state:
            case States.PREFLOP:
                self.preflop_handler()
                self.state += 1
            case States.FLOP:
                self.flop_handler()
                self.state += 1

            case States.TURN:
                self.turn_handler()
                self.state += 1
            case States.RIVER:
                self.river_handler()
                self.state += 1

    def preflop_handler(self):
        pass

    def flop_handler(self):
        pass

    def turn_handler(self):
        pass

    def river_handler(self):
        pass
class Model:
    def __init__(self):
        pass

class Turn_Tracker:
    def __init__(self, players, start_id):





        pass


if __name__ == "__main__":
    player1 = Player(0)
    player2 = Player(1)
    table = Environment()
    done = True
    while done:
        pass

    print(sys.executable)