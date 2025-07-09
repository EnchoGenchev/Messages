import socket #allows for creation of client server apps
import threading

HOST = '127.0.0.1' 
PORT = 1234 #can use any port from 0-65535
LISTENER_LIMIT = 2 #only two people can communicate

def main():
    #creating the socket object
    #AF_INET: using IPv4 addresses
    #SOCK_STREAM: using TCP packets (transmission control protocols)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #try catch block to make sure host and port are available
    try:
        #provid the server with address
        server.bind((HOST, PORT))
        print(f"server is running on {HOST} {PORT}")
    except:
        print(f"unable to binf to host {HOST} and port {PORT}")

    #set server limit
    server.listen(LISTENER_LIMIT)

    #will keep listening to client connections
    while 1:
        client, address = server.accept() 
        print(f"successfully connected to client {address[0]} {address[1]}") #address is a double (host and port)

#will only run main when server.py is run directly and not when it's imported
if __name__=='__main__':
    main()