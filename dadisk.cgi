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

DEVNULL     = open('/dev/null', 'w')
DIR         = "/Volumes/DADISK"
HEADER      = """
<!DOCTYPE html>
<html lang="en">
<head>
<base href="/~nrh/"><link rel="stylesheet" type="text/css" href="dadisk.css">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="bootstrap/css/bootstrap.min.css" rel="stylesheet" media="screen">
</head><body>
<script src="http://code.jquery.com/jquery.js"></script>
<script src="bootstrap/js/bootstrap.min.js"></script>
<div class="container">"""
FOOTER      = """</div></body></html>"""
MEDIAEXT    = ('m4v','avi','wmv','mp4','mkv')
SUBTITLES   = """
activate application "VLC"
tell application "System Events"
  tell process "VLC"
    tell menu bar 1
      tell menu bar item "Video"
        tell menu "Video"
          tell menu item "Subtitles Track"
            tell menu "Subtitles Track"
              set track1status to (value of attribute "AXMenuItemMarkChar" of menu item "Track 1" as string) ≠ ""
              if track1status is false then
                click menu item "Track 1"
              else if track1status is true then
                click menu item "Disable"
              end if
            end tell
          end tell
        end tell
      end tell
    end tell
  end tell
end tell
"""

form = cgi.FieldStorage()

print "Content-type: text/html\n\n"

def main():

    dirl = form.getfirst('dir') or None
    action = form.getfirst('action') or "list"
    mediafile = form.getfirst('file') or None

    if action == "toggle_play":
        toggle_play()
        redirect(dirl, "list")

    if action == "toggle_subs":
        toggle_subs()
        redirect(dirl, "list")

    if action == "play":
        play_media(mediafile)
        redirect(dirl, "list")

    if action == "list":
        list_dir(dirl)

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
        subprocess.call(['/usr/bin/sudo','-u','nrh','/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    print """<div id="info">playing %s</div>""" % path
    return

def toggle_play():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write("""tell application "VLC" to play""")
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u','nrh','/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    return

def toggle_subs():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(SUBTITLES)
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u','nrh','/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    return

def human_readable_size(s):
    for x in ['bytes','KB','MB','GB','TB']:
        if s < 1024.0:
            return "%3.1f %s" % (s, x)
        s /= 1024.0
    return "%3.1f" % s

def markup_file(i,fp):
    print """<tr><td>%s</td><td>%s</td></tr>""" % (i, human_readable_size(os.path.getsize(fp)))

def markup_dir(i,fp):
    print """<tr><td colspan="2"><a href="dadisk.cgi?dir=%s">%s</a></td></tr>""" % (urllib.quote_plus(fp, safe=''), i)

def markup_playlink(i,fp,d):
    print """<tr><td><a href="dadisk.cgi?dir=%s&action=play&file=%s">%s</a></td><td>%s</td></tr>""" % (urllib.quote_plus(d, safe=''), urllib.quote_plus(fp, safe=''), i, human_readable_size(os.path.getsize(fp)))

def breadcrumb(d):
    if not d:
        d = '&lt;root&gt;'

    parts = d.split('/')
    def gen_url(s):
        if s == '&lt;root&gt;':
            return "dadisk.cgi"
        return "dadisk.cgi?dir=%s" % urllib.quote_plus(s, safe='')

    print """<div><ul class="breadcrumb">"""
    for i in range(len(parts) - 1):
        print """<li><a href="%s">%s</a> <span class="divider">/</span></li>""" % (gen_url(parts[i]), parts[i])
    print """<li class="active">%s</li>""" % parts[-1]
    print """<li class="pull-right"><a class="btn" href="dadisk.cgi?dir=%s&action=toggle_play">pause</a></li>""" % urllib.quote_plus(d, safe='')

    print """<li class="pull-right"><a class="btn" href="dadisk.cgi?dir=%s&action=toggle_subs">toggle&nbsp;subs</a></li>""" % urllib.quote_plus(d, safe='')
    print """</ul></div>"""


def list_dir(d):
    print HEADER
    breadcrumb(d)
    if not d:
        realdir = DIR
    else:
        realdir = os.sep.join((DIR, d))

    print """<table class="table table-striped table-bordered">"""

    for thing in os.listdir(realdir):
        path = os.sep.join((realdir, thing))

        if thing == "":
            continue
        if re.match('^\.', thing):
            continue
        if not os.access(path, os.R_OK):
            print "skipped %s"%path
            continue

        if os.path.isdir(path):
            markup_dir(path, path)
        elif os.path.isfile(path):
            ext = path.rsplit('.')[-1:]
            if ext[0] in MEDIAEXT:
                markup_playlink(thing, path, d)
            else:
                markup_file(thing, path)

    print FOOTER

if __name__ == "__main__":
    main()

