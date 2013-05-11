#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import socket
import telnetlib
import re

PORT=4212
PASS='dickbutt'

class VLCController(object):
    def __init__(self):
        self.conn = telnetlib.Telnet('127.0.0.1', PORT)
        self.conn.read_until('ord:')
        self.conn.write(PASS + "\r\n")
        self.conn.read_until('> ')
        return

    def pause(self):
        self.conn.write("pause\r\n")
        self.conn.read_until('> ')
        return

    def is_playing(self):
        self.conn.write("is_playing\r\n")
        t = self.conn.read_until('> ')
        t = t[0:t.rindex("\r")]
        return True if int(t) == 1 else False

    def time(self):
        self.conn.write("get_time\r\n")
        t = self.conn.read_until('> ')
        t = t[0:t.rindex("\r")]
        return int(t)

    def length(self):
        self.conn.write("get_length\r\n")
        t = self.conn.read_until('> ')
        t = t[0:t.rindex("\r")]
        return int(t)

    def title(self):
        self.conn.write("get_title\r\n")
        t = self.conn.read_until('> ')
        t = t[0:t.rindex("\r")]
        return t

    def get_subtitle_tracks(self):
        self.conn.write("strack\r\n")
        tracks = self.conn.read_until('> ')
        tset = []
        tselected = None
        for t in tracks.split('\r\n'):
            match = re.match('^\| ([-]?\d+) - (.*)', t)
            if match:
                tset.append(match.groups())
                if match.group(2)[-1] == '*':
                    tselected = match.group(1)

        return (tset,tselected)

    def set_subtitle_track(self, sel):
        self.conn.write("strack %s\r\n" % sel)
        self.conn.read_until('> ')
        return

