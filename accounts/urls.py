
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register_api, name="register"),
    path("login/", views.login_api, name="login"),
    path("refresh/", views.refresh_api, name="refresh"),
    path("logout/", views.logout_api, name="logout"),

    path("page/register/", views.register_page, name="register-page"),
    path("page/login/", views.login_page, name="login-page"),
]
