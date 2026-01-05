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
    path("customers/", views.CustomerListCreateView.as_view(), name="customer_list_create"),
    path(
        "customers/<uuid:pk>/",
        views.CustomerRetrieveUpdateDestroyView.as_view(),
        name="customer_detail",
    ),
    path("projects/", views.ProjectListCreateView.as_view(), name="project_list_create"),
    path(
        "projects/<uuid:pk>/",
        views.ProjectRetrieveUpdateDestroyView.as_view(),
        name="project_detail",
    ),
    path("estimate-headers/", views.EstimateHeaderListCreateView.as_view(), name="estimate_header_list_create"),
    path(
        "estimate-headers/<uuid:pk>/",
        views.EstimateHeaderRetrieveUpdateDestroyView.as_view(),
        name="estimate_header_detail",
    ),
    path("products/", views.ProductListCreateView.as_view(), name="product_list_create"),
    path(
        "products/<uuid:pk>/",
        views.ProductRetrieveUpdateDestroyView.as_view(),
        name="product_detail",
    ),
    path("job-cards/", views.JobCardListCreateView.as_view(), name="job_card_list_create"),
    path(
        "job-cards/<uuid:pk>/",
        views.JobCardRetrieveUpdateDestroyView.as_view(),
        name="job_card_detail",
    ),
]
