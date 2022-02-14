import socket
import sys
PORT = int(sys.argv[1])
ADDRESS = ""

CLIENT_TIMEOUT_SINKHOLE = True

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
    except OSError as e:
        print("Could not create socket")
        sys.exit(0)
    
    try:
        ts_server.bind((socket.gethostbyname(socket.gethostname()), PORT))
    except OSError as e:
        print("Could not bind socket")
        sys.exit(0)

    try:
        ts_server.listen(1)
    except OSError as e:
        print("Count not listen to socket")


    # Probably need to add multi threading
    while True:
        client, address = ts_server.accept()
        
        data_recieved = (client.recv(200)).decode("utf-8")
        resolver_output = resolve_host(data_recieved)
        if resolver_output is None:
            while CLIENT_TIMEOUT_SINKHOLE:
                pass
        try:
            client.send(resolver_output.encode("utf-8"))
        except socket.error as e:
            client.close()
            break
        client.close()
            
    ts_server.close()

Main()
print("ENDING PROGRAM")
