from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from datamodel.models import Counter
from datamodel.models import Game
from datamodel.models import GameStatus
from logic.forms import SignupForm, MoveForm, LoginForm
from django.contrib.auth import authenticate
import django.contrib.auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from datamodel import constants
from django.core.exceptions import ValidationError

ANONYMOUSE_ERROR = "Action restricted to anonymous users"
LOGIN_ERROR = "Username/password is not valid"
SIGNUP_ERROR_PASSWORD = "Password and Repeat password are not the same"
SIGNUP_ERROR_USER = "A user with that username already exists"


# Decorador para requerir que el usuario no esté autenticado
def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                # Devolvemos un mensaje de error
                errorHTTP(request, exception=ANONYMOUSE_ERROR))
        else:
            return f(request)
    return wrapped


# Encapsula la devolución de un 404 con mensaje de error
def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict, status=404)


def index(request):
    return render(request, 'mouse_cat/index.html')


@anonymous_required
def login(request):
    # Author: David Cabornero
    context_dict = {}
    if request.method == 'POST':
        # Obtenemos los datos suministrados por el usuario
        username = request.POST.get('username')
        password = request.POST.get('password')
        login_form = LoginForm(data=request.POST)
        # Intentamos loguear con las credenciales
        user = authenticate(username=username, password=password)
        if user:
            # Comprobamos que el usuario no este dado de baja
            if user.is_active:
                django.contrib.auth.login(request, user)
                # Inicializamos el contador de sesión
                request.session['counter_session'] = 0
                # Redireccionamos al index
                return redirect(reverse('index'))
            else:
                return errorHTTP(request, "Login disabled")
        else:
            # Quitamos el error por defecto de username
            login_form.errors['username'] = []
            # Añadimos el error requerido por los tests
            login_form.add_error('username', LOGIN_ERROR)
            context_dict['user_form'] = login_form
            # Volvemos a cargar la página de login con los errores
            return render(request, "mouse_cat/login.html", context_dict)
    else:
        # Si la petición es un GET, simplemente devolvemos el formulario
        # a rellenar
        context_dict['user_form'] = LoginForm()
        return render(request, "mouse_cat/login.html", context_dict)


@login_required
def logout(request):
    # Author: Sergio Galán
    context_dict = {}
    # Guardamos el nombre del usuario para poder despedirle
    context_dict['user'] = request.user.username
    django.contrib.auth.logout(request)
    # Cambio a usuario no logeado, counter de sesión a 0
    request.session['counter_session'] = 0
    return render(request, "mouse_cat/logout.html", context_dict)


@anonymous_required
def signup(request):
    # Author: Sergio Galán
    context_dict = {}
    if request.method == 'POST':
        # Comprobamos que se ha confirmado la contraseña correctamente
        if request.POST.get('password') != request.POST.get('password2'):
            signup_form = SignupForm(data=request.POST)
            # Se carga el error correspondiente
            signup_form.add_error('password2', SIGNUP_ERROR_PASSWORD)
            context_dict['user_form'] = signup_form
            # Volvemos a cargar el formulario con los errores
            return render(request, "mouse_cat/signup.html", context_dict)
        user_form = SignupForm(data=request.POST)
        # Comprobamos que el registro sea válido
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            # Además de registralo, lo dejamos logueado y redireccionamos
            # al index
            django.contrib.auth.login(request, user)
            return redirect(reverse('index'))
        # Si el registro no es válido
        else:
            if "username" in user_form.errors:
                # Quitamos el error por defecto y ponemos el de los tests
                user_form.errors['username'] = []
                user_form.add_error('username', SIGNUP_ERROR_USER)
            context_dict['user_form'] = user_form
            # Volvemos a renderizar el formulario con los errores
            return render(request, "mouse_cat/signup.html", context_dict)
    # En las peticiones get devolvemos el formulario correspondiente
    else:
        context_dict['user_form'] = SignupForm()
        return render(request, "mouse_cat/signup.html", context_dict)


def counter(request):
    # Author: David Cabornero
    context_dict = {}
    if 'counter_session' in request.session:
        request.session['counter_session'] += 1
    else:
        # Caso dado cuando un usuario no logeado ni deslogueado entra
        request.session['counter_session'] = 1
    # Incrementamos el contador global mediante su interfaz
    Counter.objects.inc()
    # Pasamos los valores de los contadores a la template
    context_dict['counter_session'] = request.session['counter_session']
    context_dict['counter_global'] = Counter.objects.get_current_value()
    return render(request, "mouse_cat/counter.html", context_dict)


@login_required
def create_game(request):
    # Author: Sergio Galán
    # Creamos el juego en cuestión
    game = Game(cat_user=request.user)
    game.save()
    context_dict = {}
    # Pasamos el juego creado a la template
    context_dict['game'] = game
    return render(request, "mouse_cat/new_game.html", context_dict)


