#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import codecs
import os
from os.path import join

AUTHOR = 'Erik M. Bray'
SITENAME = 'Iguananaut.net'
SITESUBTITLE = 'Trying not to be too pretentious here'
SITE_DESCRIPTION = 'Personal blog of Erik M. Bray'
SITEURL = 'http://iguananaut.net'

TIMEZONE = 'US/East'

DEFAULT_LANG = 'en'


# Path settings
PATH = join(os.pardir, 'content')
OUTPUT_PATH = join(os.pardir, 'output')


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
                           encoding='utf8').read()

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

DEFAULT_PAGINATION = False
