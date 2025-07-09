import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

def listen_for_messages(client):
    while 1:
        message = client.recv(2048).decode('utf-8')
        username = message.split("~")[0]
        content = message.split("~")[1]
        print(f"[{username}] {content}")

def send_message(client):
    while 1:
        message = input("Message: ")
        client.sendall(message.encode())

def communicate_to_server(client):

    username = input("Enter username: ")
    if username != '':
        client.sendall(username.encode())
    else:
        print("Username cannot be empty")
        exit(0)

    threading.Thread(target=listen_for_messages, args=(client, )).start()

    send_message(client)


def main():
    #creating socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #same format as server side

    #connect to the server
    try:
        client.connect((HOST, PORT))
        print("successfully connected to server")
    except:
        print(f"unable to connect to server {HOST} {PORT}")
        return

    communicate_to_server(client)


#good practice
if __name__ == '__main__':
    main()
