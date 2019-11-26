import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'ratonGato.settings')
import django
django.setup()
from datamodel.models import Game, Move
from django.contrib.auth.models import User


def populate():
    cat = add_user(10, 'cat')
    mouse = add_user(11, 'mouse')
    add_game(cat)
    gs = Game.objects.filter(cat_user__isnull=False, mouse_user__isnull=True)
    for game in gs:
        print(game)
    thisgame = gs[0]
    add_rival(thisgame, mouse)
    print(thisgame)
    add_move(thisgame, cat, 2, 11)
    print(thisgame)
    add_move(thisgame, mouse, 59, 52)
    print(thisgame)


def add_user(id, username):
    u = User.objects.get_or_create(id=id)[0]
    u.username = username
    u.save()
    return u


def add_game(user):
    g = Game.objects.create(cat_user=user)
    return g


def add_rival(game, user):
    game.mouse_user = user
    game.save()
    return game


def add_move(game, user, origin, target):
    m = Move.objects.create(game=game, origin=origin,
                            target=target, player=user)
    return m


# Start execution here!
if __name__ == '__main__':
    print('Starting Datamodel test script...')
    populate()
