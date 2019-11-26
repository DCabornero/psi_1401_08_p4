from datamodel.models import Game, GameStatus, Move
from logic.tests_services import ServiceBaseTest
from datamodel import tests
from django.urls import reverse
from django.core.exceptions import ValidationError

SELECT_GAME_SERVICE = "select_game"
SIGNUP_SERVICE = "signup"


class TwoGamesTest(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """Se admiten varias partidas activas simultaneamente"""
        g1 = Game.objects.create(cat_user=self.users[0])
        self.assertEqual(g1.status, GameStatus.CREATED)
        g2 = Game.objects.create(cat_user=self.users[1])
        self.assertEqual(g2.status, GameStatus.CREATED)
        g1.mouse_user = self.users[1]
        g1.save()
        self.assertEqual(g1.status, GameStatus.ACTIVE)
        g2.mouse_user = self.users[0]
        g2.save()
        self.assertEqual(g2.status, GameStatus.ACTIVE)


class RedirectTest(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """Al seleccionar un juego se redirecciona a la vista del juego"""
        game = Game.objects.create(cat_user=self.user1,
                                   mouse_user=self.user2,
                                   status=GameStatus.ACTIVE)
        self.loginTestUser(self.client1, self.user1)
        response = self.client1.get(reverse(SELECT_GAME_SERVICE,
                                            kwargs={'game_id': game.id}),
                                    follow=True)
        self.assertIn("Play", self.decode(response.content))

    def test2(self):
        """Comprobamos que se renderiza correctamente el formulario de
        registro tras una petición get sin estar registrado"""
        response = self.client1.get(reverse(SIGNUP_SERVICE))
        self.assertIn("Signup user", self.decode(response.content))


class AdditionalMoveTest(tests.BaseModelTest):
    def setUp(self):
        super().setUp()

    def test1(self):
        """No se puede hacer un movimiento de gato cuyo origen no sea
        un gato"""
        game = Game.objects.create(cat_user=self.users[0],
                                   mouse_user=self.users[1],
                                   status=GameStatus.ACTIVE)
        with self.assertRaises(ValidationError):
            Move.objects.create(player=self.users[0], game=game,
                                origin=9, target=18)

    def test2(self):
        """No se puede hacer un movimiento de ratón cuyo origen no sea
        el ratón"""
        game = Game.objects.create(cat_user=self.users[0],
                                   mouse_user=self.users[1],
                                   status=GameStatus.ACTIVE)
        Move.objects.create(player=self.users[0], game=game,
                            origin=0, target=9)
        with self.assertRaises(ValidationError):
            Move.objects.create(player=self.users[1], game=game,
                                origin=50, target=41)

    def test3(self):
        """El str de Move es el esperado"""
        game = Game.objects.create(cat_user=self.users[0],
                                   mouse_user=self.users[1],
                                   status=GameStatus.ACTIVE)
        move = Move.objects.create(player=self.users[0], game=game,
                                   origin=0, target=9)
        exp_res = '(' + str(game.id) + ') '
        exp_res += str(move.origin) + ' -> ' + str(move.target) + ' '
        exp_res += self.users[0].username + ' ' + str(move.date)
        self.assertEqual(str(move), exp_res)
