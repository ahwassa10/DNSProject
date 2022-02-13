import sys

client_port = 0
client_hostname = ""

def parsePort(port):
    if port.isdigit() and int(port) > 0 and int(port) < 65535:
        return int(port)
    else:
        sys.exit("Error: Invalid port number")


def main():
    arguments = sys.argv
    if len(arguments) != 3:
        sys.exit("Error: Incorrect format\nclient.py <rsHostname> <rsListenPort>")
    
    rsHostname = arguments[1]
    rsListenPort = parsePort(arguments[2])
    
    print("Debug: Attemping to create connection at {} : {}".format(rsHostname, rsListenPort))
    
    


if (__name__ == "__main__"):
    main()