@login_required
def join_game(request):
    # Author: David Cabornero
    context_dict = {}
    try:
        # Buscamos el juego con id más alto con status CREATED en el que
        # nuestro usuario no es el gato
        game = Game.objects.filter(mouse_user__isnull=True).exclude(
                                   cat_user=request.user).order_by('-id')[0]
    except IndexError:
        # Si no hay juego disponible, informamos al usuario
        context_dict['msg_error'] = 'Sorry, there is no available game. \
                                     Try creating one yourself!'
        return render(request, "mouse_cat/join_game.html", context_dict)
    # Actualizamos los datos del juego
    game.mouse_user = request.user
    game.save()
    context_dict['game'] = game
    return render(request, "mouse_cat/join_game.html", context_dict)


@login_required
def select_game(request, type, game_id=None):
    # Author: Sergio Galán
    context_dict = {}
    # Si la petición viene con el parámetro id
    # if game_id is not None:
    #     # Buscamos el juego con ese id
    #     try:
    #         g = Game.objects.get(pk=game_id)
    #     # Salvo que no exista o no cumpla las condiciones siguientes
    #     except Game.DoesNotExist:
    #         return errorHTTP(request, "No game with id = {0} \
    #                                    in the database".format(game_id))
    #     # No se puede jugar un juego que no tenga status ACTIVE
    #     if g.status != GameStatus.ACTIVE:
    #         return errorHTTP(request, "Game with id = {0} \
    #                                    is not active".format(game_id))
    #     # No se puede jugar un juego en el que el usuario no sea uno de los
    #     # jugadores
    #     condition1 = g.mouse_user.id != request.user.id
    #     condition2 = g.cat_user.id != request.user.id
    #     if condition1 and condition2:
    #         return errorHTTP(request, "You are not a player of the game \
    #                                    with id = {0}".format(game_id))
    #     request.session['game_selected'] = game_id
    #     # Redireccionamos a la vista del juego seleccionado
    #     return redirect(reverse('show_game'))
    # Si viene sin el parametro id, ofrecemos una lista de juegos disponibles
    # diferenciados por el puesto vacante (gato o ratón)
    #else:
    u = request.user
    if type == "play":
        as_cat = Game.objects.filter(status=GameStatus.ACTIVE, cat_user=u)
        as_mouse = Game.objects.filter(status=GameStatus.ACTIVE, mouse_user=u)
        context_dict['as_cat'] = list(as_cat)
        context_dict['as_mouse'] = list(as_mouse)
        return render(request, "mouse_cat/select_game.html", context_dict)
    elif type == "join":
        available = Game.objects.filter(status=GameStatus.CREATED).exclude(cat_user=user)
        context_dict['available_games'] = list(available)
        return render(request, "mouse_cat/join_game.html", context_dict)
    elif type == "reproduce":
        reproduzable = Game.objects.filter(status=GameStatus.FINISHED)


@login_required
def show_game(request):
    # Author: Sergio Galán
    context_dict = {}
    # Comprobamos si el usuario ha seleccionado un juego previamente
    if constants.GAME_SELECTED_SESSION_ID not in request.session:
        return errorHTTP(request, "You must select a game before!")
    pk = request.session[constants.GAME_SELECTED_SESSION_ID]
    game = Game.objects.get(pk=pk)
    # Diseñamos el tablero inicial
    board = [0]*64
    board[game.cat1] = 1
    board[game.cat2] = 1
    board[game.cat3] = 1
    board[game.cat4] = 1
    board[game.mouse] = -1
    # Añadimos el formulario de movimiento
    move_form = MoveForm()
    context_dict['game'] = game
    context_dict['board'] = board
    context_dict['move_form'] = move_form
    return render(request, "mouse_cat/game.html", context_dict)


@login_required
def move(request):
    # Author: David Cabornero
    if request.method == 'POST':
        form = MoveForm(data=request.POST)
        # Comprobamos si el movimiento es válido en cuanto a rango de valores
        if form.is_valid():
            move = form.save(commit=False)
            move.player = request.user
            # Comprobamos si hay un juego seleccionado
            try:
                pk = request.session[constants.GAME_SELECTED_SESSION_ID]
                game = Game.objects.get(pk=pk)
            except KeyError:
                return errorHTTP(request, "Game not selected. Please select a \
                                           game before trying to play")
            move.game = game
            # Comprobamos si el movimiento es completamente válido en cuanto
            # a modelo y lógica
            try:
                move.save()
            except ValidationError:
                return errorHTTP(request, "Move not allowed")
            return redirect(reverse('show_game'))
        else:
            # Imprimimos los errores del formulario
            return errorHTTP(request, form.errors)
    # No debería ser posible acceder a esta función mediante un método distinto
    # de POST
    else:
        return errorHTTP(request, "Invalid method")
