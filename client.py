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

def cleanupSocket():
    if client_hostname != None:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        
        
def readLoop():
    global client_socket
    client_socket.settimeout(10)
    try:
        inputFile  = open("PROJ2-HNS.txt", "r")
        outputFile = open("RESOLVED.txt", "w")
        
        for line in inputFile:
            # Get rid of newline and leading whitespace.
            line = line.strip()
            
            client_socket.send(line.encode("utf-8"))
            print("Debug: Sending to socket: {}".format(line)) 
            data = client_socket.recv(200).decode("utf-8")
            print("Debug: Recv  from socket: {}".format(data))
            outputFile.write(data + '\n')
            
    except socket.timeout:
        cleanupSocket()
        inputFile.close()
        outputFile.close()
        sys.exit("Error: Connection to server timed out")
    
    except OSError as error:
        print(error)
        cleanupSocket()
        inputFile.close()
        outputFile.close()
        sys.exit("Error: Unable to process the input file")


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
    
    readLoop()
    print("Debug: Successfully read through the file")
    
    cleanupSocket()
    print("Debug: Successfully shutdown and closed the socket")

if (__name__ == "__main__"):
    main()