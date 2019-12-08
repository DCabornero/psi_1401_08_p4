from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from datamodel.models import Counter
from datamodel.models import Game, Move
from datamodel.models import GameStatus
from logic.forms import SignupForm, MoveForm, LoginForm
from django.contrib.auth import authenticate
import django.contrib.auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from datamodel import constants
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

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
    Counter.objects.inc()
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


# @login_required
# def join_game(request):
#     # Author: David Cabornero
#     context_dict = {}
#     try:
#         # Buscamos el juego con id más alto con status CREATED en el que
#         # nuestro usuario no es el gato
#         game = Game.objects.filter(mouse_user__isnull=True).exclude(
#                                    cat_user=request.user).order_by('-id')[0]
#     except IndexError:
#         # Si no hay juego disponible, informamos al usuario
#         context_dict['msg_error'] = 'Sorry, there is no available game. \
#                                      Try creating one yourself!'
#         return render(request, "mouse_cat/join_game.html", context_dict)
#     # Actualizamos los datos del juego
#     game.mouse_user = request.user
#     game.save()
#     context_dict['game'] = game
#     return render(request, "mouse_cat/join_game.html", context_dict)


@login_required
def select_game(request, type, game_id=None):
    # Author: Sergio Galán
    context_dict = {}
    u = request.user
    if game_id is not None:
        try:
            g = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return errorHTTP(request, "Game number {0} does not exist, please try again.".format(game_id))
        if type == "play":
            if g.cat_user.id != u.id and g.mouse_user.id != u.id:
                return errorHTTP(request, "You are not a player of game number {0}, please try again.".format(game_id))
            if g.status != GameStatus.ACTIVE:
                return errorHTTP(request, "Game number {0} is not active, you can't play. Please try again.".format(game_id))
            request.session[constants.GAME_SELECTED_SESSION_ID] = g.id
            return(redirect(reverse('show_game', args=(type,))))
        if type == "join":
            if g.mouse_user:
                return errorHTTP(request, "Game number {0} is already full, please try again.".format(game_id))
            if g.cat_user.id == u.id:
                return errorHTTP(request, "You can't join a game you created, please try again.".format(game_id))
            g.mouse_user = u
            g.save()
            request.session[constants.GAME_SELECTED_SESSION_ID] = g.id
            return(redirect(reverse('show_game', args=("play",))))
        if type == 'reproduce':
            if g.cat_user.id != u.id and g.mouse_user.id != u.id:
                return errorHTTP(request, "You are not a player of game number {0}, please try again.".format(game_id))
            if g.status != GameStatus.FINISHED:
                return errorHTTP(request, "Game number {0} is not finished, you can't reproduce it. Please try again.".format(game_id))
            request.session[constants.GAME_SELECTED_SESSION_ID] = g.id
            if 'step' in request.session:
                del request.session['step']
            if 'direction' in request.session:
                del request.session['direction']
            return(redirect(reverse('show_game', args=(type,))))
    else:
        if type == "play":
            as_cat = Game.objects.filter(status=GameStatus.ACTIVE, cat_user=u)
            as_mouse = Game.objects.filter(status=GameStatus.ACTIVE, mouse_user=u)
            paginator = Paginator(list(as_cat)+list(as_mouse), 5)
            page = request.GET.get('page', default=1)
            context_dict['games'] = paginator.get_page(page)
            context_dict['type'] = 'play'
            return render(request, "mouse_cat/select_game.html", context_dict)
        elif type == "join":
            available = Game.objects.filter(status=GameStatus.CREATED).exclude(cat_user=u)
            paginator = Paginator(list(available), 5)
            page = request.GET.get('page', default=1)
            context_dict['games'] = paginator.get_page(page)
            context_dict['type'] = 'join'
            return render(request, "mouse_cat/select_game.html", context_dict)
        elif type == "reproduce":
            as_cat = Game.objects.filter(status=GameStatus.FINISHED, cat_user=u)
            as_mouse = Game.objects.filter(status=GameStatus.FINISHED, mouse_user=u)
            paginator = Paginator(list(as_cat)+list(as_mouse), 5)
            page = request.GET.get('page', default=1)
            context_dict['games'] = paginator.get_page(page)
            context_dict['type'] = 'reproduce'
            return render(request, "mouse_cat/select_game.html", context_dict)
    return errorHTTP(request, "Invalid url.")


@login_required
def show_game(request, type):
    # Author: Sergio Galán
    context_dict = {}
    # Comprobamos si el usuario ha seleccionado un juego previamente
    if constants.GAME_SELECTED_SESSION_ID not in request.session:
        return errorHTTP(request, "You must select a game before!")
    pk = request.session[constants.GAME_SELECTED_SESSION_ID]
    try:
        game = Game.objects.get(pk=pk)
    except Game.DoesNotExist:
        return errorHTTP(request, "Something went wrong, please try again.")
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
    context_dict['type'] = type
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
                return JsonResponse({'valid' : 0})
            move.game = game
            # Comprobamos si el movimiento es completamente válido en cuanto
            # a modelo y lógica
            try:
                move.save()
            except ValidationError:
                return JsonResponse({'valid' : 0})
            return JsonResponse({'valid' : 1})
        else:
            # Imprimimos los errores del formulario
            return JsonResponse({'valid' : 0})
    # No debería ser posible acceder a esta función mediante un método distinto
    # de POST
    else:
        return JsonResponse({'valid' : 0})


@login_required
def get_move(request):
    # Author: Sergio Galán
    if request.method != 'POST':
        return errorHTTP(request, "GET not allowed")
    shift = request.POST['shift']
    shift = int(shift)
    if 'direction' in request.session:
        direction = request.session['direction']
    else:
        direction = None
    if 'step' in request.session:
        step = request.session['step']
        if direction is None or direction == shift:
            step = step + shift
    else:
        step = 0
    game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
    moves = Move.objects.filter(game__id = game_id).order_by('date')
    if step >= len(list(moves)) or step < 0:
        return errorHTTP(request, "Unexpected error, please try again!")
    try:
        curr_move = list(moves)[step]
    except:
        return errorHTTP(request, "Unexpected error, please try again!")
    if shift == 1:
        ret_json = {
            'origin' : curr_move.origin,
            'target' : curr_move.target,
            'previous' : True,
            'next' : True
        }
    else:
        ret_json = {
            'origin' : curr_move.target,
            'target' : curr_move.origin,
            'previous' : True,
            'next' : True
        }
    if step == 0 and shift == -1:
        ret_json['previous'] = False
    if step == len(list(moves)) - 1 and shift == 1:
        ret_json['next'] = False
    if direction is None or direction == shift:
        request.session['step'] = step
    request.session['direction'] = shift
    request.session.modified = True
    return JsonResponse(ret_json)


@login_required
def current_move(request):
    # Author: David Cabornero
    if request.method != 'POST':
        return errorHTTP(request, "GET not allowed")
    game_id = request.session[constants.GAME_SELECTED_SESSION_ID]
    moves = Move.objects.filter(game__id = game_id).order_by('-date')
    curr_move = list(moves)[0]
    if curr_move.game.cat_turn is True:
        last_player = 'mouse'
    else:
        last_player = 'cat'
    if curr_move.game.status == GameStatus.FINISHED:
        winner = Game.finish(curr_move.game)
    else:
        winner = 'None'
    ret_json = {
        'origin': curr_move.origin,
        'target': curr_move.target,
        'last_move': last_player,
        'winner': winner
    }
    return JsonResponse(ret_json)
