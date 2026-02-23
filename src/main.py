CARDS = {
    "0": 1,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 6,
    "u7": 1,
    "8": 8,
    "9": 9,
    "10": 10,
    "11": 11,
    "12": 12,
    "13": 12,
    "l13": 1,
    "jom": 2,
    "f4": 2,
    "swap": 2,
    "steal": 2,
    "discard": 2,
    "-2": 1,
    "-4": 1,
    "-6": 1,
    "-8": 1,
    "-10": 1,
    "/2": 1
}
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
SUBTRACTIONS = ["-2", "-4", "-6", "-8", "-10"]
players = []

quit_count = 0
analytics_visible = False
deck = {}
import random
random.choice(NUMBERS)

def init():
    global analytics_visible
    global players
    global deck
    # players = [
    #     {
    #         "id": 1,
    #         "status": "active",  # active, stay, bust
    #         "hand": {
    #             "numbers": [],
    #             "subtraction": [],
    #             "divider": False,
    #             "bonus": False,
    #             "special": []  # holds reference to u7 and l13
    #         },
    #         "name": "Isaac",
    #         "score": 0,
    #         "tolerance": 100
    #     },
    #     {
    #         "id": 2,
    #         "status": "active",  # active, stay, bust
    #         "hand": {
    #             "numbers": [],
    #             "subtraction": [],
    #             "divider": False,
    #             "bonus": False,
    #             "special": []  # holds reference to u7 and l13
    #         },
    #         "name": "Andrew",
    #         "score": 0,
    #         "tolerance": 100
    #     },
    #     {
    #         "id": 3,
    #         "status": "active",  # active, stay, bust
    #         "hand": {
    #             "numbers": [],
    #             "subtraction": [],
    #             "divider": False,
    #             "bonus": False,
    #             "special": []  # holds reference to u7 and l13
    #         },
    #         "name": "Grace",
    #         "score": 0,
    #         "tolerance": 100
    #     }
    # ]
    players = []
    deck = CARDS.copy()
    number_of_players = input("Enter the number of players: ")
    for i in range(int(number_of_players)):
        player_name = input(f"Player {i + 1} name: ")
        player = {
            "id": i + 1,
            "status": "active", #active, stay, bust
            "hand": {
                "numbers": [],
                "subtraction": [],
                "divider": False,
                "bonus": False,
                "special": [] # holds reference to u7 and l13
            },
            "name": player_name,
            "score": 0,
            "tolerance": 100
        }
        players.append(player)
    
    hints = input("Do you want to play with failure percentages visible? (y/n): ")
    if hints.lower() == "y":
        analytics_visible = True
    else:
        analytics_visible = False
    print()
    print()
    print("For each turn, input the following and click enter:")
    print("  - For number cards, just type the number: 4")
    print("  - For score modifier cards, type either a \"-\" or an \"/\" (without quotes) and then the number: -10 or /2")
    print("  - For action cards, type the following: ")
    print("    - Just One More: jom")
    print("    - Flip Four: f4")
    print("    - Swap: swap")
    print("    - Steal: steal")
    print("    - Discard: discard")
    print("  - To stay, type: s")
    print()
    print("*For Action cards, you must type the number of a non-busted player to apply the action to")
    print()
    print()
    analytics_visible = False

def main():
    global playing
    global analytics_visible
    global quit_count
    game = True
    next_player = 0

    while game:
        current_round = True
        while current_round:
            for idx, p in enumerate(players):
                if p.get("status") == "active":
                    card = draw_card(p)
                    # CHECK FOR EMPTY DECK
                    reshuffle()
                    if card != "stay":
                        next_player = idx + 1
                    player_hand = p.get("hand").get("numbers")
                    if len(player_hand) >= 7:
                        p["hand"]["bonus"] = True
                        current_round = False
                        for player in players:
                            score(player)
                            end_round_turn(player)
                        break
                    
                if quit_count >= len(players):
                    current_round = False
                    break
        for i in range(next_player):
            player = players.pop(0)
            players.append(player)
        print_leaderboard()
        quit_count = 0
        for p in players:
            p["status"] = "active"
            if p["score"] >= 200:
                game = False
                break
    print("_____________________________________")
    print("Final Scores:")
    current_scores = players.copy()
    current_scores.sort(reverse=True, key=my_func)
    for p in current_scores:
        print(f"{p["name"]}: {p["score"]}")
    winner = current_scores[0]
    print()
    print(f"Winner: {winner["name"]}")
    print("_____________________________________")
    print()
    again = input("Play again? (y/n): ")
    if again.lower() != "y":
        playing = False


