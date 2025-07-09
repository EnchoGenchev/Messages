import socket
import threading

HOST = '127.0.0.1'
PORT = 1234

def main():
    #creatng socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #same format as server side

    #connect to the server
    try:
        client.connect((HOST, PORT))
        print("successfully connected to server")
    except:
        print(f"unable to connect to server {HOST} {PORT}")


#good practice
if __name__ == '__main__':
    main()