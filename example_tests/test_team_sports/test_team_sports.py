"""
Create a 5 person team intramural high school basketball league
and test interactions

In this league, a team is made of players and coaches.
Players and coaches can belong to only one team.

In this league, a player must be between 14 and 19 years old.
In this league, a coach must be at least 25.

In this league, a team must have exactly 5 main players
and up to 4 substitions.
(Generally speaking, a main player commits to at least 80% of games but that's not tracked here... yet)

In this league, each team has exactly 1 captain who is a main player.

In this league, each player must have a unique combination of first and last name across the whole league.
In this league, each player must have a unique number within a team.
In this league, a team must have a unique name less than 50 characters but more than 5.
"""

import pytest

from faux_sure import not_db
from faux_sure.exceptions import TypeFieldRequirementException, ValidatorFieldRequirementException
from faux_sure.recipes.curries import in_range, max_length, min_length
from faux_sure.recipes.sauces import one_to_one

CURRENT_SCOPE = "example_tests.test_team_sports.test_team_sports"


def class_name(local_class: str):
    return f"{CURRENT_SCOPE}.{local_class}"


class LeagueRulesException(Exception):
    pass


class LeagueRules:
    @staticmethod
    def is_captain(player) -> bool:
        return player.is_captain or False

    @staticmethod
    def player_captain_is_main(player: "Player") -> bool:
        if player.is_captain and not player.is_main:
            raise LeagueRulesException(f"Player {player.first_name + player.last_name} must be a main to be captain")

    @staticmethod
    def unique_player_number_within_team(team: "Team") -> bool:
        """Return True if all players within a team have a unique number on their jersey"""
        all_players = not_db.Session.query_by_type_name("Player")
        team_players = [player for player in all_players if player.team == team]
        unique_jerseys = {player.jersey_number for player in team_players}
        if not len(team_players) == len(unique_jerseys):
            raise LeagueRulesException(f"Not all Players on {team} have a unique number")
        return True

    @staticmethod
    def only_one_captain_per_team(team: "Team") -> bool:
        """Return false if a team has more than one player who is a captain"""
        all_players = not_db.Session.query_by_type_name("Player")
        team_captain = [player for player in all_players if player.team == team and player.is_captain]
        if not len(team_captain) == 1:
            LeagueRulesException(f"{team} has {team_captain} captains")
        return True

    @staticmethod
    def correct_number_of_players(team: "Team") -> bool:
        """True if exactly 5 main players and less than 5 subs"""
        player_types = {True: 0, False: 0}
        all_players = not_db.Session.query_by_type_name("Player")
        for player in all_players:
            player_types[player.is_main] += 1
        if player_types[True] != 5 and player_types[False] > 4:
            LeagueRulesException(f"{team} has {player_types[True]} main players and {player_types[False]} subs")


class Person(not_db.Model):

    first_name = not_db.Field(str)
    last_name = not_db.Field(str)


class Player(Person):
    """A basketball Player"""

    age = not_db.Field(int, in_range(14, 19))
    is_captain = not_db.Field(bool, optional=True)
    is_main = not_db.Field(bool)
    jersey_number = not_db.Field(int, in_range(1, 99))
    team = not_db.Field(class_name("Team"))

    jersey_constraint = not_db.UniqueTogetherRestraint(("first_name", "last_name"))

    def checks(self):
        LeagueRules.player_captain_is_main(self)


class Coach(Person):

    age = not_db.Field(int, in_range(25, None))
    team = not_db.Field(class_name("Team"))


class Team(not_db.Model):

    team_name = not_db.Field(str, (min_length(5), max_length(50)))
    captain = not_db.Field(class_name("Player"), LeagueRules.is_captain)
    coach = not_db.Field(class_name("Coach"))

    name_constraint = not_db.UniqueTogetherRestraint("team_name")

    def checks(self):
        one_to_one(self, "captain", self.captain, "team")
        one_to_one(self, "coach", self.coach, "team")
        LeagueRules.correct_number_of_players(self)
        LeagueRules.only_one_captain_per_team(self)
        LeagueRules.unique_player_number_within_team(self)


LIST_OF_NAMES = [
    ("Johnny", "Silverhands"),
    ("Cool", "Luke"),
    ("Smellya", "Later"),
    ("Jame", ("Bigguy")),
    ("Kobe", "Rip"),
]


def test_type_repl_feedback():
    """Immediately assert error when an incorrect type is set"""

    ace = Player()
    with pytest.raises(TypeFieldRequirementException):
        ace.age = "13"


def test_rule_repl_feedback():
    """Immediately assert error when an invalid value is set"""

    ace = Player()
    with pytest.raises(ValidatorFieldRequirementException, match="age failed to validate in_range_14_to_19"):
        ace.age = 13


def test_good_single_team():

    not_db.Session.reset()

    wolves = Team("Wolves")
    ace = Player()
    ace.first_name = "Ace"
    ace.last_name = "Ventura"
    ace.age = 17
    ace.is_captain = True
    ace.is_main = True
    ace.team = wolves
    ace.jersey = 12
    wolves.captain = ace
    not_db.Session.add(ace)
    not_db.Session.add(wolves)

    other_members = (Player() for _ in range(5))
    for pos, member in enumerate(other_members):
        member.first_name = LIST_OF_NAMES[pos][0]
        member.last_name = LIST_OF_NAMES[pos][1]
        member.age = 17
        member.is_main = pos < 4
        member.team = wolves
        member.jersey_number = 27 + pos ** 2
        not_db.Session.add(member)

    coach = Coach()
    coach.first_name = "Coach"
    coach.last_name = "Mann"
    coach.age = 46
    coach.team = wolves
    wolves.coach = coach
    not_db.Session.add(coach)

    not_db.Session.commit()

    assert len(list(not_db.Session.query_by_type_name("Player"))) == 6
    assert len(list(not_db.Session.query_by_type_name("Team"))) == 1
    assert len(list(not_db.Session.query_by_type_name("Coach"))) == 1
