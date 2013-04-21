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
HEADER      = """<html><head><base href="/~nrh/"><link rel="stylesheet" type="text/css" href="dadisk.css"></head><body><div id="outer">"""
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

    dirl = form.getfirst('dir') or DIR
    action = form.getfirst('action') or "list"
    mediafile = form.getfirst('file') or None

    if action == "toggle_play":
        print toggle_play()
        redirect(dirl, "list")

    if action == "toggle_subs":
        print toggle_subs()
        redirect(dirl, "list")

    if action == "play":
        print play_media(mediafile)
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
    return """<div id="info">playing %s</div>""" % path

def toggle_play():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write("""tell application "VLC" to play""")
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u','nrh','/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    return "toggled play"

def toggle_subs():
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(SUBTITLES)
        temp.flush()
        subprocess.call(['/bin/chmod','a+r',temp.name])
        subprocess.call(['/usr/bin/sudo','-u','nrh','/usr/bin/osascript',temp.name], stderr=DEVNULL, stdout=DEVNULL)
    return "toggled subs"

def markup_file(i,fp):
    return """<div class="file">%s</div>""" % i

def markup_dir(i,fp):
    return """<div class="dir"><a href="dadisk.cgi?dir=%s">%s</a></div>""" % (urllib.quote_plus(fp, safe=''), i)

def markup_playlink(i,fp,d):
    return """<div class="playlink"><a href="dadisk.cgi?dir=%s&action=play&file=%s">%s</a>""" % (urllib.quote_plus(d, safe=''), urllib.quote_plus(fp, safe=''), i)

def list_dir(d):
    print HEADER
    print """<div id="playpause"><a href="dadisk.cgi?dir=%s&action=toggle_play">play/pause</a></div>""" % (urllib.quote_plus(d, safe=''))
    print """<div id="togglesubs"><a href="dadisk.cgi?dir=%s&action=toggle_subs">toggle subtitles</a></div>""" % (urllib.quote_plus(d, safe=''))

    for thing in os.listdir(d):
        path = os.sep.join((d, thing))

        if thing == "":
            continue
        if re.match('^\.', thing):
            continue
        if not os.access(path, os.R_OK):
            print "skipped %s"%path
            continue

        if os.path.isdir(path):
            print markup_dir(thing, path)
        elif os.path.isfile(path):
            ext = path.rsplit('.')[-1:]
            if ext[0] in MEDIAEXT:
                print markup_playlink(thing, path, d)
            else:
                print markup_file(thing, path)

    print FOOTER

if __name__ == "__main__":
    main()

