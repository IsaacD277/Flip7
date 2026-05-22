# Start Game
# Initialize
#     - Player Names
#     - Starting Player
#     - Analytics?
# Main
#     - All Rounds
#         - All Turns
#             - Update Database
#         - Show Leaderboard
#     - End Game

import uuid
import pathlib
from dataclasses import dataclass, field

ROOT_DIR = pathlib.Path(__file__).parent.parent
DB_PATH = ROOT_DIR / "flip7.db"

@dataclass
class Hand:
    numbers: list[int] = field(default_factory = list)
    addition: list[int] = field(default_factory = list)
    sc: bool = field(default = False)
    multiplier: bool = field(default = False)

class Player:
    def __init__(self, player_id, name, tolerance = 100):
        self.id = player_id
        self.name = name
        self.active = True
        self.tolerance = tolerance
        self.score = []
        self.hand = Hand()

    def hand_list(self):
        hand_list = []
        for card in self.hand.numbers:
            hand_list.append(str(card))
        for card in self.hand.addition:
            hand_list.append(f"+{card}")
        if self.hand.sc:
            hand_list.append("sc")
        if self.hand.multiplier:
            hand_list.append("x2")
        return hand_list

    def reset_hand(self):
        self.hand = Hand()

    def hand_score(self):
        current_score = sum(self.hand.numbers)
        if self.hand.multiplier:
            current_score += current_score
        current_score += sum(self.hand.addition)
        return current_score

    def bank(self):
        self.score.append(self.hand_score())
        self.reset_hand()
        self.active = False

    def bust(self):
        self.score.append(0)
        self.reset_hand()
        self.active = False

    def check_seven(self):
        if len(self.hand.numbers) >= 7:
            self.hand.addition.append(15)
            return True
        return False

    def bust_chance(self, deck):
        if self.hand.sc:
            return 0.0
        cards_remaining = 0
        bust_cards = 0
        for card in deck:
            cards_remaining += deck[card]
        for card in self.hand_list():
            bust_cards += deck[str(card)]
        return round((bust_cards / cards_remaining) * 100, 2)

    def expected_value(self, deck):
        card_count = 0
        expected_sum = 0
        hand = []
        hand_value = 0
        for card in self.hand.numbers:
            hand.append(str(card))
            hand_value += int(card)
        for card in self.hand.addition:
            hand.append(f"+{card}")
            hand_value += card
        if self.hand.multiplier:
            hand_value *= 2
        for card in deck:
            card_count += deck[card]
            if deck[card] <= 0:
                continue
            if card in hand:
                if self.hand.sc:
                    continue
                else:
                    expected_sum -= hand_value
            elif card[0] == "+":
                expected_sum += int(card[1:]) * deck[card]
            elif card == "x2":
                expected_sum += hand_value
            elif card in ["sc", "f3", "fr", "0"]:
                continue
            else:  # number cards
                if len(self.hand.numbers) >= 6:
                    if self.hand.multiplier:
                        expected_sum += (15 + int(card) + int(card)) * deck[card]
                    else:
                        expected_sum += (15 + int(card)) * deck[card]
                else:
                    if self.hand.multiplier:
                        expected_sum += (int(card) + int(card)) * deck[card]
                    else:
                        expected_sum += int(card) * deck[card]
        if card_count <= 0:
            return 0
        return round(expected_sum / card_count, 2)

