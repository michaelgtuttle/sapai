import unittest

from sapai import *
from sapai.shop import *


class TestShop(unittest.TestCase):

    def test_shop_slot_pet(self):
        slot = ShopSlot("pet")
        slot.item = Pet("ant")
        slot.roll()
        self.assertIsInstance(slot.item, Pet)

    def test_shop_slot_food(self):
        slot = ShopSlot("food")
        slot.item = Food("apple")
        slot.roll()
        self.assertIsInstance(slot.item, Food)

    def test_shop_level_up(self):
        slot = ShopSlot("levelup")
        tier = slot.item.tier
        self.assertEqual(tier, 2)

    def test_max_shop(self):
        s = Shop(turn=11)
        s.freeze(0)
        for index in range(10):
            s.roll()

    def test_rabbit_buy_food(self):
        test_player = Player(shop=["honey"], team=["rabbit"])
        start_health = 2
        self.assertEqual(test_player.team[0].pet.health, start_health)

        test_player.buy_food(0, 0)
        expected_end_health = start_health + 1
        self.assertEqual(test_player.team[0].pet.health, expected_end_health)

    def test_empty_shop_from_state(self):
        pet = Pet("fish")
        orig_shop = Shop(shop_slots=[pet])
        orig_shop.buy(pet)
        self.assertEqual(len(orig_shop.shop_slots), 0)

        copy_shop = Shop.from_state(orig_shop.state)
        self.assertEqual(len(copy_shop.shop_slots), 0)

    def test_combine_scorpions(self):
        player = Player(team=["scorpion", "scorpion"])
        player.combine(0, 1)
    
    def test_squirrel(self):
        player = Player(team=Team([Pet("squirrel")]))
        player.start_turn()
        self.assertEqual(player.shop[3].cost,2)

        player.roll()
        self.assertEqual(player.shop[3].cost,3)

    def test_pill_1gold(self):
        player = Player(shop=Shop(["sleeping-pill"]), team=Team(["fish"]))
        player.buy_food(0, 0)
        self.assertEqual(player.gold, 9)

    def test_cupcake(self):
        player = Player(shop=Shop(["cupcake"]), team=Team([Pet("fish")]))

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 5)
        self.assertEqual(player.team[0].health, 6)

        player.end_turn()
        player.start_turn()

        self.assertEqual(player.team[0].attack, 2)
        self.assertEqual(player.team[0].health, 3)

    def test_apple(self):
        player = Player(shop=Shop(["apple"]), team=Team([Pet("beaver")]))

        player.buy_food(0, 0)
        self.assertEqual(player.team[0].attack, 3)
        self.assertEqual(player.team[0].health, 3)

    def test_shop_levelup_from_combine(self):
        player = Player(shop=Shop(["fish","fish"]),team=Team([Pet("fish")]))
        player.buy_combine(1,0)
        player.buy_combine(0,0)
        self.assertEqual(len(player.shop),1)

    def test_shop_levelup_from_ability(self):
        pet = Pet("caterpillar")
        pet.level = 2
        pet.experience = 2
        player = Player(shop=Shop([]), team=Team([pet]))
        pet.sot_trigger()
        self.assertEqual(len(player.shop),1)
