from . import tests
from datamodel.models import Game, GameStatus, Move


class GameEndTests(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """ Situaciones en las que gana el ratón por pasar a los 4 gatos """
        games = []
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=25, cat2=43, cat3=29, cat4=47, mouse=9,
                          status=GameStatus.ACTIVE))
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=9, cat2=18, cat3=13, cat4=29, mouse=4,
                          status=GameStatus.ACTIVE))
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=47, cat2=61, cat3=59, cat4=57,
                          mouse=36, status=GameStatus.ACTIVE))
        for game in games:
            game.full_clean()
            game.save()
            self.assertEqual(game.status, GameStatus.FINISHED)
            self.assertEqual(Game.finish(game), "mouse")

    def test2(self):
        """ Situaciones en las que gana el ratón porque\
        los gatos se quedan sin movimientos """
        games = []
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=57, cat2=59, cat3=48, cat4=50, mouse=63,
                          status=GameStatus.ACTIVE))
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=63, cat2=61, cat3=54, cat4=47, mouse=45,
                          status=GameStatus.ACTIVE))
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=57, cat2=59, cat3=61, cat4=50, mouse=52,
                          status=GameStatus.ACTIVE))
        for game in games:
            game.full_clean()
            game.save()
            self.assertEqual(game.status, GameStatus.FINISHED)
            self.assertEqual(Game.finish(game), "mouse")

    def test3(self):
        """ Situaciones en las que ganan los gatos\
        (el ratón queda acorralado) """
        games = []
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=48, cat2=50, cat3=20, cat4=36, mouse=57,
                          status=GameStatus.ACTIVE))
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=25, cat2=41, cat3=36, cat4=52, mouse=32,
                          status=GameStatus.ACTIVE))
        games.append(Game(cat_user=self.users[0], mouse_user=self.users[1],
                          cat1=27, cat2=29, cat3=43, cat4=45, mouse=36,
                          status=GameStatus.ACTIVE))
        for game in games:
            game.full_clean()
            game.save()
            self.assertEqual(game.status, GameStatus.FINISHED)
            self.assertEqual(Game.finish(game), "cat")

    def test4(self):
        """ Los movimientos que dan una situación de \
        victoria cambian el estado a FINISHED """
        games = []
        games.append(Game.objects.create(cat_user=self.users[0],
                     mouse_user=self.users[1], cat1=25, cat2=43, cat3=38,
                     cat4=47, mouse=31, status=GameStatus.ACTIVE))
        games.append(Game.objects.create(cat_user=self.users[0],
                     mouse_user=self.users[1], cat1=63, cat2=61, cat3=54,
                     cat4=38, mouse=45, status=GameStatus.ACTIVE))
        games.append(Game.objects.create(cat_user=self.users[0],
                     mouse_user=self.users[1], cat1=27, cat2=22, cat3=43,
                     cat4=45, mouse=36, status=GameStatus.ACTIVE))
        moves = []
        moves.append(Move(game=games[0], origin=25,
                          target=32, player=self.users[0]))
        moves.append(Move(game=games[1], origin=38,
                          target=47, player=self.users[0]))
        moves.append(Move(game=games[2], origin=22,
                          target=29, player=self.users[0]))
        for game in games:
            game.full_clean()
            game.save()
            self.assertEqual(game.status, GameStatus.ACTIVE)
        for move in moves:
            move.full_clean()
            move.save()
        for game in games:
            self.assertEqual(game.status, GameStatus.FINISHED)
