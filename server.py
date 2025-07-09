import socket #allows for creation of client server apps
import threading

HOST = '127.0.0.1' 
PORT = 1234 #can use any port from 0-65535
LISTENER_LIMIT = 2 #only two people can communicate
active_clients = [] #list of all connected users

#listens for any upcoming messages from a client
def listen_for_messages(client, username):
    while 1:
    
        message = client.recv(2048).decode('utf-8')
        if message:
            final_msg = username + '~' + message
            send_message(final_msg)
        else:
            remove_client(client, username)
            break

#sends any new message to other client connected to the server
def send_message(message):
    for user, conn in active_clients:
        conn.sendall(message.encode())
       

#function to remove a client
def remove_client(client, username):
    client.close()
    for user in active_clients:
        if user[0] == username:
            active_clients.remove(user)
            break

#function to handle client
def client_handler(client):
    #server will listen for username
    while 1:
        username = client.recv(2048).decode('utf-8') #decode since everything sent in byte form
        if username != '':
            active_clients.append((username, client))
            break
        else:
            print("username is empty")

    threading.Thread(target=listen_for_messages, args=(client, username, )).start()

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

        #creating a thread to perform the function
        threading.Thread(target=client_handler, args=(client, )).start()

#will only run main when server.py is run directly and not when it's imported
if __name__=='__main__':
    main()