def print_leaderboard(new = True):
    if new:
        print("-----------NEW ROUND-----------")
    print("Current Scores:")
    current_scores = players.copy()
    current_scores.sort(reverse=True, key=my_func)
    for p in current_scores:
        print(f"{p["name"]}: {p["score"]}")


def reshuffle(in_play=None):
    if in_play is None:
        in_play = []
    global deck
    cards_remaining = 0
    for card in deck:
        cards_remaining += deck[card]
    if cards_remaining == 0:
        print("Reshuffle all cards not in hand")
        deck = CARDS.copy()
        for card in in_play:
            deck[card] -= 1
        for p in players:
            hand_special = p["hand"]["special"]
            hand_numbers = p["hand"]["numbers"]
            for number in hand_special:
                if number == "u7":
                    for i in hand_numbers:
                        if i == "7":
                            hand_numbers.remove(i)
                            break
                elif number == "l13":
                    for i in hand_numbers:
                        if i == "13":
                            hand_numbers.remove(i)
                            break
            for number in hand_numbers:
                deck[str(number)] -= 1
            hand_subtractions = p["hand"]["subtraction"]
            for number in hand_subtractions:
                deck[f"-{str(number)}"] -= 1
            hand_divider = p["hand"]["divider"]
            if hand_divider:
                deck["/2"] -= 1

def score(p):
    player_numbers = p["hand"]["numbers"]
    round_score = sum(player_numbers)
    if 14 in player_numbers:
        round_score -= 1
    if p.get("hand").get("divider"):
        round_score -= round_score / 2
    subtractions = []
    for number in p["hand"]["subtraction"]:
        subtractions.append(int(number[1:]))
    round_score -= sum(subtractions)
    existing_score = p["score"]
    if 0 in player_numbers and len(player_numbers) < 7:
        round_score = 0
    p["score"] = round_score + existing_score
    print(f"{p["name"]} scored {round_score} this round. Total: {existing_score + round_score}")

def end_round_turn(p):
    print(f"Ending round for {p["name"]}")
    p["status"] = "bust"
    empty_hand = {
        "numbers": [],
        "subtraction": [],
        "divider": False,
        "bonus": False,
        "special": [] # holds reference to u7 and l13
    }
    p["hand"] = empty_hand
    global quit_count
    quit_count += 1

