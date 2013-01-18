'''
Created on 2013-1-18

@author: kongzhp
'''
import re

from Communicator import RdpClientCommunicator, RdpServerCommunicator, \
    HttpClientCommunicator, Communicator

import time
from Config import Config, Protocol


class ProtocolException(Exception):
    pass


class ProtocolDetectDispatcher(Communicator):
    
    rdp_ptn = re.compile('\x03\x00.*Cookie: .*token=([\-\w]+);.*')
    http_ptn = re.compile('((?:HEAD)|(?:GET)|(?:POST)) (.*) HTTP/(.\..)')
    
    def __init__(self, conn, f_ctrl, ssl_ctx):
        Communicator.__init__(self, conn)
        self.ssl_ctx = ssl_ctx
        self.f_ctrl = f_ctrl
        self.lastPacketTime = time.time()
    
    
    def writable(self):
        # This class doesn't have to write anything,
        # It's just use to detect the protocol
        return False
    
    def readable(self):
        if time.time() - self.lastPacketTime > Config.connection_timeout:
            print "ProtocolDetectDispatcher::connection timeout"
            self.handle_close()
            return False
        
        return True
    
    def handle_read(self):
        try:
            if Communicator.handle_read(self) is -1:
                return
        except Communicator.Error, e:
            # empty connection opened (chrome for example)
            if e.args[0][0][1] in ['SSL23_READ', 'SSL3_READ_BYTES']:
                self.handle_close()
                return
            else:
                raise
        
        self.lastPacketTime = time.time()
        request = self._buffer.split('\n', 1)[0]
        request = request.rstrip('\n\r').decode("utf-8", "replace")
        
        # find protocol
        rdp  = ProtocolDetectDispatcher.rdp_ptn.match(request)
        http = ProtocolDetectDispatcher.http_ptn.match(request)
        
        try:
            # RDP case
            if rdp:
                token = rdp.group(1)
                fqdn = self.f_ctrl.send(("digest_token", token))
                #Logger.debug("ProtocolDetectDispatcher:: request: RDP (%s -> %s)" % (token, fqdn))
                if not fqdn:
                    raise ProtocolException('token authorization failed for: ' + token)
                
                client = RdpClientCommunicator(self.socket)
                client._buffer = self._buffer
                client.communicator = RdpServerCommunicator((fqdn, Protocol.RDP), communicator=client)
            
            # HTTP case
            elif http:
                client = HttpClientCommunicator(self.socket, self.f_ctrl, self.ssl_ctx)
                client._buffer = self._buffer
                if client.make_http_message() is not None:
                    client._buffer = client.process()
            
            # protocol error
            else:
                # Check if the packet size is larger than a common HTTP first line
                if len(self._buffer) > Config.http_max_header_size:
                    raise ProtocolException('bad first request line: ' + request)
                return
        
        except ProtocolException, err:
            #Logger.error("ProtocolDetectDispatcher::handle_read: %s" % repr(err))
            self.handle_close()