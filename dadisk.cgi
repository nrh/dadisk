#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import re
import cgi
import urllib
import subprocess
import tempfile
import pystache

LOGINUSER   = 'nrh'
DEVNULL     = open('/dev/null', 'w')
DIR         = "/Volumes/DADISK"
MEDIAEXT    = ('m4v','avi','wmv','mp4','mkv')

class Request(object):
    def __init__(self, form=None):
        form = cgi.FieldStorage()
        self.dir = form.getfirst('dir') or '/'
        self.safe_dir = urllib.quote_plus(self.dir, safe='')
        self.action = form.getfirst('action') or "list"
        self.file = form.getfirst('file') or None
        self.fsdir = os.sep.join((DIR,self.dir))

    def breadcrumb(self):
        # class=active, href=dadisk.cgi?..., target=foo
        items = [{'target': '<root>', 'href': "dadisk.cgi"}]
        parts = self.dir.split('/')
        for i in range(len(parts) - 1):
            items.append({'target': parts[i], 'href': "dadisk.cgi?dir=%s" % self.safe_dir })

        items.append({'target': parts[-1], 'class': 'active'})
        return items

    def rows(self):
        def human_readable_size(s):
            for x in ['bytes','KB','MB','GB','TB']:
                if s < 1024.0:
                    return "%3.1f %s" % (s, x)
                s /= 1024.0
            return "%3.1f" % s
        # colspan=2, href=dadisk.cgi?..., target=foo, size=bar
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
                safe_target = urllib.quote_plus(os.sep.join((self.dir, thing)), safe='')
                rows.append({'colspan': 2, 'href': "dadisk.cgi?dir=%s" % safe_target, 'target': thing})
            elif os.path.isfile(path):
                ext = path.rsplit('.')[-1:]
                size = human_readable_size(os.path.getsize(path))
                if ext[0] in MEDIAEXT:
                    href = "dadisk.cgi?dir=%s&action=play&target=%s" % (self.safe_dir, os.sep.join((self.dir, thing)))
                    rows.append({'href': href, 'target': thing, 'size': size})
                else:
                    rows.append({'target': thing, 'size': size})
        return rows

    def playurl(self):
        return """dadisk.cgi?dir=%s&action=toggle_play""" % self.safe_dir

    def subsurl(self):
        return """dadisk.cgi?dir=%s&action=toggle_subs""" % self.safe_dir


def main():

    print "Content-type: text/html\n\n"
    request = Request()

    if request.action == "toggle_play":
        toggle_play()
        redirect(dirl, "list")
        return

    if request.action == "toggle_subs":
        toggle_subs()
        redirect(dirl, "list")
        return

    if request.action == "play":
        play_media(mediafile)

    renderer = pystache.Renderer()
    print renderer.render_name('dadisk.html', request)
    return

def redirect(target, action):
    if action == "list":
        print HEADER
        print """<meta http-equiv="refresh" content="0;url='dadisk.cgi?dir=%s&action=list'">""" % (urllib.quote_plus(target, safe=''))
        print FOOTER
    return

def play_media(path):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write("""tell application "VLC" to open "%s" fullscreen""" % path)
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u',LOGINUSER,'/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    print """<div id="info">playing %s</div>""" % path
    return

def toggle_play():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write("""tell application "VLC" to play""")
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u',LOGINUSER,'/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    return

def toggle_subs():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(SUBTITLES)
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u',LOGINUSER,'/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    return

if __name__ == "__main__":
    main()

