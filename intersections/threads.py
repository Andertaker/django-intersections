import threading

from django.utils import timezone

from vkontakte_api.api import api_call
from vkontakte_users.models import User
from vkontakte_users.signals import users_to_fetch, fetch_users


def get_proccess_by_name(proccess_name):

    for t in threading.enumerate():
        if t.name == proccess_name:
            return t

    return None



class VkFetchGroupMembersThread(threading.Thread):

    group = None
    members_in_db_count = None
    _user_ids = []

    def __init__(self, group, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.daemon = True

        self.group = group
        self.members_in_db_count = 0 # group.members.count()
        self._user_ids = []

    def fetch_members(self, group, offset=0, count=1000):
        response = api_call('groups.getMembers', group_id=group.pk,
                            fields='first_name,last_name,sex,bdate,country,city',
                            offset=offset, count=count, v=5.9)
        users = User.remote.parse_response_users(response, items_field='items')
        ids = [u.pk for u in users]
        return ids

    def run(self):
        group = self.group
        offset = self.members_in_db_count

        while True:
            ids = self.fetch_members(group, offset=offset, count=1000)
            self._user_ids += ids
            self.members_in_db_count += len(ids)
            offset += 1000

            if len(ids) < 1000:
                break

        # save users
        users_to_fetch.disconnect(receiver=fetch_users) # prevent fetch users work
        group.members = self._user_ids

        if group.members_count > group.members.count():
            raise Exception("Error occured while fetch members for group %s" % group.pk)


class TwitterFetchFollowersThread(threading.Thread):

    user = None
    followers_in_db_count = None

    def __init__(self, user, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.daemon = True

        self.user = user
        self.followers_in_db_count = user.followers.count()

    def run(self):
        user = self.user
        user.fetch_followers(all=True)

        if user.followers_count > user.followers.count():
            raise Exception("Error occured while fetch followers for user %s" % user.pk)
