import socket
import sys
import threading
import time

RS_TIMEOUT = 60     # How long to wait before listening socket times out 
CLIENT_TIMEOUT = 5  # How long to wait before conn with client times out
TS_TIMEOUT     = 5  # How long to wait before conn with ts servers timers out 

rs_port     = 0
rs_socket   = None     # Timeout after RS_TIMEOUT

client_port     = 0
client_hostname = ""
client_socket   = None # Timeout after CLIENT_TIMEOUT

ts1_port     = 0
ts1_hostname = ""
ts1_response = ""

ts2_port     = 0
ts2_hostname = ""
ts2_response = ""

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
    # DO NOT call shutdown on a listening socket
    if rs_socket != None:
        rs_socket.close()

def queryTS1(data):
    global ts1_response
    ts1_response = ""
    
    try:
        ts1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts1_socket.connect((ts1_hostname, ts1_port))
        ts1_socket.settimeout(TS_TIMEOUT)
    
    except OSError as error:
        print(error)
        if (ts1_socket != None):
            ts1_socket.shutdown(socket.SHUT_RDWR)
            ts1_socket.close()
        print("    Error: Unable to connect to ts1 at {}:{}".format(ts1_hostname, ts1_port))
        return
    print("    Debug: Succesfully connected to ts1 at {}:{}".format(ts1_hostname, ts1_port))
    
    try:
        ts1_socket.send(data.encode("utf-8"))
        ts1_response = ts1_socket.recv(512).decode("utf-8")
    
    except socket.timeout:
        ts1_response = ""
    
    except OSError as error:
        print(error)
        print("    Error: Major problem occurred when querying TS1")
    
    ts1_socket.shutdown(socket.SHUT_RDWR)
    ts1_socket.close()

def queryTS2(data):
    global ts2_response
    ts2_response = ""
    
    try:
        ts2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts2_socket.connect((ts2_hostname, ts2_port))
        ts2_socket.settimeout(TS_TIMEOUT)
        
    except OSError as error:
        print(error)
        if (ts2_socket != None):
            ts2_socket.shutdown(socket.SHUT_RDWR)
            ts2_socket.close()
        print("    Error: Unable to connect to ts2 at {}:{}".format(ts2_hostname, ts2_port))
        return
    print("    Debug: Succesfully connected to ts2 at {}:{}".format(ts2_hostname, ts2_port)) 
    
    try:
        ts2_socket.send(data.encode("utf-8"))
        ts2_response = ts2_socket.recv(512).decode("utf-8")
    
    except socket.timeout:
        ts2_response = ""
    
    except OSError as error:
        print(error)
        print("    Error: Major problem occurred when querying TS2")
    
    ts2_socket.shutdown(socket.SHUT_RDWR)
    ts2_socket.close()
        
    
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
    
    except socket.timeout:
        cleanupSockets()
        sys.exit("Error: Listener socket timed out waiting for client")
    
    except OSError as error:
        print(error)
        cleanupSockets()
        sys.exit("Error: Failure to accept incoming connection")


def readLoop():
    global client_socket
    client_socket.settimeout(CLIENT_TIMEOUT)
    
    while True:
        try:
            data = client_socket.recv(200).decode("utf-8")
        
        except socket.timeout:
            print("Error: Connection to client timed out")
            break
        
        except OSError as error:
            print(error)
            print("Error: Failed to read from client")
            break
        
        data = data.strip()
        if len(data) == 0:
            break # Client ended the connection
        
        print("Debug: Received from client: {}".format(data))
        
        try:
            
            t1 = threading.Thread(target=queryTS1, name="ts1", args=(data,))
            t2 = threading.Thread(target=queryTS2, name="ts2", args=(data,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            
            print("    Debug: Received from ts1: {}".format(ts1_response))
            print("    Debug: Received from ts2: {}".format(ts2_response))
        
        except OSError as error: # multithreading error probably very bad
            print(error)
            cleanupSockets()
            sys.exit("Error: System Error")
        
        try:
            if ts1_response == "" and ts2_response == "":
                message = "{} - TIMED OUT".format(data)
                print("    Debug: Sent to client: {}".format(message))
                client_socket.send(message.encode("utf-8"))
                
            elif ts1_response != "" and ts2_response != "":
                print("    ERROR: BOTH TS RESPONDED")
            
            elif ts1_response != "":
                client_socket.send(ts1_response.encode("utf-8"))
            
            else:
                client_socket.send(ts2_response.encode("utf-8"))
        
        except socket.timeout:
            print("    Error: Connection to client timed out")
            break
        
        except OSError as error:
            print(error)
            print("    Error: Failed to send reponse to client")
            break
    
    if (client_socket != None):
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        

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
    print("Debug: Succesfully cleaned up sockets")
    

if (__name__ == "__main__"):
    main()