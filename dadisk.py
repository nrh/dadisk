#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import cgi
import os
import pystache
import re
import urllib
import vlccontroller
from pprint import pformat

LOGINUSER = 'nrh'
DEVNULL = open('/dev/null', 'w')
DIR = "/Media"
MEDIAEXT = ('m4v', 'avi', 'wmv', 'mp4', 'mkv')
SKIP = ('Desktop DB', 'Desktop DF')
ROOTURI = '/~%s/' % LOGINUSER
VLCPASS = 'dickbutt'


class Request(object):
    def __init__(self, form=None, vc=None):
        self.form = cgi.FieldStorage()
        self.dir = self.form.getfirst('dir') or '/'
        self.safe_dir = urllib.quote_plus(self.dir, safe='/')
        self.action = self.form.getfirst('action') or "list"
        self.file = self.form.getfirst('file') or None
        self.fsdir = os.sep.join((DIR,
                                 self.dir)).replace('//', '/').rstrip('/')
        self.parts = self.dir.replace('//', '/').rstrip('/').split('/')
        self.debug = self.form.getfirst('debug') or False
        self.roottarget = ROOTURI
        self.rootname = '<root>'
        self.vc = vc

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
        return urllib.quote_plus(os.sep.join(self.parts[0:numparts]),
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
        def human_readable_size(s):
            for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if s < 1024.0:
                    return "%3.1f %s" % (s, x)
                s /= 1024.0
            return "%3.1f" % s

        rows = []
        for thing in os.listdir(self.fsdir):
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
                safe_target = urllib.quote_plus(target, safe='/')
                rows.append({'isdir': 1,
                             'colspan': 2,
                             'target': safe_target,
                             'name': thing})
            elif os.path.isfile(path):
                if thing in SKIP:
                    continue

                ext = path.rsplit('.')[-1:]
                size = human_readable_size(os.path.getsize(path))
                if ext[0] in MEDIAEXT:
                    target = os.sep.join((self.dir, thing))
                    rows.append({'ismedia': 1,
                                 'target': target,
                                 'name': thing,
                                 'size': size})
                else:
                    rows.append({'isother': 1,
                                 'name': thing,
                                 'size': size})
        return rows


def main():

    print "Content-type: text/html\n\n"
    vc = vlccontroller.VLCController(password=VLCPASS)
    vc.connect()
    request = Request(vc=vc)
    renderer = pystache.Renderer()

    if request.action == "toggle_play":
        vc.pause()
        return

    if request.action == "toggle_subs":
        vc.set_subtitle_track(-1)
        return

    if request.action == "play":
        target = os.sep.join((DIR, request.form.getfirst('target')))
        vc.clear()
        vc.add(target)
        vc.play()
        return

    print renderer.render_name('dadisk.html', request)
    return

if __name__ == "__main__":
    main()
