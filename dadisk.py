#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import cgi
import os
import pystache
import re
import urllib.parse
import human_readable
import sys
from pprint import pformat

import vlccontroller

LOGINUSER = 'nrh'
DEVNULL = open('/dev/null', 'w')
DIR = '/Volumes/Media'
MEDIAEXT = ('m4v', 'avi', 'wmv', 'mp4', 'mkv', 'flv', 'mov', 'asf', 'mpg')
SKIP = ('Desktop DB', 'Desktop DF')
ROOTURI = '/~%s/' % LOGINUSER
VLCPASS = 'admin'


class Request(object):
    def __init__(self, form=None, vc=None):
        self.form = cgi.FieldStorage()
        self.dir = self.form.getfirst('dir') or '/'
        self.safe_dir = urllib.parse.quote_plus(self.dir, safe='/')
        self.action = self.form.getfirst('action') or "list"
        self.file = self.form.getfirst('file') or None
        self.fsdir = os.sep.join((DIR,
                                 self.dir)).replace('//', '/').rstrip('/')
        self.parts = self.dir.replace('//', '/').rstrip('/').split('/')
        self.debug = self.form.getfirst('debug') or False
        self.roottarget = ROOTURI
        self.rootname = '<root>'
        self.sortby = self.form.getfirst('sort') or 'D'
        self.vc = vc
        self.title = '/' if self.dir == '/' else '/ ' + self.dir

    def nextsort_date(self):
        if self.sortby == 'D':
            return 'd'
        return 'D' if self.sortby == 'd' else 'D'

    def nextsort_size(self):
        if self.sortby == 'S':
            return 's'
        return 'S' if self.sortby == 's' else 'S'

    def nextsort_name(self):
        if self.sortby == 'N':
            return 'n'
        return 'N' if self.sortby == 'n' else 'N'

    def realdir(self):
        if self.dir == '/':
            return ''
        else:
            return self.dir

    def displaydir(self):
        if self.dir == '/':
            return '<root>'
        return self.dir

    def rootactive(self):
        if self.dir == '/':
            return False
        else:
            return 'active'

    def safe_prev_dir(self, numparts=0):
        return urllib.parse.quote_plus(os.sep.join(self.parts[0:numparts]),
                                 safe='/')

    def subtitles(self):
        set = []
        foo = self.vc.get_subtitle_tracks()
        for tuple in foo[0]:
            selected = True if foo[1] == tuple[1] else False
            set.append({"name": tuple[0], "index": tuple[1],
                        "selected": selected})

        return set

    def pprint(self):
        return pformat(vars(self))

    def breadcrumb(self):
        items = []

        for i in range(len(self.parts) - 1):
            items.append({'name': self.parts[i],
                          'target': self.safe_prev_dir(i + 1)})

        items.append({'class': 'active', 'name': self.parts[-1]})
        return items

    def rows(self):

        items = []
        if self.sortby.lower() == 'n':
            items = sorted(os.listdir(self.fsdir), key=str.lower)
        elif self.sortby.lower() == 'd':
            items = sorted(os.listdir(self.fsdir),
                           key=lambda f: os.stat(
                               os.sep.join((self.fsdir, f))).st_mtime)
        elif self.sortby.lower() == 's':
            items = sorted(os.listdir(self.fsdir),
                           key=lambda f: os.stat(
                               os.sep.join((self.fsdir, f))).st_size)
        if self.sortby.isupper():
            items = reversed(items)

        rows = []
        for thing in items:
            path = os.sep.join((self.fsdir, thing))

            if thing == "":
                continue
            if re.match('^\.', thing):
                continue
            if not os.access(path, os.R_OK):
                continue

            if os.path.isdir(path):
                target = os.sep.join((self.realdir(),
                                      thing)).lstrip('/').rstrip('/')
                safe_target = urllib.parse.quote_plus(target, safe='/')
                ts = human_readable.date(os.stat(path)[8])
                rows.append({'isdir': 1,
                             'colspan': 2,
                             'target': safe_target,
                             'ts': ts,
                             'name': thing})
            elif os.path.isfile(path):
                if thing in SKIP:
                    continue

                ext = path.rsplit('.')[-1:]
                size = human_readable.size(os.path.getsize(path))
                ts = human_readable.date(os.stat(path)[8])

                if ext[0].lower() in MEDIAEXT:
                    target = os.sep.join((self.dir, thing))
                    safe_target = urllib.parse.quote_plus(target, safe='/')
                    rows.append({'ismedia': 1,
                                 'target': safe_target,
                                 'name': thing,
                                 'ts': ts,
                                 'size': size})
                else:
                    rows.append({'isother': 1,
                                 'name': thing,
                                 'ts': ts,
                                 'size': size})
        return rows

    def nowplaying(self):
        title = self.vc.title()
        if title:
            return {'name': title,
                    'length': human_readable.timestamp(self.vc.length()),
                    'time': human_readable.timestamp(self.vc.time())}
        return None


def main():

    sys.stdout.buffer.write(b'Content-type: text/html; charset=utf-8\n\n')
    vc = vlccontroller.VLCController(password=VLCPASS)
    vc.connect()
    request = Request(vc=vc)
    renderer = pystache.Renderer()

    if request.action == 'toggle_play':
        vc.pause()
        return

    if request.action == 'toggle_subs':
        vc.set_subtitle_track(-1)
        return

    if request.action == 'play':
        target = os.sep.join((DIR, urllib.parse.unquote_plus(request.form.getfirst('target'))))
        vc.clear()
        vc.add(target)
        vc.play()
        return

    if request.action == 'enqueue':
        target = os.sep.join((DIR, urllib.parse.unquote_plus(request.form.getfirst('target'))))
        vc.enqueue(target)
        return

    sys.stdout.buffer.write(renderer.render_name('dadisk.html', request).encode('utf-8'))
    return

if __name__ == '__main__':
    main()
