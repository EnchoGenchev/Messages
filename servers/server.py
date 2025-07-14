import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 2
active_clients = []

def listen_for_messages(client, username):
    while True:
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

def send_message(message):
    for user, conn in active_clients:
        conn.sendall(message.encode())

def receive_file(client, filename, username):
    file_data = b""
    while True:
        chunk = client.recv(1024)
        if b"ENDFILE" in chunk:
            file_data += chunk.replace(b"ENDFILE", b"")
            break
        file_data += chunk

    with open("SERVER_" + filename, 'wb') as f:
        f.write(file_data)

    for user, conn in active_clients:
        if conn != client:
            conn.sendall(f"FILE:{filename}".encode())
            conn.sendall(file_data)
            conn.sendall(b"ENDFILE")

def remove_client(client, username):
    client.close()
    for user in active_clients:
        if user[0] == username:
            active_clients.remove(user)
            break

def client_handler(client):
    while True:
        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
            break

    threading.Thread(target=listen_for_messages, args=(client, username)).start()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        print(f"Server running on {HOST}:{PORT}")
    except:
        print(f"Bind failed on {HOST}:{PORT}")

    server.listen(LISTENER_LIMIT)

    while True:
        client, address = server.accept()
        print(f"Connected to client {address}")
        threading.Thread(target=client_handler, args=(client,)).start()

if __name__ == '__main__':
    main()
