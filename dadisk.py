#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import cgi
import urllib
import subprocess
import tempfile
import pystache

LOGINUSER   = 'nrh'
DEVNULL     = open('/dev/null', 'w')
DIR         = "/Volumes/DADISK"
MEDIAEXT    = ('m4v', 'avi', 'wmv', 'mp4', 'mkv')


class Request(object):
    def __init__(self, form=None):
        form = cgi.FieldStorage()
        self.dir = form.getfirst('dir') or '/'
        self.safe_dir = urllib.quote_plus(self.dir, safe='')
        self.action = form.getfirst('action') or "list"
        self.file = form.getfirst('file') or None
        self.fsdir = os.sep.join((DIR, self.dir))

    def breadcrumb(self):
        # class=active, href=?..., target=foo
        items = []
        parts = self.dir.split('/')[1:]
        if len(parts) > 1:
            items.append({'target': '<root>', 'href': ""})
        else:
            items.append({'class': 'active', 'target': '<root>'})

        if len(parts) > 1:
            for i in range(len(parts) - 1):
                items.append({'target': parts[i],
                              'href': "?dir=%s" % self.safe_dir})

            items.append({'target': parts[-1], 'class': 'active'})
        return items

    def rows(self):
        def human_readable_size(s):
            for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
                if s < 1024.0:
                    return "%3.1f %s" % (s, x)
                s /= 1024.0
            return "%3.1f" % s
        # colspan=2, href=?..., target=foo, size=bar
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
                safe_target = urllib.quote_plus(os.sep.join((self.dir, thing)),
                                                safe='')
                rows.append({'colspan': 2,
                             'href': "?dir=%s" % safe_target,
                             'target': thing})
            elif os.path.isfile(path):
                ext = path.rsplit('.')[-1:]
                size = human_readable_size(os.path.getsize(path))
                if ext[0] in MEDIAEXT:
                    href = ("?dir=%s&action=play&target=%s" %
                            (self.safe_dir, os.sep.join((self.dir, thing))))
                    rows.append({'href': href, 'target': thing, 'size': size})
                else:
                    rows.append({'target': thing, 'size': size})
        return rows

    def playurl(self):
        return """?dir=%s&action=toggle_play""" % self.safe_dir

    def subsurl(self):
        return """?dir=%s&action=toggle_subs""" % self.safe_dir


def main():

    print "Content-type: text/html\n\n"
    request = Request()
    renderer = pystache.Renderer()

    if request.action == "toggle_play":
        toggle_play()
        print renderer.render_name('redirect.html', request)
        return

    if request.action == "toggle_subs":
        toggle_subs()
        print renderer.render_name('redirect.html', request)
        return

    if request.action == "play":
        play_media(request.file)
        print renderer.render_name('redirect.html', request)

    print renderer.render_name('dadisk.html', request)
    return


def play_media(path):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        renderer = pystache.Renderer()
        temp.write(renderer.render_name('play_media.applescript', {'file': path}))
        temp.flush()
        os.fchown(temp, 0444)
        subprocess.call(['/usr/bin/sudo', '-u', LOGINUSER,
                         '/usr/bin/osascript', temp.name],
                        stderr=DEVNULL, stdout=DEVNULL)
    return


def toggle_play():
    with open('toggle_play.applescript') as f:
        subprocess.call(['/usr/bin/sudo', '-u', LOGINUSER,
                         '/usr/bin/osascript', f.name],
                        stderr=DEVNULL, stdout=DEVNULL)
    return


def toggle_subs():
    with open('toggle_subs.applescript') as f:
        subprocess.call(['/usr/bin/sudo', '-u', LOGINUSER,
                         '/usr/bin/osascript', f.name],
                        stderr=DEVNULL, stdout=DEVNULL)
    return

if __name__ == "__main__":
    main()
