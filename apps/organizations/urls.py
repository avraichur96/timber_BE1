from django.urls import path
from . import views

urlpatterns = [
    path("", views.organization_list, name="organization_list"),
    path("create/", views.organization_create, name="organization_create"),
    path("<uuid:pk>/", views.organization_detail, name="organization_detail"),
    path(
        "<uuid:pk>/update/",
        views.organization_update,
        name="organization_update",
    ),
    path(
        "<uuid:pk>/members/",
        views.organization_members_list,
        name="organization_members_list",
    ),
    path("subscriptions/", views.subscription_list, name="subscription_list"),
    path(
        "subscriptions/create/",
        views.subscription_create,
        name="subscription_create",
    ),
]