def draw_card(p, flip = False, force = False):
    if analytics_visible:
        bust_percent = analytics(p)
        print("QUIT") if p["tolerance"] <= bust_percent else None
        user_input = input(f"{p["name"]}, flip a card ({bust_percent}% chance of bust) or \"s\" for stay: ")
    else:
        user_input = input(f"{p["name"]}, flip a card or \"s\" for stay: ")
    if not force:
        if user_input.lower() == 's':
            score(p)
            end_round_turn(p)
            return "stay"
    if user_input.lower() == 'lb':
        print_leaderboard(False)
        draw_card(p, flip)
        return ""
    card = user_input.lower()
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]
    subtractions = ["-2", "-4", "-6", "-8", "-10"]
    if card in deck and deck[card] > 0:
        deck[card] -= 1
        if card.lower() == "jom":
            if flip:
                return "jom"
            just_one_more()
            return ""
        elif card.lower() == "swap":
            if flip:
                return "swap"
            swap()
            return ""
        elif card.lower() == "steal":
            if flip:
                return "steal"
            steal(p)
            return ""
        elif card.lower() == "discard":
            if flip:
                return "discard"
            discard()
            return ""
        elif card == "u7":
            empty_hand = {
                "numbers": [],
                "subtraction": [],
                "divider": False,
                "bonus": False,
                "special": []  # holds reference to u7 and l13
            }
            p["hand"] = empty_hand
            p["hand"]["numbers"].append(int(7))
            p["hand"]["special"].append("u7")
            return ""
        elif card == "l13":
            p["hand"]["numbers"].append(13)
            p["hand"]["special"].append("l13")
            return ""
        elif card in numbers:
            if int(card) in p["hand"]["numbers"]:
                if card == "13" and ("l13" in p["hand"]["special"]):
                    count = 0
                    for i in p["hand"]["numbers"]:
                        if i == 13:
                            count += 1
                    if count <= 1:
                        p["hand"]["numbers"].append(int(13))
                        return ""
                print("Card already in hand. 0 points")
                end_round_turn(p)
            else:
                p["hand"]["numbers"].append(int(card))
            return ""
        elif card == "/2":
            target_player = choose_player()
            target_player["hand"]["divider"] = True
            return ""
        elif card in subtractions:
            target_player = choose_player()
            target_player["hand"]["subtraction"].append(card)
            return ""
        elif card == "f4":
            if flip:
                return "f4"
            flip_four()
            return ""
        return ""

    else:
        if card not in deck:
            print("Try again. Card is not valid.")
        elif deck[card] <= 0:
            print(f"Try again. No more {card}'s in deck.")
        else:
            print("Try again.")
        draw_card(p)
        return ""

def just_one_more():
    print("Choose a player to freeze:")
    target_player = choose_player()
    draw_card(target_player, force = True)
    score(target_player)
    end_round_turn(target_player)

def steal(player):
    if not check_active_players():
        print("No active players")
        return None

    print("Choose a card to steal:")
    target_player = choose_player()
    if (target_player["status"] == "active") and (target_player != player):
        active_cards = []
        for card in target_player["hand"]["subtraction"]:
            active_cards.append(card)
        if target_player["hand"]["divider"]:
            active_cards.append("/2")
        special = target_player["hand"]["special"]
        for card in special:
            active_cards.append(card)
        numbers = target_player["hand"]["numbers"]
        if len(special) > 0:
            for card in special:
                for num in numbers:
                    if card == "u7":
                        if num == 7:
                            numbers.remove(num)
                            break
                    if card == "l13":
                        if num == 13:
                            numbers.remove(num)
                            break
        for card in numbers:
            active_cards.append(str(card))
        print(f"What card will you steal? {active_cards}")
        target_card = input()

        if target_card in active_cards:
            if target_card == "u7":
                target_player["hand"]["special"].remove(target_card)
                target_player["hand"]["numbers"].remove(7)
                player["hand"]["numbers"] = []
                player["hand"]["subtraction"] = []
                player["hand"]["divider"] = False
                player["hand"]["special"] = []
                player["hand"]["special"].append(target_card)
                player["hand"]["numbers"].append(7)
            elif target_card == "l13":
                target_player["hand"]["special"].remove(target_card)
                target_player["hand"]["numbers"].remove(13)
                player["hand"]["special"].append(target_card)
                player["hand"]["numbers"].append(13)
            elif target_card in NUMBERS:
                target_player["hand"]["numbers"].remove(int(target_card))
                player["hand"]["numbers"].append(int(target_card))
            elif target_card in SUBTRACTIONS:
                target_player["hand"]["subtraction"].remove(target_card)
                player["hand"]["subtraction"].append(target_card)
            elif target_card == "/2":
                target_player["hand"]["divider"] = False
                player["hand"]["divider"] = True
        else:
            return steal(player)
    else:
        return steal(player)
    return None

def check_active_players():
    active_players = []
    for p in players:
        if p["status"] == "active" or "stay":
            active_players.append(p)
    return len(active_players)

