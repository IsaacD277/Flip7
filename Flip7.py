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
            "active": True,
            "hand": {
                "numbers": [],
                "addition": [],
                "multiplier": False,
                "sc": 0
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

def main():
    global playing
    global analyticsVisible
    global quitCount
    game = True
    nextplayer = 0

    while game:
        round = True
        print("-----------NEW ROUND-----------")
        print("Current Scores:")
        currentScores = players.copy()
        currentScores.sort(reverse=True, key=myFunc) 
        for p in currentScores:
            print(f"{p["name"]}: {p["score"]}")

        while round:
            for idx, p in enumerate(players):
                if p.get("active"):
                    if analyticsVisible:
                        bustPercent = analytics(p)
                        print("QUIT") if p["tolerance"] <= bustPercent else None
                        userInput = input(f"{p["name"]}, flip a card ({bustPercent}% chance of bust) or \"q\" for quit: ")
                    else:
                        userInput = input(f"{p["name"]}, flip a card or \"q\" for quit: ")
                    if userInput.lower() == 'q':
                        score(p)
                        endRoundTurn(p)
                    else:
                        drawCard(userInput, p)
                        # CHECK FOR EMPTY DECK
                        reshuffle()
                        nextplayer = idx + 1
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
        
        for i in range(nextplayer):
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
    scores = {}
    for p in players:
        scores[p["score"]] = p["name"]
        print(f"{p["name"]}: {p["score"]}")
    winner = next(iter(dict(sorted(scores.items(), reverse=True)).values()))
    print()
    print(f"Winner: {winner}")
    print("_____________________________________")
    print()
    again = input("Play again? (y/n): ")
    if again.lower() == "y":
        game = True
    else:
        playing = False

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
            deck["sc"] -= handSC
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
        "sc": 0
    }
    p.__setitem__("hand", emptyHand)
    global quitCount
    quitCount += 1

def drawCard(card, p):
    numbers = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    additions = ["+2", "+4", "+6", "+8", "+10"]
    if card in deck and deck[card] > 0:
        deck[card] -= 1
        if card == "fr":
            print("Choose an active player:")
            for idx, p in enumerate(players):
                if p["active"] == True:
                    print(f"{idx + 1}. {p["name"]}")

            target = input()
            score(players[int(target) - 1])
            endRoundTurn(players[int(target) - 1])
        elif card == "sc":
            p["hand"]["sc"] += 1
        elif card in numbers:
            if int(card) in p["hand"]["numbers"]:
                if p["hand"]["sc"] != 0:
                    p["hand"]["sc"] -= 1
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
            print("Choose an active player:")
            for idx, p in enumerate(players):
                if p["active"] == True:
                    print(f"{idx + 1}. {p["name"]}")

            target = input()
            targetPlayer = players[int(target) - 1]
            for i in range(3):
                if targetPlayer["active"]:
                    newCard = input(f"{targetPlayer["name"]}'s Card: ")
                    drawCard(newCard, targetPlayer)
                    reshuffle()
                    if len(targetPlayer["hand"]["numbers"]) >= 7:
                        targetPlayer["hand"]["addition"].append(15)
                        round = False
                        for player in players:
                            score(player)
                            endRoundTurn(player)
                        break
    else:
        if card not in deck:
            newCard = input("Try again. Card is not valid: ")
        elif deck[card] <= 0:
            newCard = input(f"Try again. No more {card}'s in deck: ")
        else:
            newCard = input("Try again: ")
        drawCard(newCard, p)

def analytics(p):
    cardsRemaining = 0
    bustCards = 0
    if p["hand"]["sc"] > 0:
        return 0
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