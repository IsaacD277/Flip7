from src.main import score

class TestScoring:
    def test_score_basic(self):
        """
        Testing with just number cards
        """
        example_player = {
            "id": 1,
            "active": True,
            "hand": {
                "numbers": [0, 9, 4, 6, 3],
                "addition": [],
                "multiplier": False,
                "sc": False
            },
            "name": "Bob",
            "score": 0,
            "tolerance": 100
        }
        player_score = score(example_player)
        print(player_score)
        assert example_player["score"] == 22

    def test_score_advanced(self):
        """
        Testing with number cards, addition cards, and a multiplier
        """
        example_player = {
            "id": 1,
            "active": True,
            "hand": {
                "numbers": [10, 9, 4],
                "addition": [+6],
                "multiplier": True,
                "sc": False
            },
            "name": "Bob",
            "score": 0,
            "tolerance": 100
        }
        player_score = score(example_player)
        print(player_score)
        assert example_player["score"] == 52
