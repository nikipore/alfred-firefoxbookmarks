# -*- coding: utf-8 -*-
import cStringIO
import glob
import os
import sqlite3
import sys
import unicodedata

from xml.etree.ElementTree import ElementTree, SubElement, fromstring

FIREFOX_HOME = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Firefox', 'Profiles')
UNESCAPE_CHARACTERS = """\\ ()[]{};`"$"""

def add(root, uid, title, url):
    item = SubElement(root, 'item', {'uid': uid, 'arg': url})
    for (tag, value) in [('title', title), ('subtitle', url), ('icon', 'icon.png')]:
        SubElement(item, tag).text = value

def combine(operator, iterable):
    return u'(%s)' % (' %s ' % operator).join(iterable)

def decode(s):
    return unicodedata.normalize('NFC', s.decode('utf-8'))

def places():
    profile = [d for d in glob.glob(os.path.join(FIREFOX_HOME, '*.default')) if os.path.isdir(d)][0]
    return os.path.join(profile, 'places.sqlite')

def sql(query):
    return u'\nunion\n'.join(u"""\
select moz_places.id, moz_places.title, moz_places.url from moz_places
%s
where %s""" % (join, where(query)) for join in (
        u'inner join %(table)s on moz_places.id = %(table)s.%(field)s' % locals()
        for (table, field) in [(u'moz_inputhistory', u'place_id'), (u'moz_bookmarks', u'id')]
    ))

def unescape(query):
    for character in UNESCAPE_CHARACTERS:
        query = query.replace('\\%s' % character, character)
    return query

def where(query):
    return combine(u'or', (
        combine(u'and', ((u"(moz_places.%s like '%%%s%%')" % (field, word)) for word in query.split(u' ')))
        for field in (u'title', u'url'))
    )

def xml(result):
    tree = ElementTree(fromstring('<items/>'))
    root = tree.getroot()
    for args in result:
        add(root, *map(unicode, args))
    buffer = cStringIO.StringIO()
    buffer.write('<?xml version="1.0"?>\n')
    tree.write(buffer, encoding='utf-8')
    return buffer.getvalue()

query = unescape(decode(sys.argv[1]))
db = sqlite3.connect(places())
sys.stdout.write(xml(db.execute(sql(query))))
