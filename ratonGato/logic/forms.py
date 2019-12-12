from django import forms
from django.core.validators import MinLengthValidator, MinValueValidator
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from datamodel.models import Move, Game

OUT_OF_RANGE = "Target should be in the range {0}-{1}".format(Game.MIN_CELL,
                                                              Game.MAX_CELL)
SIGNUP_ERROR_AUTH_PASSWORD = "Password is too short. Password should\
                              be at least 6 characters. Password is too common"


# Formulario de registro
class SignupForm(forms.ModelForm):
    # Se capta la contraseña y su confirmación como campos de contraseña
    # con validación de longitud mínima de 6 caracteres
    password = forms.CharField(validators=[MinLengthValidator(6,
                                           SIGNUP_ERROR_AUTH_PASSWORD)],
                               widget=forms.PasswordInput())
    password2 = forms.CharField(label='Repeat Password',
                                widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'password')


# Formulario de login
class LoginForm(forms.ModelForm):
    # Se capta la contraseña como campos de contraseña
    password = forms.CharField(widget=forms.PasswordInput())
    username = forms.CharField(help_text=False)

    class Meta:
        model = User
        fields = ('username', 'password')


# Formulario de movimiento
class MoveForm(forms.ModelForm):
    # Se captan el origen y el destino con una comprobación inicial de que
    # están dentro de los límites del tablero
    origin = forms.IntegerField(validators=[MinValueValidator(
                                            Game.MIN_CELL, OUT_OF_RANGE),
                                            MaxValueValidator(
                                            Game.MAX_CELL, OUT_OF_RANGE)],
                                widget=forms.HiddenInput())
    target = forms.IntegerField(validators=[MinValueValidator(
                                            Game.MIN_CELL, OUT_OF_RANGE),
                                            MaxValueValidator(
                                            Game.MAX_CELL, OUT_OF_RANGE)],
                                widget=forms.HiddenInput())

    class Meta:
        model = Move
        fields = ('origin', 'target')
