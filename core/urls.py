from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/book/", views.book_ride, name="book_ride"),
]
