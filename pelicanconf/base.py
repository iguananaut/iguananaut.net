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
STATIC_PATHS = [
    join('static', 'images'),
    join('pages', 'images')
]

# Pages
PAGE_PATHS = ['pages']
DISPLAY_PAGES_ON_MENU = True

# Theme settings
THEME = 'pelican-clean-blog'
SOCIAL = [
    ('twitter', 'https://twitter.com/iguananaut'),
    ('google-plus', 'https://plus.google.com/+ErikBray'),
    ('linkedin', 'http://www.linkedin.com/pub/erik-bray/19/2a8/a22'),
    ('stack-overflow', 'http://stackoverflow.com/users/982257/iguananaut'),
    ('github', 'https://github.com/embray'),
    ('bitbucket', 'https://bitbucket.com/embray'),
    ('envelope', 'mailto:erik.m.bray@gmail.com')
]
SHOW_SOCIAL_ON_INDEX_PAGE_HEADER = True
EXTRA_TEMPLATES_PATHS = ['includes']
FOOTER_INCLUDE = 'license.html'
DISABLE_CUSTOM_THEME_JAVASCRIPT = True

# Comments and other services
DISQUS_SITENAME = 'iguananaut'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

DEFAULT_PAGINATION = False
