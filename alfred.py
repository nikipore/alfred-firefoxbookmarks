import cStringIO
import itertools
import unicodedata
import sys

from xml.etree.ElementTree import ElementTree, SubElement, fromstring

MAX_RESULTS = 9
UNESCAPE_CHARACTERS = u'\\ ()[]{};`"$'

def args():
    return tuple(unescape(decode(arg)) for arg in sys.argv[1:])

def decode(s):
    return unicodedata.normalize('NFC', s.decode('utf-8'))

def item(root, uid, arg, title, subtitle, icon):
    item = SubElement(root, u'item', {u'uid': uid, u'arg': arg})
    for (tag, value) in [(u'title', title), (u'subtitle', subtitle), (u'icon', icon)]:
        SubElement(item, tag).text = value

def unescape(query):
    for character in UNESCAPE_CHARACTERS:
        query = query.replace('\\%s' % character, character)
    return query

def write(text):
    sys.stdout.write(text)

def xml(result):
    tree = ElementTree(fromstring('<items/>'))
    root = tree.getroot()
    for args in itertools.islice(result, MAX_RESULTS):
        item(root, *map(unicode, args))
    buffer = cStringIO.StringIO()
    buffer.write('<?xml version="1.0"?>\n')
    tree.write(buffer, encoding='utf-8')
    return buffer.getvalue()
