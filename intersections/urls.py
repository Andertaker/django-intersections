from django.conf.urls import patterns, url
from . views import SubscribersIntersection

urlpatterns = patterns('',
    url(r"^$", SubscribersIntersection.as_view(), name="subscribers_intersection"),
)
