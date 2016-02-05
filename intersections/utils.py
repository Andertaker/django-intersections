import threading


def get_social(link):
    SOCIALS = {'twitter': 'https://twitter.com',
               'vk': 'https://vk.com',
               'fb': 'https://www.facebook.com',
    }
    for social_name, social_url in SOCIALS.items():
        if link.startswith(social_url):
            return social_name

    return None


def get_proccess_by_name(proccess_name):

    for t in threading.enumerate():
        if t.name == proccess_name:
            return t

    return None



class FetchGroupMembersThread(threading.Thread):

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

        if group.members_count > group.members.count():
            raise Exception("Error occured while fetch members for group %s" % group.pk)
