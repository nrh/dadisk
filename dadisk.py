#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import cgi
import urllib
import subprocess
import tempfile
import pystache
from pprint import pformat

LOGINUSER   = 'nrh'
DEVNULL     = open('/dev/null', 'w')
DIR         = "/Volumes/DADISK"
MEDIAEXT    = ('m4v', 'avi', 'wmv', 'mp4', 'mkv')
ROOTURI     = '/~%s/' % LOGINUSER


class Request(object):
    def __init__(self, form=None):
        self.form = cgi.FieldStorage()
        self.dir = self.form.getfirst('dir') or '/'
        self.safe_dir = urllib.quote_plus(self.dir, safe='/')
        self.action = self.form.getfirst('action') or "list"
        self.file = self.form.getfirst('file') or None
        self.fsdir = os.sep.join((DIR, self.dir)).replace('//','/').rstrip('/')
        self.parts = self.dir.replace('//','/').rstrip('/').split('/')
        self.debug = self.form.getfirst('debug') or False
        self.roottarget = ROOTURI
        self.rootname = '<root>'

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
                target = os.sep.join((self.realdir(), thing)).lstrip('/').rstrip('/')
                safe_target = urllib.quote_plus(target, safe='/')
                rows.append({'isdir': 1,
                             'colspan': 2,
                             'target': safe_target,
                             'name': thing})
            elif os.path.isfile(path):
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
    request = Request()
    renderer = pystache.Renderer()

    if request.action == "toggle_play":
        toggle_play()
        print request.pprint()
        return

    if request.action == "toggle_subs":
        toggle_subs()
        print request.pprint()
        return

    if request.action == "play":
        target = os.sep.join((DIR, request.form.getfirst('target')))
        play_media(target)
        print request.pprint()
        return

    print renderer.render_name('dadisk.html', request)
    return


def play_media(path):
    with tempfile.NamedTemporaryFile() as temp:
        renderer = pystache.Renderer()
        temp.write(renderer.render_name('play_media.applescript', {'file': path}))
        temp.flush()
        os.chmod(temp.name, 0444)
        subprocess.call(['/usr/bin/sudo', '-u', LOGINUSER,
                         '/usr/bin/osascript', temp.name],
                        stderr=DEVNULL, stdout=DEVNULL)
    return


def toggle_play():
    with open('toggle_play.applescript') as f:
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(f.read())
            temp.flush()
            os.chmod(temp.name, 0444)
            subprocess.call(['/usr/bin/sudo', '-u', LOGINUSER,
                             '/usr/bin/osascript', temp.name],
                             stderr=DEVNULL, stdout=DEVNULL)
    return


def toggle_subs():
    with open('toggle_subs.applescript') as f:
        with tempfile.NamedTemporaryFile() as temp:
            temp.write(f.read())
            temp.flush()
            os.chmod(temp.name, 0444)
            subprocess.call(['/usr/bin/sudo', '-u', LOGINUSER,
                             '/usr/bin/osascript', temp.name],
                             stderr=DEVNULL, stdout=DEVNULL)
    return

if __name__ == "__main__":
    main()
