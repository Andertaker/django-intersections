from datetime import timedelta
import threading

from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import connection

from annoying.decorators import ajax_request
from vkontakte_api.api import ApiCallError
from vkontakte_groups.models import Group

from . forms import GroupsForm
from . utils import FetchGroupMembersThread, get_proccess_by_name, get_social


GROUP_REFETCH_TIME = timedelta(hours=3)




class SubscribersIntersection(View, TemplateResponseMixin):

    template_name = 'intersections/subscribers_intersection.html'

    def get(self, request):
        return self.render_to_response({'form': GroupsForm})


@csrf_exempt
@ajax_request
def fetch_group(request):
    link = request.POST['link']
    screen_name = link.split('/').pop()

    # get and update group if needed
    group = Group.objects.filter(screen_name=screen_name).first()
    # need to refetch to update members_count parameter
    if not group or group.fetched < timezone.now() - GROUP_REFETCH_TIME:
        try:
            group = Group.remote.fetch(ids=[screen_name])[0]
        except ApiCallError:
            return {'success': False, 'errors': 'Group "%s" not found' % link}


    group = {'id': group.pk,
            'name': group.name,
            'screen_name': group.screen_name,
            'members_count': group.members_count,
            'members_in_db_count': group.members.count(),
            'members_fetched_date': group.members_fetched_date,
    }

    return {'social': get_social(link),
            'group': group,
    }


@ajax_request
def fetch_group_members_monitor(request, social, group_id):

    process_name = "%s_%s_fetch_members_proccess" % (social, group_id)
    thread = get_proccess_by_name(process_name)

    if thread:
        group = thread.group
        status = 'in_progress'
        group_members_in_db_count = thread.members_in_db_count

    else :
        group = Group.objects.filter(pk=group_id).first()
        if not group:
            return {'success': False, 'errors': 'Group "%s %s" not found' % (social, group_id)}

        if not group.members_fetched_date:
            thread = FetchGroupMembersThread(group, name=process_name)
            thread.start()

            status = 'started'
            group_members_in_db_count = thread.members_in_db_count

        else:
            status = 'finished'
            group_members_in_db_count = group.members.count()

    group = {'id': group.pk,
            'name': group.name,
            'screen_name': group.screen_name,
            'members_count': group.members_count,
            'members_in_db_count': group_members_in_db_count,
            'members_fetched_date': group.members_fetched_date,
    }

    return {'status': status,
            'group': group,
    }


@ajax_request
def get_intersections(request, group_id1, group_id2):
    q = '''
        SELECT COUNT(group_id) as cnt, user_id

        FROM vkontakte_groups_group_members
        WHERE group_id IN (%s, %s)
        GROUP BY user_id
        HAVING COUNT(group_id) > 1
    '''

    cursor = connection.cursor()
    cursor.execute(q, [group_id1, group_id2])

    return {'intersections_count': cursor.rowcount}

