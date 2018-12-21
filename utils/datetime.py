from datetime import datetime


def parseDatetimeString(text):
    [ds, ts] = text.split(' ')
    [Y, M, D] = ds.split('-')
    [h, m, s] = ts.split(':')
    return datetime(int(Y), int(M), int(D), int(h), int(m), int(s))
