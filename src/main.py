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

players = []

quit_count = 0
analytics_visible = False
deck = {}

def init():
    global analytics_visible
    global players
    global deck
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
                    draw_card(p)
                    # CHECK FOR EMPTY DECK
                    reshuffle()
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
    player_numbers = p.get("hand").get("numbers")
    round_score = sum(player_numbers)
    if p.get("hand").get("divider"):
        round_score -= round_score / 2
    player_subtractions = p.get("hand").get("subtraction")
    round_score -= sum(player_subtractions)
    existing_score = p["score"]
    p.__setitem__("score", round_score + existing_score)
    print(f"{p["name"]} scored {round_score} this round. Total: {existing_score + round_score}")

def end_round_turn(p):
    print(f"Ending round for {p["name"]}")
    p.__setitem__("active", False)
    empty_hand = {
        "numbers": [],
        "subtraction": [],
        "divider": False,
        "bonus": False,
        "special": [] # holds reference to u7 and l13
    }
    p.__setitem__("hand", empty_hand)
    global quit_count
    quit_count += 1

def draw_card(p, flip = False):
    if analytics_visible:
        bust_percent = analytics(p)
        print("QUIT") if p["tolerance"] <= bust_percent else None
        user_input = input(f"{p["name"]}, flip a card ({bust_percent}% chance of bust) or \"s\" for stay: ")
    else:
        user_input = input(f"{p["name"]}, flip a card or \"s\" for stay: ")
    if user_input.lower() == 's':
        score(p)
        end_round_turn(p)
        return ""
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
            steal()
            return ""
        elif card.lower() == "discard":
            if flip:
                return "discard"
            discard()
            return ""
        elif card == "u7":
            print("NOT IMPLEMENTED")
            return ""
        elif card == "l13":
            print("NOT IMPLEMENTED")
            return ""
        elif card in numbers:
            if int(card) in p["hand"]["numbers"]:
                #TODO check for l13 in special hand
                print("Card already in hand. 0 points")
                end_round_turn(p)
            else:
                p["hand"]["numbers"].append(int(card))
            return ""
        elif card == "/2":
            p["hand"]["divider"] = True
            return ""
        elif card in subtractions:
            p["hand"]["subtraction"].append(int(card[1:]))
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
    print("Choose an active player to freeze:")
    active_players = []
    for idx, p in enumerate(players):
        if p["status"] == "active" or "stay":
            print(f"{idx + 1}. {p["name"]}")
            active_players += str(idx + 1)
    target = input()
    if target == "lb":
        print_leaderboard(False)
        just_one_more()
        return
    if target in active_players:
        score(players[int(target) - 1])
        end_round_turn(players[int(target) - 1])
    else:
        print("Try again. Not an active player: ")
        just_one_more()

def steal():
    #TODO implement
    print("NOT IMPLEMENTED")

def discard():
    #TODO implement
    print("NOT IMPLEMENTED")

def swap():
    #TODO implement
    print("NOT IMPLEMENTED")

def flip_four():
    print("Choose an active player to flip four:")
    active_players = []
    for idx, p in enumerate(players):
        if p["active"] == "active" or "stay":
            print(f"{idx + 1}. {p["name"]}")
            active_players += str(idx + 1)

    target = input()
    if target == "lb":
        print_leaderboard(False)
        flip_four()
        return
    if target in active_players:
        target_player = players[int(target) - 1]
        remaining_cards = []
        for i in range(3):
            if target_player["active"]:
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
                steal()
            elif x == "discard":
                discard()
            elif x == "f4":
                flip_four()
    else:
        print("Try again. Not an active player: ")
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

def my_func(p):
    return p["score"]

if __name__ == "__main__":
    playing = True
    while playing:
        init()
        main()
