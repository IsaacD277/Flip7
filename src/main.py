CARDS = {
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

players = []

quitCount = 0
analyticsVisible = False
deck = {}

def init():
    global analyticsVisible
    global players
    global deck
    players = []
    deck = CARDS.copy()
    numberOfPlayers = input("Enter the number of players: ")
    for i in range(int(numberOfPlayers)):
        playerName = input(f"Player {i + 1} name: ")
        player = {
            "id": i + 1,
            "active": True,
            "hand": {
                "numbers": [],
                "addition": [],
                "multiplier": False,
                "sc": False
            },
            "name": playerName,
            "score": 0,
            "tolerance": 100
        }
        players.append(player)
    
    hints = input("Do you want to play with failure percentages visible? (y/n): ")
    if hints.lower() == "y":
        analyticsVisible = True
    else:
        analyticsVisible = False
    print()
    print()
    print("For each turn, input the following and click enter:")
    print("  - For number cards, just type the number: 4")
    print("  - For score modifier cards, type either a \"+\" or an \"x\" (without quotes) and then the number: +10 or x2")
    print("  - For action cards, type the following: ")
    print("    - Second Chance: sc")
    print("    - *Freeze: fr")
    print("    - *Flip Three: f3")
    print("  - To bank points, type: b")
    print()
    print("*For Freeze and Flip Three, you must type the number of an active player to apply the action to")
    print()
    print()

def main():
    global playing
    global analyticsVisible
    global quitCount
    game = True
    nextPlayer = 0

    while game:
        round = True
        print_leaderboard()

        while round:
            for idx, p in enumerate(players):
                if p.get("active"):
                    drawCard(p)
                    # CHECK FOR EMPTY DECK
                    reshuffle()
                    nextPlayer = idx + 1
                    playerHand = p.get("hand").get("numbers")
                    if len(playerHand) >= 7:
                        p["hand"]["addition"].append(15)
                        round = False
                        for player in players:
                            score(player)
                            endRoundTurn(player)
                        break
                    
                if quitCount >= len(players):
                    round = False
                    break
        for i in range(nextPlayer):
            player = players.pop(0)
            players.append(player)

        quitCount = 0
        for p in players:
            p["active"] = True
            if p["score"] >= 200:
                game = False
                break
    print("_____________________________________")
    print("Final Scores:")
    currentScores = players.copy()
    currentScores.sort(reverse=True, key=myFunc) 
    for p in currentScores:
        print(f"{p["name"]}: {p["score"]}")
    winner = currentScores[0]
    print()
    print(f"Winner: {winner["name"]}")
    print("_____________________________________")
    print()
    again = input("Play again? (y/n): ")
    if again.lower() == "y":
        game = True
    else:
        playing = False


def print_leaderboard(new = True):
    if new:
        print("-----------NEW ROUND-----------")
    print("Current Scores:")
    currentScores = players.copy()
    currentScores.sort(reverse=True, key=myFunc)
    for p in currentScores:
        print(f"{p["name"]}: {p["score"]}")


def reshuffle():
    global deck
    cardsRemaining = 0
    for card in deck:
        cardsRemaining += deck[card]
    if cardsRemaining == 0:
        print("Reshuffle all cards not in hand")
        deck = CARDS.copy()
        for p in players:
            handNumbers = p["hand"]["numbers"]
            for number in handNumbers:
                deck[str(number)] -= 1
            handSC = p["hand"]["sc"]
            if handSC:
                deck["sc"] -= 1
            handAdditions = p["hand"]["addition"]
            for number in handAdditions:
                deck[f"+{str(number)}"] -= 1
            handMultiplier = p["hand"]["multiplier"]
            if handMultiplier:
                deck["x2"] -= 1

def score(p):
    playerNumbers = p.get("hand").get("numbers")
    score = sum(playerNumbers)
    if p.get("hand").get("multiplier"):
        score += score
    playerAdditions = p.get("hand").get("addition")
    score += sum(playerAdditions)
    existingScore = p["score"]
    p.__setitem__("score", score + existingScore)
    print(f"{p["name"]} scored {score} this round. Total: {existingScore + score}")

def endRoundTurn(p):
    print(f"Ending round for {p["name"]}")
    p.__setitem__("active", False)
    emptyHand = {
        "numbers": [],
        "addition": [],
        "multiplier": False,
        "sc": False
    }
    p.__setitem__("hand", emptyHand)
    global quitCount
    quitCount += 1

def drawCard(p, flip = False):
    if analyticsVisible:
        bustPercent = analytics(p)
        print("QUIT") if p["tolerance"] <= bustPercent else None
        userInput = input(f"{p["name"]}, flip a card ({bustPercent}% chance of bust) or \"b\" for bank: ")
    else:
        userInput = input(f"{p["name"]}, flip a card or \"b\" for bank: ")
    if userInput.lower() == 'b':
        score(p)
        endRoundTurn(p)
        return
    if userInput.lower() == 'lb':
        print_leaderboard(False)
        drawCard(p, flip)
        return
    card = userInput.lower()
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    additions = ["+2", "+4", "+6", "+8", "+10"]
    if card in deck and deck[card] > 0:
        deck[card] -= 1
        if card == "fr":
            if flip:
                return "fr"
            freeze()
        elif card == "sc":
            secondChance(p)
        elif card in numbers:
            if int(card) in p["hand"]["numbers"]:
                if p["hand"]["sc"] == True:
                    p["hand"]["sc"] = False
                    print("Saved by the second chance card!")
                else:
                    print("Card already in hand. 0 points")
                    endRoundTurn(p)
            else:
                p["hand"]["numbers"].append(int(card))
        elif card == "x2":
            p["hand"]["multiplier"] = True
        elif card in additions:
            p["hand"]["addition"].append(int(card[1:]))
        elif card == "f3":
            if flip:
                return "f3"
            flipThree()
            
    else:
        if card not in deck:
            print("Try again. Card is not valid.")
        elif deck[card] <= 0:
            print(f"Try again. No more {card}'s in deck.")
        else:
            print("Try again.")
        drawCard(p)
def secondChance(player):
    if player["hand"]["sc"] == True:
        print("Already have one. Choose an active player to give it to: ")
        activePlayers = []
        for p in players:
            if p["active"] == True and p["hand"]["sc"] == False:
                print(f"{p["id"]}. {p["name"]}")
                activePlayers.append(p["id"])
        if activePlayers == []:
            print("No active players left without a second chance. Discard the second chance.")
        target = input()
        if target == "lb":
            print_leaderboard(False)
            secondChance(player)
            return
        if int(target) in activePlayers:
            for p in players:
                if p["id"] == int(target):
                    p["hand"]["sc"] = True
                    return
        else:
            print("Try again. Not an active player: ")
            secondChance(player)
    player["hand"]["sc"] = True

def freeze():
    print("Choose an active player to freeze:")
    activePlayers = []
    for idx, p in enumerate(players):
        if p["active"] == True:
            print(f"{idx + 1}. {p["name"]}")
            activePlayers += str(idx + 1)
    target = input()
    if target == "lb":
        print_leaderboard(False)
        freeze()
        return
    if target in activePlayers:
        score(players[int(target) - 1])
        endRoundTurn(players[int(target) - 1])
    else:
        print("Try again. Not an active player: ")
        freeze()

def flipThree():
    print("Choose an active player to flip three:")
    activePlayers = []
    for idx, p in enumerate(players):
        if p["active"] == True:
            print(f"{idx + 1}. {p["name"]}")
            activePlayers += str(idx + 1)

    target = input()
    if target == "lb":
        print_leaderboard(False)
        flipThree()
        return
    if target in activePlayers:
        targetPlayer = players[int(target) - 1]
        remainingCards = []
        for i in range(3):
            if targetPlayer["active"]:
                print(f"{targetPlayer["name"]}'s Card: ")
                flippedCard = drawCard(targetPlayer, True)
                remainingCards.append(flippedCard)
                reshuffle()
                if len(targetPlayer["hand"]["numbers"]) >= 7:
                    targetPlayer["hand"]["addition"].append(15)
                    round = False
                    for player in players:
                        score(player)
                        endRoundTurn(player)
                    break
        for x in remainingCards:
            if x == "fr":
                freeze()
            elif x == "f3":
                flipThree()
    else:
        print("Try again. Not an active player: ")
        flipThree()

def analytics(p):
    cardsRemaining = 0
    bustCards = 0
    if p["hand"]["sc"] == True:
        return 0.0
    for card in deck:
        cardsRemaining += deck[card]
    for card in p["hand"]["numbers"]:
        bustCards += deck[str(card)]
    percentage = round(((bustCards) / cardsRemaining) * 100, 2)
    return percentage

def myFunc(p):
    return p["score"]

if __name__ == "__main__":
    playing = True
    while playing:
        init()
        main()
