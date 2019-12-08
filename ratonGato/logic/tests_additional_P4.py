# from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError
# from django.test import TestCase
#
# from . import tests
# from .models import Game, GameStatus, Move, Counter
#
# class GameEndTests(tests.BaseModelTest):
#     def setUp(self):
#         super().setUp()
#
#     def test1(self):
#         """ Crear juego válido con un único jugador """
#         game = Game(cat_user=self.users[0])
#         game.full_clean()
#         game.save()
#         self.assertIsNone(game.mouse_user)
#         self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
#         self.assertTrue(game.cat_turn)
#         self.assertEqual(game.status, GameStatus.CREATED)
#
#     def test2(self):
#         """ Optional """
#         """ Crear juego válido con dos jugadores """
#         game = Game(cat_user=self.users[0], mouse_user=self.users[1])
#         game.save()
#         self.assertEqual(self.get_array_positions(game), [0, 2, 4, 6, 59])
#         self.assertTrue(game.cat_turn)
#         self.assertEqual(game.status, GameStatus.ACTIVE)
#
#     def test3(self):
#         """ Optional """
#         """ Transición de creado a activo al añadir el segundo jugador """
#         game = Game(cat_user=self.users[0])
#         game.save()
#         self.assertEqual(game.status, GameStatus.CREATED)
#         game.mouse_user = self.users[1]
#         game.save()
#         self.assertEqual(game.status, GameStatus.ACTIVE)
#
#     def test4(self):
#         """ Estados válidos de juegos con dos jugadores """
#         states = [
#             {"status": GameStatus.ACTIVE, "valid": True},
#             {"status": GameStatus.FINISHED, "valid": True}
#         ]
#
#         for state in states:
#             game = Game(cat_user=self.users[0], mouse_user=self.users[1], status=state["status"])
#             game.full_clean()
#             game.save()
#             self.assertEqual(game.status, state["status"])
#
#     def test5(self):
#         """ Estados válidos con un jugador """
#         states = [
#             {"status": GameStatus.CREATED, "valid": True},
#             {"status": GameStatus.ACTIVE, "valid": False},
#             {"status": GameStatus.FINISHED, "valid": False}
#         ]
#
#         for state in states:
#             try:
#                 game = Game(cat_user=self.users[0], status=state["status"])
#                 game.full_clean()
#                 game.save()
#                 self.assertEqual(game.status, state["status"])
#             except ValidationError as err:
#                 with self.assertRaisesRegex(ValidationError, tests.MSG_ERROR_GAMESTATUS):
#                     if not state["valid"]:
#                         raise err
#
#     def test6(self):
#         """ Juegos sin jugador 1 """
#         for status in [GameStatus.CREATED, GameStatus.ACTIVE, GameStatus.FINISHED]:
#             with self.assertRaises(ValidationError):
#                 game = Game(mouse_user=self.users[1], status=status)
#                 game.full_clean()
