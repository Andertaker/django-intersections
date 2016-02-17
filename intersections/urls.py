from django.conf.urls import patterns, url
from . views import SubscribersIntersection, FetchGroupView, FetchGroupMembersMonitorView, \
                    get_intersections



urlpatterns = patterns('',
    url(r"^$", SubscribersIntersection.as_view(), name="subscribers_intersection"),

    url(r"^fetch_group/$", FetchGroupView.as_view(), name="fetch_group"),

    url(r"^fetch_group_members_monitor/(?P<social>\w+)/(?P<group_id>\d+)/$", FetchGroupMembersMonitorView.as_view(), name="fetch_group_members_monitor"),
    url(r"^get_intersections/(?P<group_id1>\d+)/(?P<group_id2>\d+)/$", get_intersections, name="get_intersections"),
)
