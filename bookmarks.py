# -*- coding: utf-8 -*-
import glob
import os
import re
import sqlite3
import time
from shutil import copyfile

import alfred

_MAX_RESULTS = 20
_CACHE_EXPIRY = 24 * 60 * 60 # in seconds
_CACHE = alfred.work(True)

def combine(operator, iterable):
    return u'(%s)' % (u' %s ' % operator).join(iterable)

def icon(favicons_db, url_hash):
    if not url_hash:
        return
    
    result = favicons_db.execute(u"""\
select moz_icons.id, moz_icons.data from moz_icons
inner join moz_icons_to_pages on moz_icons.id = moz_icons_to_pages.icon_id
inner join moz_pages_w_icons on moz_icons_to_pages.page_id = moz_pages_w_icons.id
where moz_pages_w_icons.page_url_hash = '%s'
order by moz_icons.id asc limit 1""" % url_hash).fetchone()
    if not result:
        return
    (id, data) = result
    if not data:
        return
    icon = os.path.join(_CACHE, 'icon-%d.png' % id)
    if (not os.path.exists(icon)) or ((time.time() - os.path.getmtime(icon)) > _CACHE_EXPIRY):
        open(icon, 'wb').write(data)
    return icon

def places(profile):
    profile = (d for d in glob.glob(os.path.expanduser(profile)) if os.path.isdir(d)).next()
    orig = os.path.join(profile, 'places.sqlite')
    new = os.path.join(profile, 'places-alfredcopy.sqlite')
    copyfile(orig, new)
    return new

def favicons(profile):
    profile = (d for d in glob.glob(os.path.expanduser(profile)) if os.path.isdir(d)).next()
    orig = os.path.join(profile, 'favicons.sqlite')
    new = os.path.join(profile, 'favicons-alfredcopy.sqlite')
    copyfile(orig, new)
    return new

def regexp(pattern, item):
    return item and bool(re.match(pattern, item, flags=re.IGNORECASE))

def results(places_db, favicons_db, query):
    places_db.create_function("regexp", 2, regexp)
    found = set()
    for result in places_db.execute(sql(query)):
        if result in found:
            continue
        found.add(result)
        (uid, title, url, url_hash) = result
        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url}, title, url, icon(favicons_db, url_hash))

def sql(query):
    keywords = u"""\
select distinct moz_places.id, moz_bookmarks.title, moz_places.url, moz_places.url_hash from moz_places
inner join moz_bookmarks on moz_places.id = moz_bookmarks.fk
inner join moz_keywords on moz_bookmarks.keyword_id = moz_keywords.id
where %s""" % where(query, [u'moz_keywords.keyword'])

    bookmarks = u"""\
select distinct moz_places.id, moz_bookmarks.title, moz_places.url, moz_places.url_hash from moz_places
inner join moz_bookmarks on moz_places.id = moz_bookmarks.fk
where %s""" % where(query, [u'moz_bookmarks.title', u'moz_places.url'])

    input_history = u"""\
select distinct moz_places.id, moz_places.title, moz_places.url, moz_places.url_hash from moz_places
inner join moz_inputhistory on moz_places.id = moz_inputhistory.place_id
where %s""" % where(query, [u'moz_inputhistory.input', u'moz_places.title', u'moz_places.url'])

    browsing_history = u"""\
select distinct moz_places.id, moz_places.title, moz_places.url, moz_places.url_hash from moz_places
inner join moz_historyvisits on moz_places.id = moz_historyvisits.place_id
where %s and moz_places.title notnull""" % where(query, [u'moz_places.title', u'moz_places.url'])

    joinTemplate = u"""\
inner join %(table)s on moz_places.id = %(table)s.%(field)s
"""
    return u'\nunion\n'.join([keywords, bookmarks, input_history, browsing_history])

def where(query, fields):
    return combine(u'or', ('%s regexp "%s"' % (field, '.*%s' % '.*'.join(re.escape(c) for c in query.split(' '))) for field in fields))

(profile, query) = alfred.args()
places_db = sqlite3.connect(places(profile))
favicons_db = sqlite3.connect(favicons(profile))
alfred.write(alfred.xml(results(places_db, favicons_db, query), maxresults=_MAX_RESULTS))
