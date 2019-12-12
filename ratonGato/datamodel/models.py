from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

MSG_ERROR_INVALID_CELL = "Invalid cell for a cat or the mouse"
MSG_ERROR_INVALID_CELL += "|Gato o ratón en posición no válida"
MSG_ERROR_GAMESTATUS = "Game status not valid|Estado no válido"
MSG_ERROR_MOVE = "Move not allowed|Movimiento no permitido"
MSG_ERROR_NEW_COUNTER = "Insert not allowed|Inseción no permitida"


class GameStatus(models.IntegerField):
    # Definimos los posibles estados del juego
    CREATED = 0
    ACTIVE = 1
    FINISHED = 2

    def __init__(self, *args, **kwargs):
        # Hacemos que GameStatus solo pueda tener los tres valores definidos
        kwargs['choices'] = ((self.CREATED, 0),
                             (self.ACTIVE, 1),
                             (self.FINISHED, 2),)
        super().__init__(*args, **kwargs)


class Game(models.Model):
    # Características básicas del tablero
    MIN_CELL = 0
    MAX_CELL = 63
    ROW_LEN = 8
    COL_LEN = 8

    # Validador de casilla correcta
    def validator_tile(value):
        if value < Game.MIN_CELL or value > Game.MAX_CELL:
            raise ValidationError(MSG_ERROR_INVALID_CELL)
        # Calculamos la fila y columna de manera genérica (es decir, teniendo
        # en cuenta que podría haber un número distinto de filas y columnas)
        coded_value = [(value//Game.COL_LEN)+1, (value % Game.ROW_LEN)+1]
        # Si ambas coordenadas son pares o impares, son casillas válidas
        # y la suma tanto de dos pares como de dos impares es par
        suma = coded_value[0]+coded_value[1]
        if (suma % 2) != 0:
            raise ValidationError(MSG_ERROR_INVALID_CELL)

    # Definimos los campos necesarios para implementar la funcionalidad
    cat_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='games_as_cat')
    mouse_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='games_as_mouse',
                                   null=True, blank=True)
    cat1 = models.IntegerField(blank=True, default=0,
                               validators=[validator_tile])
    cat2 = models.IntegerField(blank=True, default=2,
                               validators=[validator_tile])
    cat3 = models.IntegerField(blank=True, default=4,
                               validators=[validator_tile])
    cat4 = models.IntegerField(blank=True, default=6,
                               validators=[validator_tile])
    mouse = models.IntegerField(blank=True, default=59,
                                validators=[validator_tile])
    cat_turn = models.BooleanField(blank=True, default=True)
    status = GameStatus(blank=True, default=GameStatus.CREATED)

    # Devuelve "cat" si ganan los gatos, "mouse" si gana el ratón, None si
    # la partida no cumple las condiciones de finalización
    def finish(self):
        m = self.mouse
        c1 = self.cat1
        c2 = self.cat2
        c3 = self.cat3
        c4 = self.cat4
        m = [(m//Game.ROW_LEN)+1, (m % Game.ROW_LEN)+1]
        c1 = [(c1//Game.ROW_LEN)+1, (c1 % Game.ROW_LEN)+1]
        c2 = [(c2//Game.ROW_LEN)+1, (c2 % Game.ROW_LEN)+1]
        c3 = [(c3//Game.ROW_LEN)+1, (c3 % Game.ROW_LEN)+1]
        c4 = [(c4//Game.ROW_LEN)+1, (c4 % Game.ROW_LEN)+1]
        # Guardamos las coordenadas de los cuatro gatos
        cats = [c1, c2, c3, c4]
        valid_targets = [[m[0]-1, (m[1]-1) % (Game.ROW_LEN + 1)],
                         [m[0]-1, (m[1]+1) % (Game.ROW_LEN + 1)],
                         [m[0]+1, (m[1]-1) % (Game.ROW_LEN + 1)],
                         [m[0]+1, (m[1]+1) % (Game.ROW_LEN + 1)]]
        is_mouse_notloser = 0
        for t in valid_targets:
            flag = 0
            if t[0] <= Game.COL_LEN and t[0] >= 1 and t[1] != 0:
                # Nos quedamos con los movimientos que se quedan dentro del
                # tablero
                for cat in cats:
                    # Miramos si el objetivo no está ocupado por un gato
                    if cat[0] == t[0] and cat[1] == t[1]:
                        flag = 1
                        break
                if flag == 0:
                    is_mouse_notloser = 1
                    break
        if not is_mouse_notloser:
            return "cat"
        # Ahora tenemos que ver si ha ganado el ratón, es decir que ningún
        # gato tiene movimientos disponibles o que el ratón ha adelantado a
        # los gatos
        others = [c1, c2, c3, c4, m]
        # Comprobamos si todos los gatos están adelantados
        mouse_win = 1
        for cat in cats:
            if m[0] >= cat[0]:
                mouse_win = 0
                break
        if mouse_win == 1:
            return "mouse"

        for cat in cats:
            others.remove(cat)
            valid_targets = [[cat[0]+1, (cat[1]-1) % (Game.ROW_LEN + 1)],
                             [cat[0]+1, (cat[1]+1) % (Game.ROW_LEN + 1)]]
            for t in valid_targets:
                if t[0] <= Game.COL_LEN and t[0] >= 1 and t[1] != 0:
                    # Comprobamos si los posibles movimientos están ocupados
                    # por otras entidades
                    if t not in others:
                        return None
            others.append(cat)
        # Si llega aquí es que ha ganado el ratón por no tener ningún
        # movimiento válido los gatos
        return "mouse"

    def save(self, *args, **kwargs):
        # Hacemos una comprobación inicial de datos
        self.full_clean()
        # Si el juego estaba creado...
        if self.status is GameStatus.CREATED:
            if self.mouse_user is None:
                self.status = GameStatus.CREATED
            # ... y se acaba de unir el jugador ratón, empieza el juego
            else:
                self.status = GameStatus.ACTIVE
        if self.status == GameStatus.ACTIVE:
            winner = Game.finish(self)
            if winner:
                self.status = GameStatus.FINISHED

        return super(Game, self).save(*args, **kwargs)

    # Ejemplo de String que respresenta el juego:
    # (3, Active) Cat [X] cat(0, 11, 4, 6) --- Mouse [ ] mouse(52)
    def __str__(self):
        if self.status is None:
            clave = 0
        else:
            clave = self.status
        translate = {str(GameStatus.CREATED): 'Created',
                     str(GameStatus.ACTIVE): 'Active',
                     str(GameStatus.FINISHED): 'Finished'}
        # Construimos la string que representa el juego
        res = ''
        res = res + '(' + str(self.id) + ', ' + translate[str(clave)] + ')'
        res = res + '\t' + 'Cat ['
        if self.cat_turn:
            res += 'X'
        else:
            res += ' '
        res = res + '] ' + self.cat_user.username + '(' + str(self.cat1) + ', '
        res = res + str(self.cat2) + ', ' + str(self.cat3) + ', '
        res = res + str(self.cat4) + ')'
        if self.mouse_user is not None:
            res = res + ' --- Mouse ['
            if self.cat_turn:
                res += ' '
            else:
                res += 'X'
            res = res + '] ' + self.mouse_user.username + '('
            res = res + str(self.mouse) + ')'
        return res


class Move(models.Model):
    # Definimos los campos necesarios para implementar la funcionalidad
    origin = models.IntegerField(blank=True)
    target = models.IntegerField(blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE,
                             related_name='moves')
    player = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='moves')
    date = models.DateTimeField(blank=True, default=timezone.now)

    def save(self, *args, **kwargs):
        # Comprobaciones de errores:
        # No se puede añadir movimientos a una partida no activa
        if self.game.status != GameStatus.ACTIVE:
            raise ValidationError(MSG_ERROR_MOVE)
        # Solo pueden mover los jugadores de la partida
        condition1 = self.player.id != self.game.cat_user.id
        condition2 = self.player.id != self.game.mouse_user.id
        if condition1 and condition2:
            raise ValidationError(MSG_ERROR_MOVE)
        # Solo puede mover el jugador que tiene el turno
        if self.game.cat_turn and self.player.id == self.game.mouse_user.id:
            raise ValidationError(MSG_ERROR_MOVE)
        if not self.game.cat_turn and self.player.id == self.game.cat_user.id:
            raise ValidationError(MSG_ERROR_MOVE)
        new_o = [(self.origin//Game.ROW_LEN)+1, (self.origin % Game.ROW_LEN)+1]
        # Posibles movimientos en diagonal hacia atrás o hacia alante
        valid_targets = [[new_o[0]-1, (new_o[1]-1) % (Game.ROW_LEN + 1)],
                         [new_o[0]-1, (new_o[1]+1) % (Game.ROW_LEN + 1)],
                         [new_o[0]+1, (new_o[1]-1) % (Game.ROW_LEN + 1)],
                         [new_o[0]+1, (new_o[1]+1) % (Game.ROW_LEN + 1)]]
        # Si es gato no puede mover hacia atrás
        if self.game.cat_turn:
            del valid_targets[:2]
        # Quitamos los movimientos que se salen del tablero
        valid_targets_filtered = []
        for t in valid_targets:
            if t[0] <= Game.COL_LEN and t[0] >= 1 and t[1] != 0:
                # Nos quedamos con los movimientos que se quedan dentro del
                # tablero
                valid_targets_filtered.append(t)
        new_t = [(self.target//Game.ROW_LEN)+1, (self.target % Game.ROW_LEN)+1]
        # Si el target no está en la lista de movimientos válidos, excepción
        if new_t not in valid_targets_filtered:
            raise ValidationError(MSG_ERROR_MOVE)
        # No se puede mover una ficha al lugar en el que ya hay otra
        if self.target in [self.game.mouse, self.game.cat1, self.game.cat2,
                           self.game.cat3, self.game.cat4]:
            raise ValidationError(MSG_ERROR_MOVE)
        # No se puede tener un origen donde no haya una de las
        # fichas del jugador
        if self.game.cat_turn:
            auxg = self.game
            if self.origin not in [auxg.cat1, auxg.cat2, auxg.cat3, auxg.cat4]:
                raise ValidationError(MSG_ERROR_MOVE)
            elif self.origin == self.game.cat1:
                self.game.cat1 = self.target
            elif self.origin == self.game.cat2:
                self.game.cat2 = self.target
            elif self.origin == self.game.cat3:
                self.game.cat3 = self.target
            else:
                self.game.cat4 = self.target
        else:
            if self.origin != self.game.mouse:
                raise ValidationError(MSG_ERROR_MOVE)
            self.game.mouse = self.target
        self.game.cat_turn = not self.game.cat_turn
        # Si hay alguna inconsistencia con el game...
        try:
            self.game.save()
        # ...generamos ValidationError
        except ValidationError:
            raise ValidationError(MSG_ERROR_MOVE)
        return super(Move, self).save(*args, **kwargs)

    def __str__(self):
        res = '(' + str(self.game.id) + ') ' + str(self.origin) + ' -> '
        res += str(self.target) + ' ' + self.player.username + ' '
        res += str(self.date)
        return res


# Manager personalizado del Contador
class CounterManager(models.Manager):
    # Interfaz para incrementar la instancia única del contador
    def inc(self):
        c = self.obtain_instance()
        c.value += 1
        super(Counter, c).save()
        # Devolvemos el nuevo valor del contador
        return c.value

    # Interfaz para obtener el valor actual del contador
    def get_current_value(self):
        return self.obtain_instance().value

    # Interfaz para crear u obtener la instancia única del contador
    def obtain_instance(self):
        # Si existe, se lo damos
        try:
            return self.all()[0]
        # Si no existe, lo creamos
        except IndexError:
            c = Counter(id=0)
            super(Counter, c).save()
            # Y lo devolvemos
            return c


# Contador singleton
class Counter(models.Model):

    value = models.IntegerField(blank=True, default=0)
    # Sobrescribimos el manager objects por defecto
    objects = CounterManager()

    # No permitimos que se pueda guardar mediante save
    def save(self, *args, **kwargs):
        raise ValidationError(MSG_ERROR_NEW_COUNTER)
