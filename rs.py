import socket
import sys
import threading
import time

RS_TIMEOUT = 10     # How long to wait before listening socket times out 
CLIENT_TIMEOUT = 5  # How long to wait before conn with client times out
TS_TIMEOUT     = 5  # How long to wait before conn with ts servers timers out 

rs_port     = 0
rs_socket   = None     # Timeout after RS_TIMEOUT

client_port     = 0
client_hostname = ""
client_socket   = None # Timeout after CLIENT_TIMEOUT

ts1_port     = 0
ts1_hostname = ""
ts1_socket   = None    # Timeout after TS_TIMEOUT

ts2_port     = 0
ts2_hostname = ""
ts2_socket   = None    # Timeout after TS_TIMEOUT

def parsePort(port):
    if port.isdigit() and int(port) > 0 and int(port) < 65535:
        return int(port)
    else:
        sys.exit("Error: Invalid port number: {}".format(port))

def parseArgs():
    arguments = sys.argv
    if len(arguments) != 6:
        sys.exit("Error: Incorrect Format\n" +
                 "rs.py rsListenPort ts1Hostname " +
                 "ts1ListenPort ts2Hostname ts2ListenPort")
    
    global rs_port
    rs_port = parsePort(arguments[1])
    
    global ts1_hostname
    global ts1_port
    ts1_hostname = arguments[2]
    ts1_port     = parsePort(arguments[3])
    
    global ts2_hostname
    global ts2_port
    ts2_hostname = arguments[4]
    ts2_port     = parsePort(arguments[5])


def cleanupSockets():
    if ts1_socket != None:
        ts1_socket.shutdown(socket.SHUT_RDWR)
        ts1_socket.close()
    
    if ts2_socket != None:
        ts2_socket.shutdown(socket.SHUT_RDWR)
        ts2_socket.close()
    
    # DO NOT call shutdown on a listening socket
    if rs_socket != None:
        rs_socket.close()
    
    if client_socket != None:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()

def queryTS1():
    global ts1_socket
    ts1_socket = None
    
    try:
        ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts1_socket.connect((ts1_hostname, ts1_port))
        ts1_socket.settimeout(TS_TIMEOUT)
    
    except OSError as error:
        print(error)
        sys.exit("Error: Unable to connect to ts1 at {}:{}".format(ts1_hostname, ts1_port))
    


def openTSConnections():
    global ts1_socket
    try:
        ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts1_socket.connect((ts1_hostname, ts1_port))
        ts1_socket.settimeout(TS_TIMEOUT)
    
    except OSError as error:
        print(error)
        sys.exit("Error: Unable to connect to ts1 at {} : {}".format(ts1_hostname, ts1_port))
    
    global ts2_socket
    try:
        ts2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts2_socket.connect((ts2_hostname, ts2_port))
        ts1_socket.settimeout(TS_TIMEOUT)
    
    except OSError as error:
        print(error)
        cleanupSockets()
        sys.exit("Error: Unable to connect to ts2 at {} : {}".format(ts2_hostname, ts2_port))

def openListener():
    global rs_socket
    try:
        rs_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        rs_binding = ('', rs_port)
        rs_socket.bind(rs_binding)
        rs_socket.listen(3)
        
    except OSError as error:
        print(error)
        cleanupSockets()
        sys.exit("Error: Failed to create listening socket")

def waitClient():
    global client_port
    global client_hostname
    global client_socket
    
    try:
        rs_socket.settimeout(RS_TIMEOUT)
        client_socket, address = rs_socket.accept()
        client_hostname = address[0]
        client_port     = address[1]
    
    except socket.timeout
        cleanupSockets()
        sys.exit("Error: Listener socket timed out waiting for client")
    
    except OSError as error:
        print(error)
        cleanupSockets()
        sys.exit("Error: Failure to accept incoming connection")


def readLoop():
    client_socket.settimeout(CLIENT_TIMEOUT)
    
    while True:
        try:
            data = client_socket.recv(200).decode("utf-8")
        
        except socket.timeout:
            print("Error: Connection to client timed out")
            return
        
        except OSError as error:
            print(error)
            cleanupSockets()
            sys.exit("Error: Failed to read from client")
        
        data = data.strip()
        if len(data) == 0:
            return # Client ended the connection
        
        print("Debug: Received from client: {}".format(data))
        
        try:
            
            t1 = threading.Thread(target=sendTS, name="ts1", args=(data, ts1_socket))
            t2 = threading.Thread(target=sendTS, name="ts2", args=(data, ts2_socket))
            t1.start()
            t2.start()
            
            ts1_data = ""
            ts2_data = ""
            
            print("Debug: Received from ts1: {}".format(ts1_data))
            print("Debug: Received from ts2: {}".format(ts2_data))
        
        except OSError as error:
            print(error)
            cleanupSockets()
            sys.exit("Error: Failed to communicated with ts server")
            

def main():
    parseArgs()
    print("Debug: Succesfully parsed all command line arguments")
    
    openListener()
    host = socket.gethostname()
    ip   = socket.gethostbyname(host)
    print("Debug: Succesfully opened a listening socket at " \
          "{} : {} {}".format(host, rs_port, ip))
    
    global client_hostname
    global client_port
    global client_socket
    
    while True:
        # Cleanup resources from previous client connection
        client_hostname = ""
        client_port = 0
        client_socket = None
        
        waitClient()
        print("Debug: Succesfully establish connection with: " \
              "{} : {}".format(client_hostname, client_port))
        
        readLoop()
        print("Debug: Interaction with client finished")
    
    
    
    cleanupSockets()
    print("Debug: Succesfully cleaned up connections to ts1 and ts2")
    

if (__name__ == "__main__"):
    main()