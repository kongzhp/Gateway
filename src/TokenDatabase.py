'''
Created on 2013-1-18

@author: kongzhp
'''
import uuid
import threading

database = {}
lock = threading.Lock()

def insertToken(fqdn):
    token = str(uuid.uuid4())
    lock.acquire()
    database[token] = fqdn
    lock.release()
    return token

def digestToken(token):
    try:
        lock.acquire()
        return database.pop(token)
    except KeyError:
        return None
    finally:
        lock.release()
