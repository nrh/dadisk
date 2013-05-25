# -*- coding: utf-8 -*-
import time


def size(s):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if s < 1024.0:
            return "%3.1f %s" % (s, x)
        s /= 1024.0
    return '%3.1f' % s


def date(d):
    """emulate gnu coreutils 'ls -l' time format"""
    if time.time() - d > 15724800:
        return time.strftime('%b %e  %Y', time.localtime(d))
    else:
        return time.strftime('%b %e %H:%M', time.localtime(d))


def timestamp(t):
    intervals = [86400, 3600, 60, 1]
    names = ['d', 'h', 'm', 's']

    result = ''
    for x in range(len(intervals)):
        if t >= intervals[x]:
            d = t / intervals[x]
            result = "%s%s%s" % (result, d, names[x])
            t = t - d * intervals[x]
    return result


def timestamp_set(t):
    intervals = [86400, 3600, 60, 1]

    result = []
    for x in range(len(intervals)):
        if t >= intervals[x]:
            d = t / intervals[x]
            result.append(d)
            t = t - d * intervals[x]
        else:
            result.append(0)
    return result
