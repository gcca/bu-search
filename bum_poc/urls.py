from django.urls import path

from .views import PartialSearch, SearchPage

app_name = "bum_poc"

urlpatterns = (
    path("", SearchPage, name="index"),
    path("partial-search/", PartialSearch, name="partial-search"),
)
