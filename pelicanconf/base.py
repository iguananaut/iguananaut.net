#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import codecs
import os
from os.path import join, abspath

AUTHOR = 'Erik M. Bray'
SITENAME = 'from iguananaut import braindump'
SITESUBTITLE = 'a storm drain for my brain'
SITE_DESCRIPTION = 'Personal blog of Erik M. Bray'
SITEURL = 'http://iguananaut.net'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = 'en'


# Path settings
PATH = join(os.pardir, 'content')
OUTPUT_PATH = join(os.pardir, 'output')

# URL Settings
ARTICLE_URL = 'blog/{category}/{slug}.html'
ARTICLE_SAVE_AS = ARTICLE_URL
STATIC_PATHS = ['images']

# Pages
PAGE_PATHS = [join(os.pardir, 'pages')]
DISPLAY_PAGES_ON_MENU = True

# Theme settings
THEME = 'pelican-clean-blog'
SOCIAL = [
    ('twitter', 'https://twitter.com/iguananaut'),
    ('google-plus', 'https://plus.google.com/+ErikBray'),
    ('github', 'https://github.com/embray'),
    ('bitbucket', 'https://bitbucket.com/embray'),
    ('envelope', 'mailto:erik.m.bray@gmail.com')
]
SHOW_SOCIAL_ON_INDEX_PAGE_HEADER = True
EXTRA_TEMPLATES_PATHS = ['includes']
FOOTER_INCLUDE = 'license.html'

# Comments and other services
DISQUS_SITENAME = 'iguananaut'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

DEFAULT_PAGINATION = False
