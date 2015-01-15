#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import codecs
import os
from os.path import join, abspath

AUTHOR = 'Erik M. Bray'
SITENAME = 'from iguananaut import braindump'
SITESUBTITLE = 'Trying not to be too pretentious here'
SITE_DESCRIPTION = 'Personal blog of Erik M. Bray'
SITEURL = 'http://iguananaut.net'

TIMEZONE = 'America/New_York'

DEFAULT_LANG = 'en'


# Path settings
PATH = join(os.pardir, 'content')
OUTPUT_PATH = join(os.pardir, 'output')

# URL Settings
ARTICLE_URL = 'blog/{category}/{slug}.html'
ARTICLE_SAVE_AS = ARTICLE_URL
STATIC_PATHS = ['images']

# Theme settings
THEME = 'pelican-elegant'
CUSTOM_CSS = True
RECENT_ARTICLES_COUNT = 5
LANDING_PAGE_ABOUT = {
    'title': SITESUBTITLE,
    'details': codecs.open(join('templates', 'about.html'),
                           encoding='utf8').read()
}
SITE_LICENSE = codecs.open(join('templates', 'license.html'),
                           encoding='utf8').read().format(SITENAME=SITENAME)


# Comments and other services
DISQUS_SITENAME = 'iguananaut'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

DEFAULT_PAGINATION = False
