import socket
import sys
PORT = int(sys.argv[1])
ADDRESS = ""

TS_TIMEOUT = 60     # time to wait for connection before TS timesout
CLIENT_TIMEOUT = 10 # time to wait for RS to send something to TS
rr_map = dict()


CLIENT_TIMEOUT_SINKHOLE = True

def parse_RR():
    global rr_map
    try:
        f = open("PROJ2-DNSTS2.txt", "r")
        
        for line in f:
            line = line.strip()
            if (line == ""):
                continue
            
            hostname = (line.split(" ")[0]).lower()
            rr_map[hostname] = (line + " IN")
     
    except OSError as e:
        print(e)
        sys.exit("Failure to read input file and build dict")
            
        

def resolve_host(data_recieved):
    
    data_recieved = str.lower(data_recieved).strip()
    print(data_recieved)
    new_string = ""
    with open("PROJ2-DNSTS2.txt", 'r') as NFILE:
        for lines in NFILE.readlines():
            format_split_up = str(lines).strip().split(" ")
            
            hostname = format_split_up[0].rstrip()
            print(data_recieved == hostname)
            if data_recieved == hostname:
                format_split_up.append("IN\n")
                new_string =  " ".join(format_split_up)
                return new_string
    return None

def Main():
    
    ts_server = None
    try:
        ts_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ts_server.bind(('', PORT))
        ts_server.listen(3)
        ts_server.settimeout(TS_TIMEOUT)
        
    except OSError as e:
        print(e)
        if (ts_server != None):
            ts_server.close()
        sys.exit("Could not create listening socket")
    
    print("Debug: Successfully created listening socket")
    
    # Probably need to add multi threading
    while True:
        try:
            client, address = ts_server.accept()
            client.settimeout(CLIENT_TIMEOUT)
        
        except socket.timeout:
            print("Listener socket timed out waiting for RS")
            break
        
        except OSError as e:
            print(e)
            ts_server.close()
            sys.exit("Failed to accept incoming connection")
        
        print("Debug: Created connection with {}:{}".format(address[0], address[1]))
        
        try:
            data_recieved = (client.recv(200)).decode("utf-8").lower()
            print("    Debug: Received from RS: {}".format(data_recieved))
            
            if data_recieved in rr_map:
                message = rr_map[data_recieved]
                print("    Debug: Sending to RS: {}".format(message))
                client.send(message.encode("utf-8"))
            else:
                print("    Debug: {} not in rr_map".format(data_recieved))
                
        except socket.timeout:
            print("    Debug: Connection with RS timed out")
        
        # Not a fatal error, just wait for another connection.
        except OSError as e:
            print(e)
            print("    Debug: Connection with RS unexpectedly terminated")
            
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        print("    Debug: Shutdown RS connection")
            
    ts_server.close()
    print("Debug: Listening socket shut down")

if (__name__ == "__main__"):
    parse_RR()
    print(rr_map)
    Main()
    print("ENDING PROGRAM")
