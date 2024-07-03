from django.urls import path

from api.views import GreetingView

urlpatterns = [
    path("hello/", GreetingView.as_view(), name="hello"),
]
