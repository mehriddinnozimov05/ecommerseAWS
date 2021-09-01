from os import name
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),

    path("forgotPassword/", views.forgot_password, name="forgot_password"),
    path("resetpassword/", views.reset_password, name="reset_password"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("resetpassword_validate/<uidb64>/<token>/", views.resetpassword_validate, name="reset_password_validate"),

    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("my_orders/<int:order_id>", views.order_detail, name="order_detail"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),

]