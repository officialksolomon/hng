from django.urls import path
from knox import views as knox_views

from api.views import (AddUserToOrganisationView, GreetingView, LoginView,
                       OrganisationCreateView, OrganisationDetailView,
                       OrganisationListView, RegisterView, UserDetailView)

app_name ='api'
urlpatterns = [
    path("hello/", GreetingView.as_view(), name="hello"),
    path("users/<uuid:id>", UserDetailView.as_view(), name="user-detail"),
    path("organisations", OrganisationListView.as_view(), name="organisation-list"),
    path(
        "organisations/<uuid:pk>",
        OrganisationDetailView.as_view(),
        name="organisation-detail",
    ),
    path("organisations", OrganisationCreateView.as_view(), name="organisation-create"),
    path(
        "organisations/<uuid:orgId>/users",
        AddUserToOrganisationView.as_view(),
        name="add-user-to-organisation",
    ),
     path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/logout", knox_views.LogoutView.as_view(), name="logout"),
    path("auth/logoutall", knox_views.LogoutAllView.as_view(), name="logoutall"),
]
