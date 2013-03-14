import cStringIO
import itertools
import os
import plistlib
import unicodedata
import sys

from xml.etree.ElementTree import ElementTree, SubElement, fromstring

_MAX_RESULTS = 9
_UNESCAPE_CHARACTERS = u'\\ ()[]{};`"$'

PREFERENCES = plistlib.readPlist('info.plist')
BUNDLE_ID = PREFERENCES['bundleid']

def args():
    return tuple(unescape(decode(arg)) for arg in sys.argv[1:])

def decode(s):
    return unicodedata.normalize('NFC', s.decode('utf-8'))

def item(root, uid, arg, title, subtitle, icon):
    item = SubElement(root, u'item', {u'uid': uid, u'arg': arg})
    for (tag, value) in [(u'title', title), (u'subtitle', subtitle), (u'icon', icon)]:
        SubElement(item, tag).text = value

def path(volatile):
    path = {
        True: '~/Library/Caches/com.runningwithcrayons.Alfred-2/Workflow Data',
        False: '~/Library/Application Support/Alfred 2/Workflow Data'
    }[bool(volatile)]
    path = os.path.join(os.path.expanduser(path), BUNDLE_ID)
    if not os.access(path, os.R_OK):
        os.mkdir(path)
    if not os.access(path, os.W_OK):
        raise IOError('No write access to path: %s' % path)
    return path

def unescape(query, characters=None):
    for character in (_UNESCAPE_CHARACTERS if (characters is None) else characters):
        query = query.replace('\\%s' % character, character)
    return query

def write(text):
    sys.stdout.write(text)

def xml(result):
    tree = ElementTree(fromstring('<items/>'))
    root = tree.getroot()
    for args in itertools.islice(result, _MAX_RESULTS):
        item(root, *map(unicode, args))
    buffer = cStringIO.StringIO()
    buffer.write('<?xml version="1.0"?>\n')
    tree.write(buffer, encoding='utf-8')
    return buffer.getvalue()
