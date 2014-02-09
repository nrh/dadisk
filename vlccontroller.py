#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import re
import telnetlib

READ_TIMEOUT = 2
CONNECTION_TIMEOUT = 10


class VLCController(object):
    def __init__(self, password=None, host='127.0.0.1', port=4212):
        self.password = bytes(password, encoding='ascii')
        self.host = host
        self.port = port
        self.conn = None
        return

    def connect(self):
        if not self.conn:
            self.conn = telnetlib.Telnet(self.host, self.port,
                                         timeout=CONNECTION_TIMEOUT)
            self.conn.read_until(b'assword:', READ_TIMEOUT)
            self.conn.write(self.password + b'\r\n')
            self.conn.read_until(b'> ', READ_TIMEOUT)
        return

    def pause(self):
        self.conn.write(b'pause\r\n')
        self.conn.read_until(b'> ', READ_TIMEOUT)
        return

    def is_playing(self):
        self.conn.write(b'is_playing\r\n')
        t = self.conn.read_until(b'> ', READ_TIMEOUT)
        t = t[0:t.rindex(b'\r')]
        return True if int(t) == 1 else False

    def enqueue(self, item):
        self.conn.write(('enqueue %s\r\n' % item).encode('utf-8'))
        self.conn.read_until(b'> ', READ_TIMEOUT)
        return

    def add(self, item):
        self.conn.write(('add %s\r\n' % item).encode('utf-8'))
        self.conn.read_until(b'> ', READ_TIMEOUT)
        return

    def play(self):
        self.conn.write(b'play\r\n')
        self.conn.read_until(b'> ', READ_TIMEOUT)
        return

    def clear(self):
        self.conn.write(b'clear\r\n')
        self.conn.read_until(b'> ', READ_TIMEOUT)
        return

    def time(self):
        self.conn.write(b'get_time\r\n')
        t = self.conn.read_until(b'> ', READ_TIMEOUT)
        t = t[0:t.rindex(b'\r')]
        try:
            t = int(t)
        except ValueError:
            return None
        return t

    def length(self):
        self.conn.write(b'get_length\r\n')
        t = self.conn.read_until(b'> ', READ_TIMEOUT)
        t = t[0:t.rindex(b'\r')]
        try:
            t = int(t)
        except ValueError:
            return None
        return t

    def title(self):
        self.conn.write(b'get_title\r\n')
        t = self.conn.read_until(b'> ', READ_TIMEOUT)
        if t:
            t = t[0:t.rindex(b'\r')]
            return t
        return None

    def get_subtitle_tracks(self):
        self.conn.write(b'strack\r\n')
        tracks = self.conn.read_until(b'> ', READ_TIMEOUT)
        tset = []
        tselected = None
        for t in tracks.split(b'\r\n'):
            match = re.match('^\| ([-]?\d+) - (.*)', t)
            if match:
                name = match.group(2)
                if name[-1] == '*':
                    tselected = match.group(1)
                    name = name[0:-1].rstrip()
                tset.append((match.group(1), name))

        return (tset, tselected)

    def set_subtitle_track(self, sel):
        self.conn.write(('strack %s\r\n' % sel).encode('utf-8'))
        self.conn.read_until(b'> ', READ_TIMEOUT)
        return
