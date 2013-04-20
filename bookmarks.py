# -*- coding: utf-8 -*-
import glob
import os
import sqlite3
import time

import alfred

_MAX_RESULTS = 20
_CACHE_EXPIRY = 24 * 60 * 60 # in seconds
_CACHE = alfred.work(True)

def combine(operator, iterable):
    return u'(%s)' % (u' %s ' % operator).join(iterable)

def icon(db, faviconid):
    if not faviconid:
        return
    data = db.execute(u'select data from moz_favicons where id=%d' % faviconid).fetchone()[0]
    icon = os.path.join(_CACHE, 'icon-%d.png' % faviconid)
    if (not os.path.exists(icon)) or ((time.time() - os.path.getmtime(icon)) > _CACHE_EXPIRY):
        open(icon, 'wb').write(data)
    return icon

def places(profile):
    profile = [d for d in glob.glob(os.path.expanduser(profile)) if os.path.isdir(d)][0]
    return os.path.join(profile, 'places.sqlite')

def results(db, query):
    found = set()
    for result in db.execute(sql(query)):
        if result in found:
            continue
        found.add(result)
        (uid, title, url, faviconid) = result
        yield alfred.Item({u'uid': alfred.uid(uid), u'arg': url}, title, url, icon(db, faviconid))

def sql(query):
    bookmarks = u"""\
select distinct moz_places.id, moz_bookmarks.title, moz_places.url, moz_places.favicon_id from moz_places
inner join moz_bookmarks on moz_places.id = moz_bookmarks.fk
where %s
""" % where(query, [u'moz_bookmarks.title', u'moz_places.url'])

    history = u"""\
select distinct moz_places.id, moz_places.title, moz_places.url, moz_places.favicon_id from moz_places
inner join moz_inputhistory on moz_places.id = moz_inputhistory.place_id
where %s
""" % where(query, [u'moz_inputhistory.input', u'moz_places.title', u'moz_places.url'])
    joinTemplate = u"""\
inner join %(table)s on moz_places.id = %(table)s.%(field)s
"""
    return u' union '.join([bookmarks, history])

def where(query, fields):
    words = [word.replace(u"'", u"''") for word in query.split(u' ')]
    return combine(u'or', (
        combine(u'and', ((u"(%s like '%%%s%%')" % (field, word)) for word in words))
        for field in fields)
    )

(profile, query) = alfred.args()
db = sqlite3.connect(places(profile))
alfred.write(alfred.xml(results(db, query), maxresults=_MAX_RESULTS))
