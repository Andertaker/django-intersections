from datetime import timedelta
import threading

from django.views.generic import View
from django.views.generic.base import TemplateResponseMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import connection

from vkontakte_api.api import ApiCallError
from vkontakte_groups.models import Group
from tweepy import TweepError
from twitter_api.models import User
from instagram_api.models import User as InstagramUser

from . decorators import ajax_request
from . forms import GroupsForm
from . utils import get_social, get_screen_name, members_last_update_time
from . threads import VkFetchGroupMembersThread, TwitterFetchFollowersThread, \
                    InstagramFetchFollowersThread, get_proccess_by_name


GROUP_REFETCH_TIME = timedelta(hours=3)



class SubscribersIntersection(View, TemplateResponseMixin):

    template_name = 'intersections/subscribers_intersection.html'

    def get(self, request):
        return self.render_to_response({'form': GroupsForm})



class FetchGroupView(View):

    @csrf_exempt
    @ajax_request
    def dispatch(self, request, *args, **kwargs):
        return super(FetchGroupView, self).dispatch(request, *args, **kwargs)

    def post(self, request):
        link = request.POST['link']
        social = get_social(link)
        screen_name = get_screen_name(link)
        group = None

        if not social:
            return {'success': False, 'errors': 'This social network is not supported'}
        if not screen_name:
            return {'success': False, 'errors': 'Invalid link'}

        if social == 'vk':
            group = self.vk_fetch_group(screen_name)
        elif social == 'twitter':
            group = self.twitter_fetch_user(screen_name)
        elif social == 'instagram':
            group = self.instagram_fetch_user(screen_name)

        if not group:
            return {'success': False, 'errors': 'Group "%s" not found' % screen_name}

        return {'social': social,
                'group': group,
        }

    def vk_fetch_group(self, screen_name):

        # get and update group if needed
        group = Group.objects.filter(screen_name=screen_name).first()
        # need to refetch to update members_count parameter
        if not group or group.fetched < timezone.now() - GROUP_REFETCH_TIME:
            try:
                group = Group.remote.fetch(ids=[screen_name])[0]
            except ApiCallError:
                return None

        return {'id': group.pk,
                'name': group.name,
                'screen_name': group.screen_name,
                'members_count': group.members_count,
                'members_in_db_count': group.members.count(),
                'members_fetched_date': members_last_update_time(group.members),
        }

    def twitter_fetch_user(self, screen_name):
        user = User.objects.filter(screen_name=screen_name).first()

        if not user or user.fetched < timezone.now() - GROUP_REFETCH_TIME:
            try:
                user = User.remote.fetch(screen_name)
            except TweepError:
                return None

        return {'id': user.pk,
                'name': user.name,
                'screen_name': user.screen_name,
                'members_count': user.followers_count,
                'members_in_db_count': user.followers.count(),
                'members_fetched_date': members_last_update_time(user.followers),
        }

    def instagram_fetch_user(self, username):
        user = InstagramUser.objects.filter(username=username).first()

        if not user or user.fetched < timezone.now() - GROUP_REFETCH_TIME:
            try:
                user = InstagramUser.remote.fetch_by_slug(username)
            except ValueError:
                return None

        return {'id': user.pk,
                'name': user.full_name,
                'screen_name': user.username,
                'members_count': user.followers_count,
                'members_in_db_count': user.followers.count(),
                'members_fetched_date': members_last_update_time(user.followers),
        }


class FetchGroupMembersMonitorView(View):

    @ajax_request
    def get(self, request, social, group_id):
        return getattr(self, '%s_monitor' % social)(group_id)


    def vk_monitor(self, group_id):

        process_name = "vk_%s_fetch_members_proccess" % group_id
        thread = get_proccess_by_name(process_name)

        if thread:
            group = thread.group
            status = 'in_progress'
            group_members_in_db_count = thread.members_in_db_count

        else :
            group = Group.objects.filter(pk=group_id).first()
            if not group:
                return {'success': False, 'errors': 'Vk Group "%s" not found' % group_id}

            if not members_last_update_time(group.members):
                thread = VkFetchGroupMembersThread(group, name=process_name)
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
                'members_fetched_date': members_last_update_time(group.members),
        }

        return {'status': status,
                'group': group,
        }

    def twitter_monitor(self, group_id): # user_id

        process_name = "twitter_%s_fetch_members_proccess" % group_id
        thread = get_proccess_by_name(process_name)

        if thread:
            group = thread.user
            status = 'in_progress'
            group_members_in_db_count = thread.followers_in_db_count
            members_fetched_date = members_last_update_time(group.followers)

        else :
            group = User.objects.filter(pk=group_id).first()
            if not group:
                return {'success': False, 'errors': 'Twitter User "%s" not found' % group_id}

            members_fetched_date = members_last_update_time(group.followers)
            if not members_fetched_date:
                thread = TwitterFetchFollowersThread(group, name=process_name)
                thread.start()

                status = 'started'
                group_members_in_db_count = thread.followers_in_db_count

            else:
                status = 'finished'
                group_members_in_db_count = group.followers.count()

        group = {'id': group.pk,
                'name': group.name,
                'screen_name': group.screen_name,
                'members_count': group.followers_count,
                'members_in_db_count': group_members_in_db_count,
                'members_fetched_date': members_fetched_date,
        }

        return {'status': status,
                'group': group,
        }

    def instagram_monitor(self, group_id): # user_id

        process_name = "instagram_%s_fetch_members_proccess" % group_id
        thread = get_proccess_by_name(process_name)

        if thread:
            group = thread.user
            status = 'in_progress'
            group_members_in_db_count = thread.followers_in_db_count
            members_fetched_date = members_last_update_time(group.followers)

        else :
            group = InstagramUser.objects.filter(pk=group_id).first()
            if not group:
                return {'success': False, 'errors': 'Instagram User "%s" not found' % group_id}

            members_fetched_date = members_last_update_time(group.followers)
            if not members_fetched_date:
                thread = InstagramFetchFollowersThread(group, name=process_name)
                thread.start()

                status = 'started'
                group_members_in_db_count = thread.followers_in_db_count

            else:
                status = 'finished'
                group_members_in_db_count = group.followers.count()

        group = {'id': group.pk,
                'name': group.full_name,
                'screen_name': group.username,
                'members_count': group.followers_count,
                'members_in_db_count': group_members_in_db_count,
                'members_fetched_date': members_fetched_date,
        }

        return {'status': status,
                'group': group,
        }


class GetIntersectionsView(View):
    vk_query = '''
        SELECT COUNT(group_id) as cnt, user_id

        FROM vkontakte_groups_group_members
        WHERE group_id IN (%s, %s) AND time_to IS NULL
        GROUP BY user_id
        HAVING COUNT(group_id) > 1
    '''

    twitter_query = '''
        SELECT COUNT(from_user_id) as cnt, to_user_id

        FROM twitter_api_user_followers
        WHERE from_user_id IN (%s, %s) AND time_to IS NULL
        GROUP BY to_user_id
        HAVING COUNT(from_user_id) > 1
    '''

    @ajax_request
    def get(self, request, social, group_id1, group_id2):
        q = getattr(self, '%s_query' % social)

        cursor = connection.cursor()
        cursor.execute(q, [group_id1, group_id2])

        return {'intersections_count': cursor.rowcount}
