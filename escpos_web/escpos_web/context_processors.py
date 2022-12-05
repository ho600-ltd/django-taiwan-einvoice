#!/usr/bin/python
import re, datetime
from django.conf import settings as dj_settings



def settings(R):
    try: from __version__ import version
    except ImportError: version = 'LOCAL_DEBUG'
    try: from __version__ import BUILD_URL
    except ImportError: BUILD_URL = 'NO_BUILD_URL'
    if version == 'LOCAL_DEBUG':
        version = R.META.get('CURRENT_VERSION_ID', '__ondjangoserver__')
        if version != '__djangoserver__':
            r = re.match('[^-]+-([^-]+)-.*-([^-]+)\.[0-9]+', version)
            if not r: version = '__version__'
            else: version = '-'.join(r.groups())
    d = {}
    for k in dir(dj_settings):
        d[k] = getattr(dj_settings, k)
    d['BUILD_URL'] = BUILD_URL
    d['version'] = version
    d['now'] = datetime.datetime.now()
    _d = {}
    for k, v in d.items():
        if 'key' in k.lower() or 'secret' in k.lower() or 'pass' in k.lower():
            v = re.sub('(.(.))', r'*\2', str(v))
        _d[k] = v
    return {'settings': _d}