'''
Created on 2013-1-17

@author: ausu
'''
import threading
from TCPHandler import GatewayTCPHandler

class Role(object):
    '''
    gate way role
    '''
    def __init__(self):
        self.server = None
        self.processes = {}
        self.kill_mutex = threading.Lock()
        
        
        
        