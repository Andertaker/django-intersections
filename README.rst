==================
Django Intersections
==================

Django tool to show groups members intersections for social networks.

Quick start
-----------

First of all, read the installation instructions here:
https://github.com/ramusus/django-twitter-api,
https://github.com/ramusus/django-vkontakte-api

Then add this app to your INSTALLED_APPS setting::

    INSTALLED_APPS = (
        ...
        'oauth_tokens',
        'taggit',
        'vkontakte_api',
        'intersections',
    )

Include the intersections URLs in your project::

    url(r'^intersections/', include('intersections.urls')),
