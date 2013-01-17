'''
Created on 2013-1-17

@author: ausu
'''
import asyncore
from multiprocessing import Process, current_process
import Queue
import signal
import threading

from ControlProcess import ControlFatherProcess
from ProtocolDetectDispatcher import ProtocolDetectDispatcher

class ConnectionPoolProcess(Process):
    '''
    classdocs
    '''
    def __init__(self, child_pipes, father_pipes, ssl_ctx):
        Process.__init__(self)
        
        self.pipes = child_pipes
        self.father_pipes = father_pipes
        self.ssl_ctx = ssl_ctx
        
        self.f_control = None
        self.t_asyncore = None
        self.socks = None
        
        # use for process cleaning
        self.was_lazy = False
        self.clean_timer = None
        
    def run(self):
        
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        
        # close inherited father pipes
        self.father_pipes[0].close()
        self.father_pipes[1].close()
        
        self.socks = Queue.Queue() #线程安全的queue

        self.clean_timer = threading.Timer(60, self.clean)
        self.clean_timer.start()
        
        self.f_control = ControlFatherProcess(self)
        self.f_control.start()
        
        while self.f_control.is_alive() or not self.socks.empty():
            try:
                sock = self.socks.get(timeout=0.01) #在timeout时间内，假如socks为空，返回Empty Exception
                sock.accept()
                ProtocolDetectDispatcher(sock, self.f_control)
            except (IOError, Queue.Empty):
                continue

            # reload asyncore if stopped
            if self.t_asyncore is None or not self.t_asyncore.is_alive():
                # timeout needed for more SSL layer reactivity
                self.t_asyncore = threading.Thread(target=lambda:asyncore.loop(timeout=0.01))
                self.t_asyncore.start()
        
        if self.t_asyncore is not None and self.t_asyncore.is_alive():
            asyncore.close_all()
            self.t_asyncore.join()
        
        