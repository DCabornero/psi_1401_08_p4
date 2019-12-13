# from . import tests
# from datamodel.models import Game, GameStatus, Move
from logic.tests_services import ServiceBaseTest
from datamodel import tests
# from django.urls import reverse
from django.core.exceptions import ValidationError
import re
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Q
from django.test import Client, TransactionTestCase
from django.urls import reverse

from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, Move
from datamodel.tests import BaseModelTest

from . import forms

# Tests classes:
# - LogInOutServiceTests
# - SignupServiceTests
# - CounterServiceTests
# - LogInOutCounterServiceTests
# - CreateGameServiceTests
# - JoinGameServiceTests
# - SelectGameServiceTests
# - PlayServiceTests
# - MoveServiceTests

TEST_USERNAME_1 = "testUserMouseCatBaseTest_1"
TEST_PASSWORD_1 = "hskjdhfhw"
TEST_USERNAME_2 = "testUserMouseCatBaseTest_2"
TEST_PASSWORD_2 = "kj83jfbhg"

USER_SESSION_ID = "_auth_user_id"

LANDING_PAGE = "landing"
LANDING_TITLE = r"<h1>Service catalog</h1>|<h1>Servicios</h1>"

ANONYMOUSE_ERROR = "Anonymous required"
ERROR_TITLE = "<h1>Error</h1>"

LOGIN_SERVICE = "login"
LOGIN_ERROR = "login_error"
LOGIN_TITLE = "<h1>Login</h1>"

LOGOUT_SERVICE = "logout"

SIGNUP_SERVICE = "signup"
SIGNUP_ERROR_PASSWORD = "signup_error1"
SIGNUP_ERROR_USER = "signup_error2"
SIGNUP_ERROR_AUTH_PASSWORD = "signup_error3"
SIGNUP_TITLE = r"<h1>Signup user</h1>|<h1>Alta de usuarios</h1>"

COUNTER_SERVICE = "counter"
COUNTER_SESSION_VALUE = "session_counter"
COUNTER_GLOBAL_VALUE = "global_counter"
COUNTER_TITLE = r"<h1>Request counters</h1>|<h1>Contadores de peticiones</h1>"

CREATE_GAME_SERVICE = "create_game"

JOIN_GAME_SERVICE = "join_game"
JOIN_GAME_ERROR_NOGAME = "join_game_error"
JOIN_GAME_TITLE = r"<h1>Join game</h1>|<h1>Unirse a juego</h1>"

CLEAN_SERVICE = "clean_db"
CLEAN_TITLE = r"<h1>Clean orphan games</h1>|<h1>Borrar juegos huérfanos</h1>"

SELECT_GAME_SERVICE = "select_game"
SELECT_GAME_ERROR_NOCAT = "select_game_error1"
SELECT_GAME_ERROR_NOMOUSE = "select_game_error2"
SELECT_GAME_TITLE = r"<h1>Select game</h1>|<h1>Seleccionar juego</h1>"

SHOW_GAME_SERVICE = "show_game"
PLAY_GAME_MOVING = "play_moving"
PLAY_GAME_WAITING = "play_waiting"
SHOW_GAME_TITLE = r"<h1>Play</h1>|<h1>Jugar</h1>"

MOVE_SERVICE = "move"

