import socket
import sys

client_port = 0
client_hostname = ""
client_socket = None

def parsePort(port):
    if port.isdigit() and int(port) > 0 and int(port) < 65535:
        return int(port)
    else:
        sys.exit("Error: Invalid port number")

def createSocket():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((client_hostname, client_port))
        
    except OSError as error:
        print(error)
        sys.exit("Error: Unable to establish connection at {} : {}".format(client_hostname, client_port))
        
    
    

def main():
    arguments = sys.argv
    if len(arguments) != 3:
        sys.exit("Error: Incorrect format\nclient.py <rsHostname> <rsListenPort>")
    
    
    global client_hostname
    global client_port
    
    client_hostname = arguments[1]
    client_port     = parsePort(arguments[2])
    
    print("Debug: Attemping to create connection at {} : {}".format(client_hostname, client_port))
    createSocket()
    print("Debug: Created connection at {} : {}".format(client_hostname, client_port))
    
    
    
    
    client_socket.shutdown()
    client_socket.close()

if (__name__ == "__main__"):
    main()