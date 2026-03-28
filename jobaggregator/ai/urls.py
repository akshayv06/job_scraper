from django.urls import path
from .views import agent_view

urlpatterns = [
    path("agent/", agent_view),
]