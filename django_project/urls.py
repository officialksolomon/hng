from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from knox import views as knox_views

from api.views import LoginView, RegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/", include("api.urls")),
    path("", include("pages.urls")),
    # django-browser_reload
    path("__reload__/", include("django_browser_reload.urls")),
    # auth
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", knox_views.LogoutView.as_view(), name="logout"),
    path("auth/logoutall/", knox_views.LogoutAllView.as_view(), name="logoutall"),
]

urlpatterns += [
    # auth
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/logout", knox_views.LogoutView.as_view(), name="logout"),
    path("auth/logoutall", knox_views.LogoutAllView.as_view(), name="logoutall"),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
