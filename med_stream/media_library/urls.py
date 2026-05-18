from django.urls import path
from .views import MediaList, AddMedia

urlpatterns = [
    path("media_list/", MediaList, name="media_list"),
    path("add_media/", AddMedia, name="add_media"),
]
