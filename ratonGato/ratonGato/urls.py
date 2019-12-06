"""ratonGato URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from logic import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='landing'),
    path('index/', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('counter/', views.counter, name='counter'),
    path('create_game/', views.create_game, name='create_game'),
    path('select_game/<str:type>', views.select_game, name='select_game'),
    path('select_game/<str:type>/<int:game_id>', views.select_game, name='select_game'),
    path('show_game/<str:type>', views.show_game, name='show_game'),
    path('move/', views.move, name='move'),
    path('errorHTTP/', views.errorHTTP, name='errorHTTP'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
