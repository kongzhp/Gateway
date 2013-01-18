'''
Created on 2013-1-17

@author: ausu
'''
from multiprocessing.reduction import reduce_socket
from SocketServer import BaseRequestHandler
import pickle

class GatewayTCPHandler(BaseRequestHandler):
    def handle(self):
        self.role.kill_mutex.acquire()
        
        best_proc = None #Ö¸Ïò
        for pid, proc in self.role.processes.items():
            ctrl = proc[0][1]
            nb_conn = ctrl.send('nb_conn')
            self.role.processes[pid][1] = nb_conn
            if nb_conn < 100:
                best_proc = pid
                break
        if best_proc is None:
            if len(self.role.processes) < 10:
                best_proc = self.role.create_process()
            else:
                best_proc = min(self.role.processes, key=lambda pid:self.role.processes[pid][1])
               
        
        ctrl = self.role.processes[best_proc][0][1]
        pickled_sock = pickle.dumps(reduce_socket(self.request)[1])
        ctrl.send(('socket', pickled_sock))
        
        self.role.kill_mutex.release()
        