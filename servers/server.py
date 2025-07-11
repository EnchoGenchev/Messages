import socket #allows for creation of client server apps
import threading

HOST = '127.0.0.1' 
PORT = 1234 #can use any port from 0-65535
LISTENER_LIMIT = 2 #only two people can communicate
active_clients = [] #list of all connected users

#listens for any upcoming messages from a client
def listen_for_messages(client, username):
    while 1:
        try:
            message = client.recv(2048)
            if message.startswith(b"FILE:"):
                filename = message.decode().split(":", 1)[1]
                receive_file(client, filename, username)
            else:
                final_msg = username + '~' + message.decode('utf-8')
                send_message(final_msg)
        except:
            remove_client(client, username)
            break

#sends any new message to other client connected to the server
def send_message(message):
    for user, conn in active_clients:
        conn.sendall(message.encode())

def receive_file(client, filename, username):
    file_data = client.recv(1024)
    # saving on server side
    with open("SERVER_" + filename, 'wb') as f:
        f.write(file_data)

    # send file to all clients
    for user, conn in active_clients:
        if conn != client:
            conn.sendall(f"FILE:{filename}".encode())
            conn.sendall(file_data)

#function to remove a client
def remove_client(client, username):
    client.close()
    for user in active_clients:
        if user[0] == username:
            active_clients.remove(user)
            break

#function to handle client
def client_handler(client):
    while 1:
        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
            break
        else:
            print("username is empty")

    threading.Thread(target=listen_for_messages, args=(client, username, )).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        print(f"server is running on {HOST} {PORT}")
    except:
        print(f"unable to bind to host {HOST} and port {PORT}")

    server.listen(LISTENER_LIMIT)

    while 1:
        client, address = server.accept() 
        print(f"successfully connected to client {address[0]} {address[1]}")
        threading.Thread(target=client_handler, args=(client, )).start()

if __name__=='__main__':
    main()
