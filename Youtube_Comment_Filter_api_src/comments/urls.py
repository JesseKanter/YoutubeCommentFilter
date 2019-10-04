from django.conf.urls import url
from comments.views import comments


urlpatterns = [
    url('', comments, name='submission'),
]