SERVICE_DEF = {
    LANDING_PAGE: {
        "title": LANDING_TITLE,
        "pattern": r"<span class=\"username\">(?P<username>\w+)</span>"
    },
    ANONYMOUSE_ERROR: {
        "title": ERROR_TITLE,
        "pattern": r"Action restricted to anonymous \
                     users|Servicio restringido a usuarios anónimos"
    },
    LOGIN_SERVICE: {
        "title": LOGIN_TITLE,
        "pattern": r"Log in to continue:|Autenticarse para continuar:"
    },
    LOGIN_ERROR: {
        "title": LOGIN_TITLE,
        "pattern": r"Username/password is not valid|Usuario/clave no válidos"
    },
    SIGNUP_ERROR_PASSWORD: {
        "title": SIGNUP_TITLE,
        "pattern": r"Password and Repeat password are not \
                     the same|La clave y su repetición no coinciden"
    },
    SIGNUP_ERROR_USER: {
        "title": SIGNUP_TITLE,
        "pattern": r"A user with that username already \
                     exists|Usuario duplicado"
    },
    SIGNUP_ERROR_AUTH_PASSWORD: {
        "title": SIGNUP_TITLE,
        "pattern": r"(?=.*too short)(?=.*at least 6 \
                     characters)(?=.*too common)"
    },
    COUNTER_SESSION_VALUE: {
        "title": COUNTER_TITLE,
        "pattern": r"Counter session: <b>(?P<session_counter>\d+)</b>"
    },
    COUNTER_GLOBAL_VALUE: {
        "title": COUNTER_TITLE,
        "pattern": r"Counter global: <b>(?P<global_counter>\d+)</b>"
    },
    JOIN_GAME_ERROR_NOGAME: {
        "title": JOIN_GAME_TITLE,
        "pattern": r"There is no available games|No hay juegos disponibles"
    },
    CLEAN_SERVICE: {
        "title": CLEAN_TITLE,
        "pattern": r"<b>(?P<n_games_delete>\d+)</b> (games removed \
                     from db|juegos borrados de la bd)"
    },
    SELECT_GAME_SERVICE: {
        "title": SELECT_GAME_TITLE,
        "pattern": r""
    },
    SELECT_GAME_ERROR_NOCAT: {
        "title": SELECT_GAME_TITLE,
        "pattern": r"No games as cat|No hay juegos disponibles como gato"
    },
    SELECT_GAME_ERROR_NOMOUSE: {
        "title": SELECT_GAME_TITLE,
        "pattern": r"No games as mouse|No hay juegos disponibles como ratón"
    },
    SHOW_GAME_SERVICE: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"(Board|Tablero): (?P<board>\[.*?\])"
    },
    PLAY_GAME_MOVING: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"<blockquote class=\"(?P<turn>\w+)\">(.|\n)*?"
        r"<input type=\"submit\" value=\"Move\" />(.|\n)*?</blockquote>"
    },
    PLAY_GAME_WAITING: {
        "title": SHOW_GAME_TITLE,
        "pattern": r"(Waiting for the|Esperando al) (?P<turn>\w+).{3}"
    },
}

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


class ServiceBaseTest(TransactionTestCase):
    def setUp(self):
        self.paramsUser1 = {"username": TEST_USERNAME_1,
                            "password": TEST_PASSWORD_1}
        self.paramsUser2 = {"username": TEST_USERNAME_2,
                            "password": TEST_PASSWORD_2}

        User.objects.filter(
            Q(username=self.paramsUser1["username"]) |
            Q(username=self.paramsUser2["username"])).delete()

        self.user1 = User.objects.create_user(
            username=self.paramsUser1["username"],
            password=self.paramsUser1["password"])
        self.user2 = User.objects.create_user(
            username=self.paramsUser2["username"],
            password=self.paramsUser2["password"])

        self.client1 = self.client
        self.client2 = Client()

    def tearDown(self):
        User.objects.filter(
            Q(username=self.paramsUser1["username"]) |
            Q(username=self.paramsUser2["username"])).delete()

    @classmethod
    def loginTestUser(cls, client, user):
        client.force_login(user)

    @classmethod
    def logoutTestUser(cls, client):
        client.logout()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")

    def validate_login_required(self, client, service):
        self.logoutTestUser(client)
        response = client.get(reverse(service), follow=True)
        self.assertEqual(response.status_code, 200)
        self.is_login(response)

    def validate_anonymous_required(self, client, service):
        self.loginTestUser(client, self.user1)
        response = client.get(reverse(service), follow=True)
        self.assertEqual(response.status_code, 403)
        self.is_anonymous_error(response)

    def validate_response(self, service, response):
        definition = SERVICE_DEF[service]
        self.assertRegex(self.decode(response.content), definition["title"])
        m = re.search(definition["pattern"], self.decode(response.content))
        self.assertTrue(m)
        return m

    def is_login(self, response):
        self.validate_response(LOGIN_SERVICE, response)

    def is_login_error(self, response):
        self.validate_response(LOGIN_ERROR, response)

    def is_anonymous_error(self, response):
        self.validate_response(ANONYMOUSE_ERROR, response)

    def is_landing_autenticated(self, response, user):
        m = self.validate_response(LANDING_PAGE, response)
        self.assertEqual(m.group("username"), user.username)

    def is_signup_error1(self, response):
        self.validate_response(SIGNUP_ERROR_PASSWORD, response)

    def is_signup_error2(self, response):
        self.validate_response(SIGNUP_ERROR_USER, response)

    def is_signup_error3(self, response):
        self.validate_response(SIGNUP_ERROR_AUTH_PASSWORD, response)

    def is_counter_session(self, response, value):
        m = self.validate_response(COUNTER_SESSION_VALUE, response)
        self.assertEqual(Decimal(m.group("session_counter")), value)

    def is_counter_global(self, response, value):
        m = self.validate_response(COUNTER_GLOBAL_VALUE, response)
        self.assertEqual(Decimal(m.group("global_counter")), value)

    def is_join_game_error(self, response):
        self.validate_response(JOIN_GAME_ERROR_NOGAME, response)

    def is_clean_db(self, response, n_games):
        m = self.validate_response(CLEAN_SERVICE, response)
        self.assertEqual(Decimal(m.group("n_games_delete")), n_games)

    def is_select_game(self, response):
        self.validate_response(SELECT_GAME_SERVICE, response)

    def is_select_game_nocat(self, response):
        self.validate_response(SELECT_GAME_ERROR_NOCAT, response)

    def is_select_game_nomouse(self, response):
        self.validate_response(SELECT_GAME_ERROR_NOMOUSE, response)

    def is_play_game(self, response, game):
        m = self.validate_response(SHOW_GAME_SERVICE, response)
        board = ([0] * (Game.MAX_CELL - Game.MIN_CELL + 1))
        board[game.cat1] = board[game.cat2] = 1
        board[game.cat3] = board[game.cat4] = 1
        board[game.mouse] = -1
        self.assertEquals(m.group("board"), str(board))

    def is_play_game_moving(self, response, game):
        m = self.validate_response(PLAY_GAME_MOVING, response)
        self.assertEqual(game.cat_turn, m.group("turn") == "cat")
        self.assertEqual(not game.cat_turn, m.group("turn") == "mouse")

    def is_play_game_waiting(self, response, game):
        m = self.validate_response(PLAY_GAME_WAITING, response)
        self.assertEqual(game.cat_turn, m.group("turn") == "cat")
        self.assertEqual(not game.cat_turn, m.group("turn") == "mouse")


class LogInOutServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Logout válido """
        self.loginTestUser(self.client1, self.user1)
        self.assertEqual(Decimal(self.client1.session.get(USER_SESSION_ID)),
                         self.user1.id)
        self.client1.get(reverse(LOGOUT_SERVICE), follow=True)
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))


class SignupServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()
        self.paramsUser1.update({"password2": self.paramsUser1["password"]})

    def tearDown(self):
        super().tearDown()

    def test0(self):
        """ Validación correcta del formulario de alta """
        User.objects.filter(id=self.user1.id).delete()
        self.assertTrue(forms.SignupForm(self.paramsUser1).is_valid())

    def test1(self):
        """ Alta correcta de usuarios """
        User.objects.filter(id=self.user1.id).delete()
        n_user = User.objects.count()

        self.client1.post(reverse(SIGNUP_SERVICE), self.paramsUser1,
                          follow=True)
        self.assertEquals(User.objects.count(), n_user + 1)

        user = User.objects.get(username=self.paramsUser1["username"])
        self.assertEqual(user.username, self.paramsUser1["username"])
        self.assertNotEqual(user.password, self.paramsUser1["password"])
        self.assertTrue(user.check_password(self.paramsUser1["password"]))


class CounterServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Actualización correcta del contador de sesión """
        for i in range(1, 4):
            response = self.client1.get(reverse(COUNTER_SERVICE), follow=True)
            self.is_counter_session(response, i)
        for i in range(1, 3):
            response = self.client2.get(reverse(COUNTER_SERVICE), follow=True)
            self.is_counter_session(response, i)
        for i in range(4, 6):
            response = self.client1.get(reverse(COUNTER_SERVICE), follow=True)
            self.is_counter_session(response, i)

    def test2(self):
        """ Actualización correcta del contador global """
        n_calls = Counter.objects.get_current_value()

        for _ in range(2):
            response = self.client1.get(reverse(COUNTER_SERVICE), follow=True)
            n_calls += 1
            self.is_counter_global(response, n_calls)

            response = self.client2.get(reverse(COUNTER_SERVICE), follow=True)
            n_calls += 1
            self.is_counter_global(response, n_calls)


class LogInOutCounterServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Gestión correcta de los contadores cuando se cierra y
        reabre sesión """
        n_calls = Counter.objects.get_current_value()

        for i in range(1, 3):
            response = self.client1.get(reverse(COUNTER_SERVICE), follow=True)
            n_calls += 1
            self.is_counter_session(response, i)
            self.is_counter_global(response, n_calls)

        response = self.client1.post(reverse(LOGIN_SERVICE), self.paramsUser1,
                                     follow=True)
        self.assertEqual(response.status_code, 200)
        for i in range(1, 3):
            response = self.client1.get(reverse(COUNTER_SERVICE), follow=True)
            n_calls += 1
            self.is_counter_session(response, i)
            self.is_counter_global(response, n_calls)

        response = self.client1.get(reverse(LOGOUT_SERVICE), follow=True)
        self.assertEqual(response.status_code, 200)
        for i in range(1, 3):
            response = self.client1.get(reverse(COUNTER_SERVICE), follow=True)
            n_calls += 1
            self.is_counter_session(response, i)
            self.is_counter_global(response, n_calls)


class GameRequiredBaseServiceTests(ServiceBaseTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        self.user1.games_as_cat.all().delete()
        self.user2.games_as_cat.all().delete()
        super().tearDown()


class BckGamesServiceTests(GameRequiredBaseServiceTests):
    def setUp(self):
        super().setUp()
        self.bck_games = None

    def tearDown(self):
        if self.bck_games:
            for game in self.bck_games:
                game.mouse_user = None
                game.save()

        super().tearDown()

    def clean_games(self):
        self.bck_games = Game.objects.filter(mouse_user__isnull=True)
        for game in self.bck_games:
            game.mouse_user = self.user1
            game.save()


class CreateGameServiceTests(GameRequiredBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """ Crear juego correctamente """
        n_games = Game.objects.count()
        if n_games == 0:
            id_max = -1
        else:
            id_max = Game.objects.order_by('-id')[0:1].get().id

        self.loginTestUser(self.client1, self.user1)
        response = self.client1.get(reverse(CREATE_GAME_SERVICE), follow=True)
        self.assertEqual(response.status_code, 200)

        games = Game.objects.filter(id__gt=id_max)
        self.assertEqual(games.count(), 1)
        self.assertEqual(games[0].cat_user.username, self.user1.username)
        self.assertIsNone(games[0].mouse_user)
        self.assertTrue(games[0].cat_turn)


class PlayGameBaseServiceTests(GameRequiredBaseServiceTests):
    def setUp(self):
        super().setUp()

        self.sessions = [
            {"client": self.client1, "player": self.user1},
            {"client": self.client2, "player": self.user2},
        ]

    def tearDown(self):
        super().tearDown()

    def set_game_in_session(self, client, user, game_id):
        self.loginTestUser(client, user)
        session = client.session
        session[constants.GAME_SELECTED_SESSION_ID] = game_id
        session.save()


class SelectServiceTests(GameRequiredBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test1(self):
        """La generalización del servicio funciona"""
        Game.objects.create(id=147, cat_user=self.user1, mouse_user=self.user2)
        Game.objects.create(id=258, cat_user=self.user1, mouse_user=self.user2,
                            status=GameStatus.FINISHED)
        Game.objects.create(id=369, cat_user=self.user1)
        self.loginTestUser(self.client2, self.user2)
        response = self.client2.get(reverse('select_game',
                                            kwargs={'type': 'join'}),
                                    follow=True)
        self.assertIn('369', self.decode(response.content))
        self.assertNotIn('147', self.decode(response.content))
        self.assertNotIn('258', self.decode(response.content))
        response = self.client2.get(reverse('select_game',
                                            kwargs={'type': 'play'}),
                                    follow=True)
        self.assertNotIn('369', self.decode(response.content))
        self.assertIn('147', self.decode(response.content))
        self.assertNotIn('258', self.decode(response.content))
        response = self.client2.get(reverse('select_game',
                                            kwargs={'type': 'reproduce'}),
                                    follow=True)
        self.assertNotIn('369', self.decode(response.content))
        self.assertNotIn('147', self.decode(response.content))
        self.assertIn('258', self.decode(response.content))


class MoveServiceTests(PlayGameBaseServiceTests):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test0(self):
        """ Campos de formulario válidos """
        self.assertTrue(forms.MoveForm({"origin": 0, "target": 0}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": -1,
                                         "target": 0}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": 64,
                                         "target": 0}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": 0,
                                         "target": -1}).is_valid())
        self.assertFalse(forms.MoveForm({"origin": 0,
                                         "target": 64}).is_valid())

    def test1(self):
        """ Secuencia de movimientos válidos """
        moves = [
            {**self.sessions[0], **{"origin": 0, "target": 9,
                                    "positions": [9, 2, 4, 6, 59]}},
            {**self.sessions[1], **{"origin": 59, "target": 50,
                                    "positions": [9, 2, 4, 6, 50]}},
            {**self.sessions[0], **{"origin": 9, "target": 16,
                                    "positions": [16, 2, 4, 6, 50]}},
            {**self.sessions[1], **{"origin": 50, "target": 41,
                                    "positions": [16, 2, 4, 6, 41]}},
        ]

        game_t0 = Game.objects.create(cat_user=self.user1,
                                      mouse_user=self.user2,
                                      status=GameStatus.ACTIVE)
        for session in self.sessions:
            self.set_game_in_session(session["client"], session["player"],
                                     game_t0.id)

        n_moves = 0
        for move in moves:
            response = move["client"].post(reverse(MOVE_SERVICE), move,
                                           follow=True)
            self.assertEqual(response.status_code, 200)

            game_t1 = Game.objects.get(id=game_t0.id)
            n_moves += 1
            self.assertNotEqual(str(game_t0), str(game_t1))
            self.assertEqual(BaseModelTest.get_array_positions(game_t1),
                             move["positions"])
            self.assertEqual(game_t1.cat_turn, move["player"] == self.user2)
            self.assertEqual(game_t1.moves.count(), n_moves)

            game_t0 = game_t1
