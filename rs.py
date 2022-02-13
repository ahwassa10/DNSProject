import socket
import sys

rs_port     = 0
rs_socket   = None

client_port     = 0
client_hostname = ""
client_socket   = None

ts1_port     = 0
ts1_hostname = ""
ts1_socket   = None

ts2_port     = 0
ts2_hostname = ""
ts2_socket   = None

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
    
    if rs_socket != None:
        rs_socket.close()


def openTSConnections():
    global ts1_socket
    try:
        ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts1_socket.connect((ts1_hostname, ts1_port))
    
    except OSError as error:
        print(error)
        sys.exit("Error: Unable to connect to ts1 at {} : {}".format(ts1_hostname, ts1_port))
    
    global ts2_socket
    try:
        ts2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts2_socket.connect((ts2_hostname, ts2_port))
    
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

def main():
    parseArgs()
    print("Debug: Succesfully parsed all command line arguments")
    
    openTSConnections()
    print("Debug: Succesfully opened connections to ts1 and ts2")
    print("Debug: ts1 at {} : {}".format(ts1_hostname, ts1_port))
    print("Debug: ts2 at {} : {}".format(ts2_hostname, ts2_port))
    
    openListener()
    host = socket.gethostname()
    ip   = socket.gethostbyname(host)
    print("Debug: Succesfully opened a listening socket at " \
          "{} : {} {}".format(host, rs_port, ip))
    
    cleanupSockets()
    print("Debug: Succesfully cleaned up connections to ts1 and ts2")
    

if (__name__ == "__main__"):
    main()