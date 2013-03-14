# -*- coding: utf-8 -*-
import glob
import os
import sqlite3
import time

import alfred

_CACHE = alfred.work(True)

def combine(operator, iterable):
    return u'(%s)' % (' %s ' % operator).join(iterable)

def icon(uid, data, expiration):
    icon = os.path.join(_CACHE, 'icon-%d.png' % uid)
    expired = (expiration / 1000000.0) > time.time()
    if expired or not os.path.exists(icon):
        open(icon, 'wb').write(data)
    return icon

def places(profile):
    profile = [d for d in glob.glob(os.path.expanduser(profile)) if os.path.isdir(d)][0]
    return os.path.join(profile, 'places.sqlite')

def results(db, query):
    for (uid, title, url, data, expiration) in db.execute(sql(query)):
        yield alfred.result(uid, url, title, url, icon(uid, data, expiration))

def sql(query):
    subqueryTemplate = u"""\
select moz_places.id, moz_places.title, moz_places.url, moz_favicons.data, moz_favicons.expiration from moz_places
%s
where %s"""
    joinTemplate = u"""\
inner join %(table)s on moz_places.id = %(table)s.%(field)s
inner join moz_favicons on moz_places.favicon_id = moz_favicons.id"""
    tablesAndFields = [(u'moz_inputhistory', u'place_id'), (u'moz_bookmarks', u'id')]
    return u'\nunion\n'.join(
        subqueryTemplate % (joinTemplate % locals(), where(query))
        for (table, field) in tablesAndFields
    )

def where(query):
    return combine(u'or', (
        combine(u'and', ((u"(moz_places.%s like '%%%s%%')" % (field, word)) for word in query.split(u' ')))
        for field in (u'title', u'url'))
    )

(profile, query) = alfred.args()
db = sqlite3.connect(places(profile))
alfred.write(alfred.xml(results(db, query)))