def check_active_cards():
    active_cards = []
    active_players = []
    for p in players:
        if p["status"] == "active" or "stay":
            active_players.append(p)
    for p in active_players:
        for card in p["hand"]["subtraction"]:
            active_cards.append(card)
        if p["hand"]["divider"]:
            active_cards.append("/2")
        special = p["hand"]["special"]
        numbers = p["hand"]["numbers"]
        if len(special) > 0:
            for card in special:
                for num in numbers:
                    if card == "u7":
                        if num == 7:
                            numbers.remove(num)
                            break
                    if card == "l13":
                        if num == 13:
                            numbers.remove(num)
                            break
        for card in numbers:
            active_cards.append(str(card))
    return len(active_cards)

def discard():
    if not check_active_players():
        print("No active players")
        return None

    print("Choose a player to make discard a card:")
    target_player = choose_player()
    if target_player["status"] == "active":
        active_cards = []
        for card in target_player["hand"]["subtraction"]:
            active_cards.append(card)
        if target_player["hand"]["divider"]:
            active_cards.append("/2")
        special = target_player["hand"]["special"]
        for card in special:
            active_cards.append(card)
        numbers = target_player["hand"]["numbers"]
        if len(special) > 0:
            for card in special:
                for num in numbers:
                    if card == "u7":
                        if num == 7:
                            numbers.remove(num)
                            break
                    if card == "l13":
                        if num == 13:
                            numbers.remove(num)
                            break
        for card in numbers:
            active_cards.append(str(card))
        print(f"What card will you discard? {active_cards}")
        target_card = input()

        if target_card in active_cards:
            if target_card == "u7":
                target_player["hand"]["special"].remove(target_card)
                target_player["hand"]["numbers"].remove(7)
            elif target_card == "l13":
                target_player["hand"]["special"].remove(target_card)
                target_player["hand"]["numbers"].remove(13)
            elif target_card in NUMBERS:
                target_player["hand"]["numbers"].remove(int(target_card))
            elif target_card in SUBTRACTIONS:
                target_player["hand"]["subtraction"].remove(target_card)
            elif target_card == "/2":
                target_player["hand"]["divider"] = False
        return True
    return None

