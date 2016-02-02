from django.conf.urls import patterns, url
from . views import SubscribersIntersection, group_subscribers_update



urlpatterns = patterns('',
    url(r"^$", SubscribersIntersection.as_view(), name="subscribers_intersection"),
    url(r"^group_subscribers_update/$", group_subscribers_update, name="group_subscribers_update"),

)
