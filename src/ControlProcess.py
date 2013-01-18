'''
Created on 2013-1-18

@author: kongzhp
'''
import asyncore
from multiprocessing.reduction import rebuild_socket
import pickle
from threading import Thread
from TokenDatabase import digestToken,insertToken

class ControlClassProcess(Thread):
    def __init__(self, _class):
        Thread.__init__(self)
        self._class = _class
        (self._pipe_s, self._pipe_m) = self._class.pipes
    
    
    def run(self):
        while True:
            try:
                cmd = self._pipe_s.recv()
                if type(cmd) is type(""):
                    args = ()
                elif type(cmd) is type(()):
                    args = cmd[1:]
                    cmd = cmd[0]
                cmd = '_'+cmd
                if hasattr(self, cmd):
                    attr = getattr(self, cmd)
                    self._pipe_s.send(attr(*args))
                else:
                    self._pipe_s.send(None)
            except (EOFError, IOError):
                break
    
    
    def terminate(self):
        self._pipe_s.close()
        self._pipe_m.close()
    
    
    def send(self, cmd):
        self._pipe_m.send(cmd)
        return self._pipe_m.recv()



class ControlFatherProcess(ControlClassProcess):
    
    def _nb_conn(self):
        return len(asyncore.socket_map) / 2
    
    def _socket(self, picklable):
        args = pickle.loads(picklable)
        sock = rebuild_socket(*args)
        self._class.socks.put(sock)
    
    def _stop(self):
        self._class.stop()



class ControlChildProcess(ControlClassProcess):
    
    def _digest_token(self, token):
        return digestToken(token)
    
    def _insert_token(self, fqdn):
        return insertToken(fqdn)
    
    def _stop_pid(self, pid):
        self._class.kill_process(pid)
        