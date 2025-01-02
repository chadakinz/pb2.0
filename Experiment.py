import sys
from enum import Enum
import random
import numpy as np
import math
from pokerBot.Poker_bot_desicions.poker_bot import PokerBot
from pokerBot.Poker_bot_desicions import Equity, Pre_flop_hand_rankings

import eval7


class States(Enum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    def get_next_state(state):
        match state:
            case States.PREFLOP:
                return States.FLOP

            case States.FLOP:
                return States.TURN

            case States.TURN:
                return States.RIVER

            case States.RIVER:
                return States.PREFLOP

class Card:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
    def __str__(self):
        return f"{self.value}{self.suit}"
class Deck:
    def __init__(self):
        self._deck = []
        suits = ['c', 'd', 's', 'h']
        for i in suits:
            for j in range(2, 15):
                if j == 10:
                    self._deck.append(Card("T", i))
                elif j == 11:
                    self._deck.append(Card("J", i))
                elif j == 12:
                    self._deck.append(Card("Q", i))
                elif j == 13:
                    self._deck.append(Card("K", i))
                elif j == 14:
                    self._deck.append(Card("A", i))
                else:

                    self._deck.append(Card(j, i))
        self._dealt_cards = []

    def shuffle(self):
        while len(self._dealt_cards) > 0:
            self._deck.append(self._dealt_cards.pop())
        random.shuffle(self._deck)

    def deal_card(self):
        card = self._deck.pop()
        self._dealt_cards.append(card)
        return card

class Player:
    def __init__(self, id):
        self.id = id
        self.chips = 1000
        self.hand = []
        self.action = None
        self.raise_tot = 0
        self.raise_amnt = 0
    def reset(self):
        self.raise_tot = 0
        self.raise_amnt = 0
        self.hand = []

class Environment:
    def __init__(self, players):

        self.state = States.PREFLOP
        self.pot = 0
        self.board = []
        self.blinds = [1, 2]
        self.players = players
        self.deck = Deck()
        self.turn_tracker = Turn_Tracker(players, players[0].id)
        self.raise_tot = 0
        self.call_amount = 0
        self.raise_amnt = self.blinds[1]

    def action_handler(self, id, action):
        """
        :param action (tuple): (action, raise_amount)
        :param id (int): id of current player
        :return: id of the player whos turn is next
        """

        opp_id = 0 if id == 1 else 1
        match action[0]:
            case "FOLD":
                self.players[opp_id].chips += self.pot
                self.state_handler()

            case "CHECK":
                self.turn_tracker.set()
                if self.turn_tracker.check():
                    self.state_handler()


            case "CALL":
                self.turn_tracker.set()
                self.players[id].chips -= self.players[opp_id].raise_amnt - self.players[id].raise_amnt
                self.players[id].raise_amnt = self.players[opp_id]
                if self.turn_tracker.check():
                    self.state_handler()


            case "RAISE":

                raise_amnt = self.players[id].raise_amnt - self.players[opp_id].raise_amnt
                if raise_amnt < self.raise_amnt:
                    print("RAISE AMOUNT TOO SMALL MUST RAISE AT LEAST", self.raise_amnt, id)
                    return id
                else:
                    self.turn_tracker.raise_reset()
                    self.raise_amnt = raise_amnt if raise_amnt > self.raise_amnt else self.raise_amnt
                    self.players[id].chips -= raise_amnt
                    self.players[id].raise_amnt += raise_amnt
                    self.call_amount = self.players[id].raise_amnt - self.players[opp_id].raise_amnt



        return self.turn_tracker.set_dealer()

    def state_handler(self):
        for player in self.players:
            self.pot += player.raise_tot
            player.raise_tot = 0
        match self.state:
            case States.PREFLOP:
                self.reset()
                self.preflop_handler()

            case States.FLOP:
                self.flop_handler()

            case States.TURN:
                self.turn_handler()

            case States.RIVER:
                self.river_handler()

        self.state = self.state.get_next_state()
    def reset(self):
        self.turn_tracker.reset()
        self.pot = self.call_amount = 0
        self.board = []
        for player in self.players:
            player.reset()
        self.deck.shuffle()
        self.state = States.PREFLOP

    def preflop_handler(self):
        for player in self.players:
            for i in range(2):
                player.hand.append(self.deck.deal_card())
        dealer_id = self.turn_tracker.set_dealer()
        big_blind_id = 0 if dealer_id == 1 else 1
        self.players[dealer_id].raise_amnt = self.blinds[0]
        self.players[big_blind_id].raise_amnt = self.blinds[1]
        self.players[dealer_id].chips -= self.blinds[0]
        self.players[big_blind_id].chips -= self.blinds[1]
        self.raise_tot = self.blinds[1]





    def flop_handler(self):
        for i in range(3):
            self.board.append(self.deck.deal_card())
        self.raise_tot = 0



    def turn_handler(self):
        self.board.append(self.deck.deal_card())
        self.raise_tot = 0



    def river_handler(self):
        self.board.append(self.deck.deal_card())
        self.raise_tot = 0

    def start_game(self):
        self.preflop_handler()
        return self.turn_tracker.set_dealer()
class Model:
    def __init__(self, actions, gamma, alpha, epsilon):
        self.actions = actions
        self.state_actions = np.zeros((4, 4, 4, 5, 9))
        self.state_action_distribution = np.zeros((4, 4, 4, 5, 9))
        self.state_action_distribution.fill(1 / 9)

        self.current_SA = None
        self.alpha = alpha
        self.action_log = []
        self.gamma = gamma
        self.epsilon = epsilon

    def get_action(self, state):
        current_action = self.choose_action(state)
        self.action_log.append(current_action)
        self.current_SA = state, current_action
        print(self.current_SA)
        return current_action

    def policy_update(self, reward, next_state):


        optimal_future_action = self.get_max_value(next_state)

        self.state_actions[self.current_SA[0]][self.current_SA[1]] += (self.alpha *
                                                (reward + (self.gamma *
                                                           self.state_actions[next_state][
                                                               optimal_future_action]) -
                                                 self.state_actions[self.current_SA[0]][self.current_SA[1]]))
        self.update_distribution(self.current_SA[0])
    def choose_action(self, state):

        print(self.state_action_distribution[state])
        return np.random.choice(self.actions, size=1, p=self.state_action_distribution[state])[0]

    def update_distribution(self, state):
        print(state)
        best_action = self.get_max_value(state)
        print(f"BEST ACTION: {best_action}")
        print(state)
        for x in range(len(self.state_action_distribution[state])):
            if x == best_action:
                self.state_action_distribution[state][x] += (1 - self.state_action_distribution[state][x]) * self.epsilon


            else:
                self.state_action_distribution[state][x] -= self.state_action_distribution[state][x] * self.epsilon

    def get_max_value(self, state):
        return np.unravel_index(np.argmax(self.state_actions[state]), self.state_actions.shape)[1]

class Turn_Tracker:
    def __init__(self, players, start_id):
        self._switch = 0
        self._dealer = start_id

    def set(self):
        self._switch += 1

    def check(self):
        return self._switch == 2
    def reset(self):
        self._dealer = 0 if self._dealer == 1 else 1
        self._switch = 0

    def raise_reset(self):
        self._switch = 1

    def set_dealer(self):
        self._dealer = 0 if self._dealer == 1 else 1
        return self._dealer
    def is_dealer(self, id):
        return 0 if id != self._dealer else 1
class Printing:
    def __init__(self, environment):
        self._environment = environment
def read_state(env):
    """
    Reads the state and converts it into a tuple of integers which the Q-Learning model can read.
    env -> (our_chips, pot_size, state_of_game, equity)
    0 <= our_chips, pot_size <= 3
    our_chips, pot_size = 0 -> 0-25 percent of total amount of chips
    our_chips, pot_size = 1 -> 25-50 percent of total amount of chips
    ....
    ....
    0 <= equity <= 4
    equity = 0 -> 0-20 percent chance of winning
    equity = 1 -> 20-40 percent chance of winning
    ....
    ....

    :param env:
    :return:
    """
    per_conv = [.25, .5, .75, 1]
    eq_conv = [.2, .4, .6, .8, 1]
    tot_chips = 2000
    po_chips = env.players[1].chips/tot_chips
    po_pot = env.pot/tot_chips
    equity = Equity.Equity(env.players[1].hand, dist(table.turn_tracker.is_dealer(1)), env.board, 300)
    for i in range(len(per_conv)):
        if po_chips <= per_conv[i]:
            po_chips = i
            break
    for i in range(len(per_conv)):
        if po_pot <= per_conv[i]:
            po_pot = i
            break

    for i in range(len(eq_conv)):
        if equity <= eq_conv[i]:
            equity = i
            break
    return po_chips, po_pot, env.state.value, equity

def read_action(action, env):
    """
    Reads the action from the model so the environment can read
    0 <= action <= 8
    0 = fold
    1 = call/check
    2 = raise_min
    ...
    ...
    ...
    ...
    8 = raise_max
    :param action:
    :return:
    """
    if action == 0:
        return "FOLD", 0
    elif action == 1:
        return "CALL"
    else:
        min_raise = env.call_amount + env.raise_amnt

        max_raise = env.players[1].chips
        print(f"Min Raise: {min_raise}, Max Raise: {max_raise}")
        d = (max_raise - min_raise) / 7
        raise_amnt = d * (action - 1) + min_raise
        return "RAISE", int(raise_amnt)


#TODO: Organize function below

def dist(dealer_pos):
    hand_rankings = Pre_flop_hand_rankings.hand_rankings

    card_distribution = ""
    ordered_rankings = list(hand_rankings)

    if dealer_pos == 0:
        expected = 85
    else:
        expected = 127
    for i in range(expected):
        card_distribution += f"{ordered_rankings[i]}, "

    return card_distribution[:-2]




if __name__ == "__main__":
    players = [Player(0), Player(1)]
    table = Environment(players)
    pb1 = PokerBot(1000, table.blinds[1])
    q_model = Model([0, 1, 2, 3, 4, 5, 6, 7, 8], .9, 1, .03)
    old_chips = table.players[1].chips

    turn = table.start_game()

    count = 0
    while True:

        if turn == 0:
            dealer = table.turn_tracker.is_dealer(turn)
            pb1.cards = table.players[1].hand
            pb1.chips = table.players[1].chips
            a = pb1.action(table.pot, table.raise_amnt, players[1].raise_amnt, table.state, table.board, dealer)
            players[0].raise_amnt += pb1.raise_amount
            action = (a, players[0].raise_amnt)

        else:
            print(f"ROUND: {count}")
            state = read_state(table)
            if count > 0:
                new_chips = table.players[1].chips
                reward = new_chips - old_chips
                q_model.policy_update(reward, state)

            a = q_model.get_action(state)
            action = read_action(a, table)
            print(f"ACTION: {action}")
            old_chips = table.players[1].chips
            count += 1
        turn = table.action_handler(turn, action)





