# -*- coding: utf-8 -*-
import cStringIO
import glob
import os
import sqlite3
import sys
from xml.etree.ElementTree import ElementTree, SubElement, fromstring

UNESCAPE_CHARACTERS = """\\ ()[]{};`'"$"""
FIREFOX_HOME = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Firefox', 'Profiles')

def add(root, uid, title, url):
    item = SubElement(root, 'item', {'uid': uid, 'arg': url})
    for (tag, value) in [('title', title), ('subtitle', url), ('icon', 'icon.png')]:
        subItem = SubElement(item, tag)
        subItem.text = value

def pattern(query):
    return '%'.join([''] + query.split(' ') + [''])

def places():
    profile = [d for d in glob.glob(os.path.join(FIREFOX_HOME, '*.default')) if os.path.isdir(d)][0]
    return os.path.join(profile, 'places.sqlite')

def sql(query):
    return '\nunion\n'.join("""\
select moz_places.id, moz_places.title, moz_places.url
from moz_places
%s
where url like '%s'""" % (join, pattern(query)) for join in [
    'inner join moz_inputhistory on moz_places.id = moz_inputhistory.place_id',
    'inner join moz_bookmarks on moz_places.id = moz_bookmarks.id'
])

def unescape(query):
    for character in UNESCAPE_CHARACTERS:
        query = query.replace('\\%s' % character, character)
    return query

def xml(result):
    tree = ElementTree(fromstring('<items/>'))
    root = tree.getroot()
    for args in result:
        add(root, *args)
    buffer = cStringIO.StringIO()
    buffer.write('<?xml version="1.0"?>\n')
    tree.write(buffer, encoding='utf-8')
    return buffer.getvalue()

query = unescape(sys.argv[1])
db = sqlite3.connect(places())
sys.stdout.write(xml(map(unicode, args) for args in db.execute(sql(query))))
