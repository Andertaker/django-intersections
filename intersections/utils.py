import re



GROUPS_RE = {'twitter': re.compile(r'^https?://twitter.com/([\w\d\_]+)/?$'),
           'vk': re.compile(r'^https?://vk.com/([\w\d\_]+)/?$'),
           'instagram': re.compile(r'^https?://www.instagram.com/([\w\d\_]+)/?$'),
}


def get_social(link):
    SOCIALS = {'twitter': 'https://twitter.com',
               'vk': 'https://vk.com',
               # 'fb': 'https://www.facebook.com',
               'instagram': 'https://www.instagram.com',
    }
    for social_name, social_url in SOCIALS.items():
        if link.startswith(social_url):
            return social_name

    return None


def get_screen_name(link):
    social = get_social(link)
    group_re = GROUPS_RE[social]

    m = group_re.match(link)
    if m:
        return m.group(1)

    return None


def members_last_update_time(qs):
    '''
        group = Group.objects.first()
        print members_last_update_time(group.members)

    '''

    version = qs.versions.last()
    if version:
        return version.time

    return None
