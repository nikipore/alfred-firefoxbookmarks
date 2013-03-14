alfred-firefoxbookmarks
=======================

This is an Alfred 2 workflow which gives you access to your Firefox bookmarks. In fact, in aims to mimick the awesome bar by scanning not only bookmarks, but also the input history, cf. the `places.db` [scheme](http://people.mozilla.org/~dietrich/places-erd.png).

The `alfred.py` module is a collection of helper functions which ease the communication with Alfred. Everyone is invited to use and improve it for other workflows.

Installation
------------
Download and double-click [Firefox Bookmarks.alfredworkflow](https://github.com/nikipore/alfred-firefoxbookmarks/raw/master/Firefox%20Bookmarks.alfredworkflow).

Usage
-----
Just type `ff <query>`.

Note
----
This workflow looks for the Firefox `places.db` according to your setting of `PROFILE` in the `ff`script filter (it's a glob expression, so the wildcards `*` and `?` are allowed). By default, it points to your default profile.
