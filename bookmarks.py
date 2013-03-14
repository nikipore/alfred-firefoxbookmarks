# -*- coding: utf-8 -*-
import glob
import os
import sqlite3

import alfred

def combine(operator, iterable):
    return u'(%s)' % (' %s ' % operator).join(iterable)

def places(profile):
    profile = [d for d in glob.glob(os.path.expanduser(profile)) if os.path.isdir(d)][0]
    return os.path.join(profile, 'places.sqlite')

def result(db, query):
    return (
        (uid, url, title, url, u'icon.png') for (uid, title, url) in
        (item[:3] for item in db.execute(sql(query)))
    )

def sql(query):
    return u"""\
%s
order by visit_count desc""" % u'\nunion\n'.join(u"""\
select moz_places.id, moz_places.title, moz_places.url, moz_places.visit_count from moz_places
%s
where %s""" % (join, where(query)) for join in (
        u'inner join %(table)s on moz_places.id = %(table)s.%(field)s' % locals()
        for (table, field) in [(u'moz_inputhistory', u'place_id'), (u'moz_bookmarks', u'id')]
    ))

def where(query):
    return combine(u'or', (
        combine(u'and', ((u"(moz_places.%s like '%%%s%%')" % (field, word)) for word in query.split(u' ')))
        for field in (u'title', u'url'))
    )


(profile, query) = alfred.args()
db = sqlite3.connect(places(profile))
alfred.write(alfred.xml(result(db, query)))