def swap():
    if check_active_players() <= 1 or check_active_cards() <= 1:
        print("Discard")
        return None

    print("Choose two players to swap a card:")
    target_player_1 = choose_player()
    target_player_2 = choose_player()
    if target_player_1["status"] and target_player_2["status"] == "active" or "stay":
        active_cards = []
        for card in target_player_1["hand"]["subtraction"]:
            active_cards.append(card)
        if target_player_1["hand"]["divider"]:
            active_cards.append("/2")
        special = target_player_1["hand"]["special"]
        for card in special:
            active_cards.append(card)
        numbers = target_player_1["hand"]["numbers"]
        if len(special) > 0:
            for card in special:
                for num in numbers:
                    if card == "u7":
                        if num == 7:
                            numbers.remove(num)
                            break
                    if card == "l13":
                        if num == 13:
                            numbers.remove(num)
                            break
        for card in numbers:
            active_cards.append(str(card))
        for card in target_player_2["hand"]["subtraction"]:
            active_cards.append(card)
        if target_player_2["hand"]["divider"]:
            active_cards.append("/2")
        special = target_player_2["hand"]["special"]
        for card in special:
            active_cards.append(card)
        numbers = target_player_2["hand"]["numbers"]
        if len(special) > 0:
            for card in special:
                for num in numbers:
                    if card == "u7":
                        if num == 7:
                            numbers.remove(num)
                            break
                    if card == "l13":
                        if num == 13:
                            numbers.remove(num)
                            break
        for card in numbers:
            active_cards.append(str(card))
        print(f"What card will {target_player_1["name"]} give up? {active_cards}")
        target_card_1 = input()
        print(f"What card will {target_player_2["name"]} give up? {active_cards}")
        target_card_2 = input()


        if target_card_1 and target_card_2 in active_cards:
            if target_card_1 == "u7":
                target_player_1["hand"]["special"].remove(target_card_1)
                target_player_1["hand"]["numbers"].remove(7)
                target_player_2["hand"]["numbers"] = []
                target_player_2["hand"]["subtraction"] = []
                target_player_2["hand"]["divider"] = False
                target_player_2["hand"]["special"] = []
                target_player_2["hand"]["special"].append(target_card_1)
                target_player_2["hand"]["numbers"].append(7)
            elif target_card_1 == "l13":
                target_player_1["hand"]["special"].remove(target_card_1)
                target_player_1["hand"]["numbers"].remove(13)
                target_player_2["hand"]["numbers"].append(int(13))
                target_player_2["hand"]["special"].append(target_card_1)
            elif target_card_1 in NUMBERS:
                target_player_1["hand"]["numbers"].remove(int(target_card_1))
                target_player_2["hand"]["numbers"].append(int(target_card_1))
            elif target_card_1 in SUBTRACTIONS:
                target_player_1["hand"]["subtraction"].remove(target_card_1)
                target_player_2["hand"]["subtraction"].append(int(target_card_1))
            elif target_card_1 == "/2":
                target_player_1["hand"]["divider"] = False
                target_player_2["hand"]["divider"] = True

            if target_card_2 == "u7":
                target_player_2["hand"]["special"].remove(target_card_1)
                target_player_2["hand"]["numbers"].remove(7)
                target_player_1["hand"]["numbers"] = []
                target_player_1["hand"]["subtraction"] = []
                target_player_1["hand"]["divider"] = False
                target_player_1["hand"]["special"] = []
                target_player_1["hand"]["special"].append(target_card_1)
                target_player_1["hand"]["numbers"].append(7)
            elif target_card_2 == "l13":
                target_player_2["hand"]["special"].remove(target_card_1)
                target_player_2["hand"]["numbers"].remove(13)
                target_player_1["hand"]["numbers"].append(int(13))
                target_player_1["hand"]["special"].append(target_card_1)
            elif target_card_1 in NUMBERS:
                target_player_2["hand"]["numbers"].remove(int(target_card_1))
                target_player_1["hand"]["numbers"].append(int(target_card_1))
            elif target_card_1 in SUBTRACTIONS:
                target_player_2["hand"]["subtraction"].remove(target_card_1)
                target_player_1["hand"]["subtraction"].append(int(target_card_1))
            elif target_card_1 == "/2":
                target_player_2["hand"]["divider"] = False
                target_player_1["hand"]["divider"] = True
        return True
    return None

def flip_four():
    print("Choose an active player to flip four:")
    target_player = choose_player()
    remaining_cards = []
    for i in range(4):
        if target_player["status"] == ("active" or "stay"):
            print(f"{target_player["name"]}'s Card: ")
            flipped_card = draw_card(target_player, True)
            remaining_cards.append(flipped_card)
            reshuffle()
            if len(target_player["hand"]["numbers"]) >= 7:
                target_player["hand"]["addition"].append(15)
                for player in players:
                    score(player)
                    end_round_turn(player)
                break
    for x in remaining_cards:
        if x == "jom":
            just_one_more()
        elif x == "swap":
            swap()
        elif x == "steal":
            steal(target_player)
        elif x == "discard":
            discard()
        elif x == "f4":
            flip_four()

def analytics(p):
    cards_remaining = 0
    bust_cards = 0
    for card in deck:
        cards_remaining += deck[card]
    for card in p["hand"]["numbers"]:
        bust_cards += deck[str(card)]
    percentage = round((bust_cards / cards_remaining) * 100, 2)
    return percentage

def choose_player():
    active_players = []
    # Print list of active players
    for idx, p in enumerate(players):
        if p["status"] == ("active" or "stay"):
            print(f"{idx + 1}. {p["name"]}")
            active_players += str(idx + 1)
    # Choose the player
    target = input()
    if target == "lb":
        print_leaderboard(False)
    if target in active_players:
        return players[int(target) - 1]
    else:
        print("Try again. Not an active player: ")
        choose_player()
        return None

def my_func(p):
    return p["score"]

if __name__ == "__main__":
    playing = True
    while playing:
        init()
        main()
