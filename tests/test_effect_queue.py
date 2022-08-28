#%%
import unittest
from functools import partial

import numpy as np

from sapai import *
from sapai.battle import Battle, run_looping_effect_queue
from sapai.graph import graph_battle
from sapai.compress import *

### Remember: Can always graph result with graph_battle(b,verbose=True) to
###   visualize behavior of the run_looping_effect_queue
g = partial(graph_battle, verbose=True)


class TestEffectQueue(unittest.TestCase):
    def test_summon_sob(self):
        ref_team = Team(["pet-zombie-cricket"], battle=True)

        ### Simple sob test for effect loop behavior
        t0 = Team(["cricket"])
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        ref_team[0].obj._attack = 1
        ref_team[0].obj._health = 1
        self.assertEqual(b.t0.state, ref_team.state)

        ### Dolphin should kill cricket, then mosquito has no target, so
        ###   ref_state should remain the same
        t0 = Team(["cricket"])
        t1 = Team(["dolphin", "mosquito"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

        ### Dolphin should kill cricket, then dolphin should hit camel for 5
        ###   leaving it with 1 hp, then mosquito only be able to hit camel
        ###   for 1 leaving only the zombie cricket
        t0 = Team(["cricket", "camel"])
        t1 = Team(["dolphin", "dolphin", "mosquito"])
        t1[2].obj.level = 3
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_blowfish_pingpong(self):
        ref_team = Team(["blowfish"], battle=True)
        ref_team[0].obj._health = 1

        ### Check puffer-fish ping-pong, even though not part of start of
        ### battle it should work if hurt is triggered manufriend
        t0 = Team(["blowfish"])
        t1 = Team(["blowfish"])
        t0[0].obj.hurt(1)
        b = run_sob(t0, t1)
        self.assertEqual(b.t1.state, ref_team.state)

    def test_bee_sob(self):
        ref_team = Team(["pet-bee"], battle=True)
        t0 = Team(["ant"])
        t0[0].obj.eat(Food("honey"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_badger_sob(self):
        """
        Fairly complex example, where badger has honey, friend fish has one-up,
        then dolphin kills badger for sob, badger kills dolphin and fish,
        then bee spawns and one-up fish spawns, all in the correct locations.
        """
        ref_team = Team(["pet-bee", "fish", "fish"], battle=True)
        ref_team[1].obj._attack = 1
        ref_team[1].obj._health = 1

        t0 = Team(["badger", "fish", "fish"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_badger_honey_fly_sob(self):
        """
        Same as above but with fly for friend. Badger and fish should spawn
        their status pets first, then fly should place zombie-flies in the
        correct locations.

        This is a very complex example. All these cases succeed demonstrating
        the validity of the code to replicate the game auto-battle mechanics.
        """
        ref_team = Team(["zombie-fly", "bee", "zombie-fly", "fish", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 4
        ref_team[2].obj._health = 4
        ref_team[3].obj._attack = 1
        ref_team[3].obj._health = 1
        ref_team[4].obj.ability_counter = 2

        t0 = Team(["badger", "fish", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)

        self.assertEqual(b.t0.state, ref_team.state)

        ### Another fish, then ability counter of fly should be only 1
        ref_team = Team(["zombie-fly", "bee", "fish", "fish", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 1
        ref_team[2].obj._health = 1
        ref_team[4].obj.ability_counter = 1
        t0 = Team(["badger", "fish", "fish", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_badger_honey_fly_shark_sob(self):
        """
        Same as above but with shark for friend
        """
        ### Shark should activate twice
        ref_team = Team(["zombie-fly", "bee", "fish", "fly", "shark"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 1
        ref_team[2].obj._health = 1
        ref_team[4].obj._attack = 4 + 4
        ref_team[4].obj._health = 4 + 4
        ref_team[3].obj.ability_counter = 1
        ref_team[4].obj.ability_counter = 2

        t0 = Team(["badger", "fish", "fly", "shark"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t0[1].obj.eat(Food("mushroom"))
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)

        self.assertEqual(b.t0.state, ref_team.state)

    def test_badger_hedgehog(self):
        """
        Badger should kill dolphin and hedgehog, hedgehog's ability should
        activate, the bee should spawn leaving bee as pet left and t0 as winner
        """
        ref_team = Team(["pet-bee"], battle=True)
        t0 = Team(["badger", "hedgehog"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_sheep_fly(self):
        ref_team = Team(["zombie-fly", "bee", "pet-ram", "pet-ram", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[2].obj._attack = 2
        ref_team[2].obj._health = 2
        ref_team[3].obj._attack = 2
        ref_team[3].obj._health = 2
        ref_team[4].obj.ability_counter = 1

        t0 = Team(["sheep", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)

        self.assertEqual(b.t0.state, ref_team.state)

    def test_spider_fly(self):
        ref_team = Team(["zombie-fly", "spider", "turtle", "fly"], battle=True)
        ref_team[0].obj._attack = 4
        ref_team[0].obj._health = 4
        ref_team[1].obj._attack = 1
        ref_team[1].obj._health = 1
        ref_team[1].obj.level = 3
        ### Spider spaws everything at 2/2
        ref_team[2].obj._attack = 2
        ref_team[2].obj._health = 2
        ref_team[2].obj.level = 3
        ref_team[3].obj.ability_counter = 1

        seed_state = np.random.RandomState(seed=3).get_state()
        t0 = Team(["spider", "fly"], seed_state=seed_state)
        t0[0].obj.eat(Food("mushroom"))
        t0[0].obj.level = 3
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)

        self.assertEqual(minimal_state(b.t0), minimal_state(ref_team))

    def test_ox_fly(self):
        ref_team = Team(["bee", "ram", "ram", "ox", "fly"], battle=True)
        ref_team[1].obj._attack = 2
        ref_team[1].obj._health = 2
        ref_team[2].obj._attack = 2
        ref_team[2].obj._health = 2
        ref_team[3].obj._attack = 2
        ref_team[3].obj.ability_counter = 2
        ref_team[3].obj.status = "status-melon-armor"

        t0 = Team(["sheep", "ox", "fly"])
        t0[0].obj.eat(Food("honey"))
        t0[0].obj._health = 1
        t1 = Team(["dolphin"])
        b = run_sob(t0, t1)
        self.assertEqual(b.t0.state, ref_team.state)

    def test_rhino_loop(self):
        pass

    def test_kangaroo_ability(self):
        """
        Ensure that kangaroo ability activates before any hurt or faint triggers

        """

        ### If kangaroo ability doesn't activate first, then it would faint
        ###   from blowfish ability
        t0 = Team(["sheep", "kangaroo"])
        t1 = Team(["blowfish"])
        b = run_sob(t0, t1)

        ### If kangaroo ability doesn't activate first, then it would faint
        ###   from badger faint ability
        t0 = Team(["sheep", "kangaroo"])
        t1 = Team(["badger"])
        b = run_sob(t0, t1)


def run_sob(t0, t1):
    b = Battle(t0, t1)
    phase_dict = {
        "init": [[str(x) for x in b.t0], [str(x) for x in b.t1]],
        "start": {
            "phase_start": [],
        },
    }
    run_looping_effect_queue(
        "sob_trigger",
        ["oteam"],
        b,
        "phase_start",
        [b.t0, b.t1],
        b.pet_priority,
        phase_dict["start"],
    )
    phase_dict["start"]["phase_move_end"] = [
        [
            [str(x) for x in b.t0],
            [str(x) for x in b.t1],
        ]
    ]
    b.battle_history = phase_dict
    return b


def run_attack(t0, t1, run_before=False, finish_battle=False):
    b = Battle(t0, t1)
    phase_dict = {
        "init": [[str(x) for x in b.t0], [str(x) for x in b.t1]],
        "attack 0": {
            "phase_move_start": [],
            "phase_attack": [],
        },
    }


# %%

# seed_state = np.random.RandomState(seed=3).get_state()
# t0 = Team(["spider", "fly"], seed_state=seed_state)
# t0[0].obj.eat(Food("mushroom"))
# t0[0].obj.level = 3
# t0[0].obj._health = 1
# t1 = Team(["dolphin"])
# b = run_sob(t0, t1)

# ref_team = Team(["zombie-fly", "spider", "turtle", "fly"], battle=True)
# ref_team[0].obj._attack = 4
# ref_team[0].obj._health = 4
# ref_team[1].obj._attack = 1
# ref_team[1].obj._health = 1
# ref_team[1].obj.level = 3
# ref_team[2].obj.level = 3
# ref_team[3].obj.ability_counter = 1
# t = minimal_state(b.t0)
# r = minimal_state(ref_team)

# for i in range(len(t["team"])):
#     print(i, t["team"][i] == r["team"][i])

#%%
# ref_team = Team(["bee", "ram", "ram", "ox", "fly"], battle=True)
# ref_team[1].obj._attack = 2
# ref_team[1].obj._health = 2
# ref_team[2].obj._attack = 2
# ref_team[2].obj._health = 2
# ref_team[3].obj._attack = 2
# ref_team[3].obj.ability_counter = 2
# ref_team[3].obj.status = "status-melon-armor"

# t0 = Team(["sheep", "ox", "fly"])
# t0[0].obj.eat(Food("honey"))
# t0[0].obj._health = 1
# t1 = Team(["dolphin"])
# b = run_sob(t0, t1)

# t = b.t0.state
# r = ref_team.state
# for i in range(len(t["team"])):
#     print(i, t["team"][i] == r["team"][i])
# print(b.t0.state == ref_team.state)
# %%


#%%
