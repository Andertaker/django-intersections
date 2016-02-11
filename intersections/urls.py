from django.conf.urls import patterns, url
from . views import SubscribersIntersection, fetch_group, fetch_group_members_monitor, \
                    get_intersections



urlpatterns = patterns('',
    url(r"^$", SubscribersIntersection.as_view(), name="subscribers_intersection"),
    url(r"^fetch_group/$", fetch_group, name="fetch_group"),
    url(r"^fetch_group_members_monitor/(?P<social>\w+)/(?P<group_id>\d+)/$", fetch_group_members_monitor, name="fetch_group_members_monitor"),
    url(r"^get_intersections/(?P<group_id1>\d+)/(?P<group_id2>\d+)/$", get_intersections, name="get_intersections"),
)
