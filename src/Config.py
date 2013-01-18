'''
Created on 2013-1-18

@author: kongzhp
'''
class Protocol:
    HTTP = 80
    HTTPS = 443
    RDP = 3389
    
class Config:
    general = None
    address = "0.0.0.0"
    port = 443
    max_process = 10
    max_connection = 100
    process_timeout = 60
    connection_timeout = 10
    http_max_header_size = 2048
    web_client = None
    admin_redirection = False
    root_redirection = None
    http_keep_alive = True