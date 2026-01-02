# Flip 7
Play along with a game of Flip 7 to easily keep track of player scores, as well as determine your chances of busting with each draw.

Based on the game [Flip 7](https://theop.games/products/flip-7?srsltid=AfmBOoqKFcSsXR_gzwPF5m0WmrJCndbbAC45NuzLV37Fk3iATaWGR_9T), but not in any way affiliated with the OP Games.

This game is played in the console and only requires python to be installed.

## Getting Started
1. Open the flip7.py file with python
2. Select the number of players
3. Input their names in turn order
4. Choose whether you want to "cheat" and see your chances of busting each turn
5. BEGIN!

There are a couple different inputs based on the type of card:
- For number cards, just type the number: 4
- For score modifier cards, type either a "+" or an "x" (without quotes) and then the number: +10 or x2
- For action cards, type the following:
    - Second Chance: sc
    - *Freeze: fr
    - *Flip Three: f3
- To bank points, type: b

\*For Freeze and Flip Three, you must type the number of an active player to apply the action to

At the end of each round (7 cards in a players hand or no remaining active players), the scores will show in a leaderboard and the next round will begin!
Pay attention to the player name at the beginning of each turn to ensure each player's score is accurate.

The game will let you know to shuffle the deck when there are no cards left (if you run out of cards and the game doesn't tell you to reshuffle...you are probably missing a card, look around for any cards not included in the deck).

If you know you are missing a card from your physical deck, you will need to edit the CARDS variable within the Python file to match what you actually have.
