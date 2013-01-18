'''
Created on 2013-1-18

@author: kongzhp
'''
from gzip import GzipFile
from cStringIO import StringIO


def gzip(buf):
    zbuf = StringIO()
    zfile = GzipFile(mode='wb',  fileobj=zbuf)
    zfile.write(buf)
    zfile.close()
    return zbuf.getvalue()


def gunzip(buf):
    zfile = GzipFile(fileobj=StringIO(buf))
    data = zfile.read()
    zfile.close()
    return data