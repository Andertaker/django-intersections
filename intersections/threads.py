import threading

from django.utils import timezone


def get_proccess_by_name(proccess_name):

    for t in threading.enumerate():
        if t.name == proccess_name:
            return t

    return None



class VkFetchGroupMembersThread(threading.Thread):

    group = None
    members_in_db_count = None

    def __init__(self, group, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        self.daemon = True

        self.group = group
        self.members_in_db_count = group.members.count()

    def run(self):
        group = self.group
        offset = self.members_in_db_count

        while True:
            users = group.fetch_members(offset=offset, count=1000)

            if len(users) == 0:
                break

            self.members_in_db_count += len(users) # TO FIX: does't not show real value
            offset += 1000

        group.members_fetched_date = timezone.now()
        group.save()

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
