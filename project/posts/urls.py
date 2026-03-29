from django.urls import path
from posts.views import *

urlpatterns = [
    path('<int:id>', get_post_detail),
]