class GameState:
    def __init__(self, analytics = True, round = 1):
        self.cards = {
            "0": 1,
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "11": 11,
            "12": 12,
            "sc": 3,
            "fr": 3,
            "f3": 3,
            "+2": 1,
            "+4": 1,
            "+6": 1,
            "+8": 1,
            "+10": 1,
            "x2": 1
        }
        self.deck = self.cards.copy()
        self.players = []
        self.analytics = analytics
        self.gameId = uuid.uuid4()
        self.round = round

    def add_player(self, name, tolerance = 100):
        player = Player(len(self.players) + 1, name, tolerance)
        self.players.append(player)

    def set_analytics(self, choice: bool):
        self.analytics = choice

    def current_player(self):
        if not self.players:
            return None
        return self.players[0]

    def next_player(self):
        if self.players:
            player = self.players.pop(0)
            self.players.append(player)

    def leaderboard(self):
        current_scores = self.players.copy()
        current_scores.sort(reverse=True, key=lambda x: x.score)
        return current_scores

    def show_scores(self, new_round = True):
        if new_round:
            print("-----------NEW ROUND-----------")
        print("Current Scores:")
        current_scores = self.leaderboard()
        for player in current_scores:
            print(f"{player.name}: {sum(player.score[:self.round - 1])}")
            print(player.score)

    def is_valid_card(self, card):
        if card.lower() in self.deck and self.deck[card.lower()] > 0:
            return True
        else:
            return False
    
    def active_players(self):
        active = []
        for player in self.players:
            if player.active:
                active.append(player)
        return active

    def check_deck(self):
        cards_remaining = 0
        for card in self.deck:
            cards_remaining += self.deck[card]
        if cards_remaining == 0:
            print("Reshuffle all cards not in hand")
            self.deck = self.cards.copy()
            for p in self.players:
                hand_numbers = p.hand.numbers
                for number in hand_numbers:
                    self.deck[str(number)] -= 1
                hand_sc = p.hand.sc
                if hand_sc:
                    self.deck["sc"] -= 1
                hand_additions = p.hand.addition
                for number in hand_additions:
                    self.deck[f"+{str(number)}"] -= 1
                hand_multiplier = p.hand.multiplier
                if hand_multiplier:
                    self.deck["x2"] -= 1

    def choose_player(self, second_chance = False):
        if self.active_players():
            for index, p in enumerate(self.active_players()):
                if second_chance:
                    if p.hand.sc:
                        continue
                print(f"{index + 1}. {p.name}")
            while True:
                target = input("Enter the number of your choice: ")
                if target == "lb":
                    self.show_scores(False)
                try:
                    selection_index = int(target) - 1
                    if 0 <= selection_index < len(self.active_players()):
                        selected_player = self.active_players()[selection_index]
                        break
                    else:
                        print("Invalid selection. Try again.")
                except ValueError:
                    print("Invalid selection. Try again.")
            return selected_player
        return None

    def draw_card(self, user_input, player):
        card = user_input.lower()
        numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        additions = ["+2", "+4", "+6", "+8", "+10"]
        if card in self.deck and self.deck[card] > 0:
            self.deck[card] -= 1
            if card == "fr":
                return self.freeze()
            elif card == "sc":
                return self.second_chance(player)
            elif card == "f3":
                return self.flip_three()
            elif card == "x2":
                player.hand.multiplier = True
            elif card in additions:
                player.hand.addition.append(int(card[1:]))
            elif card in numbers:
                if card in player.hand_list():
                    if player.hand.sc:
                        player.hand.sc = False
                        print("Saved by the second chance card!")
                    else:
                        player.bust()
                        print("Card already in hand. 0 points.")
                else:
                    player.hand.numbers.append(int(card))
        return None

    def second_chance(self, player):
        if player.hand.sc:
            if self.active_players():
                print("Already have one. Choose an active player to give it to: ")
                selected_player = self.choose_player(True)
                if not selected_player:
                    return None
            else:
                print("No active players left without a second chance. Discard the second chance.")
                return None
            selected_player.hand.sc = True
            return selected_player
        else:
            player.hand.sc = True
            return player

    def flip_three(self):
        print("Choose an active player to flip three:")
        selected_player = self.choose_player(False)
        flipped_cards = []
        for i in range(3):
            if selected_player.active:
                user_input = input(f"{selected_player.name}'s Card: ")
                flipped_card = self.draw_card(user_input, selected_player)
                flipped_cards.append(flipped_card)
                self.check_deck()
                if selected_player.check_seven():
                    break
        for x in flipped_cards:
            if selected_player.active:
                if x == "fr":
                    self.freeze()
                elif x == "f3":
                    self.flip_three()
        return selected_player

    def freeze(self):
        print("Choose an active player to freeze:")
        selected_player = self.choose_player(False)
        selected_player.bank()
        return selected_player

    def new_round(self):
        end_game = False
        for player in self.players:
            if int(sum(player.score)) >= 200:
                end_game = True
            player.reset_hand()
            player.active = True
        if not end_game:
            self.round += 1
            self.show_scores()
            return False
        return self.end_game()

    def end_game(self):
        print("_____________________________________")
        print("Final Scores:")
        current_scores = self.leaderboard()
        for player in current_scores:
            print(f"{player.name}: {player.score}")
        if len(current_scores) > 1:
            if current_scores[0] == current_scores[1]:
                print()
                print(f"Tie between {current_scores[0].name} and {current_scores[1].name}")
                print("_____________________________________")
                print()
        else:
            winner = current_scores[0]
            print()
            print(f"Winner: {winner["name"]}")
            print("_____________________________________")
            print()
        return True

def game_round(game):
        while True: # Round Loop
            player = game.current_player()
            if player.active:
                game.check_deck()  # check for an empty deck, if so, reshuffle
                while True: # loop until valid input
                    if game.analytics:
                        user_input = input(f"{player.name} ({player.bust_chance(game.deck)}% bust, {player.expected_value(game.deck)} EV): ")
                    else:
                        user_input = input(f"{player.name}, flip a card or \"b\" for bank: ")
                    if user_input.lower() == "b":
                        player.bank()
                        break
                    elif user_input.lower() == "lb":
                        game.show_scores()
                    else:
                        if game.is_valid_card(user_input):
                            break
                        else:
                            print("Invalid input. Try again.")
                game.draw_card(user_input, player)
                game.next_player()
                if player.check_seven():
                    for player in game.active_players():
                        player.bank()
                if not game.active_players():
                    break
        return game.new_round()

def init(game):
    while True:
        count_input = input("Enter the number of players: ")
        try:
            player_count = int(count_input)
            if player_count > 0:
                break
            else:
                raise ValueError
        except ValueError:
            print("Please enter a positive integer")
    for i in range(int(player_count)):
        name_input = input(f"Player {i + 1} name: ")
        game.add_player(name_input)
    hints = input("Do you want to play with failure percentages visible? (y/n): ")
    if hints.lower() == "y":
        game.set_analytics(True)
    else:
        game.set_analytics(False)


if __name__ == "__main__":
    state = GameState()
    init(state)
    while True:
        game_round(state)