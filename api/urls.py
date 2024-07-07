from django.urls import path


from api.views import (
    AddUserToOrganisationView,
    GreetingView,
    OrganisationCreateView,
    OrganisationDetailView,
    OrganisationListView,
    UserDetailView,
)

urlpatterns = [
    path("hello/", GreetingView.as_view(), name="hello"),
]

urlpatterns += [
    path("users/<uuid:id>", UserDetailView.as_view(), name="user-detail"),
    path("organisations", OrganisationListView.as_view(), name="organisation-list"),
    path(
        "organisations/<uuid:orgId>",
        OrganisationDetailView.as_view(),
        name="organisation-detail",
    ),
    path("organisations", OrganisationCreateView.as_view(), name="organisation-create"),
    path(
        "organisations/<uuid:orgId>/users",
        AddUserToOrganisationView.as_view(),
        name="add-user-to-organisation",
    ),
]
