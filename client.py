import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

#fonts and colors to be used
BLUE ='lightsteelblue'
BLUE2 = 'white'
BLUE3 = 'azure'
GRAY = 'lightslategray'
WHITE ='white'
FONT = ("Helvitica", 17)
FONT2 = ("Helvitica", 13)

def connect():
    print("yo")

def send_message():
    print("yo mama")

#making gui for users
root = tk.Tk()
root.geometry("600x600")
root.title("Messenger")
root.resizable(False, False)

#assigning specific height to each row
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

#different sections of window
top = tk.Frame(root, width=600, height=100, bg=GRAY)
top.grid(row=0, column=0, sticky=tk.NSEW) #grid divides window into sections for frames to be assigned
#adding features to window
username_label = tk.Label(top, text="Enter username: ", font=FONT, bg=GRAY, fg=BLUE2)
username_label.pack(side=tk.LEFT, padx=10) #positions element in the frame
username_text = tk.Entry(top, font=FONT, bg=GRAY, fg=BLUE2, width=23)
username_text.pack(side=tk.LEFT)
#when user clicks the button, perform the following function
username_button = tk.Button(top, text="Join", font=FONT2, bg=GRAY, fg=BLUE2, command=connect)
username_button.pack(side=tk.LEFT,padx=15)

middle = tk.Frame(root, width=600, height=400, bg=BLUE2)
middle.grid(row=1,column=0, sticky=tk.NSEW)
#displaying messages being sent
message_box = scrolledtext.ScrolledText(middle, font=FONT2, bg=BLUE2, width=60, height=23)
message_box.config(state=tk.DISABLED) #user can't directly add text
message_box.pack(side=tk.LEFT,padx=15)

bottom = tk.Frame(root, width=600, height = 100, bg=GRAY)
bottom.grid(row=2, column=0, sticky=tk.NSEW)
#widgets for bottom frame
message_textbox = tk.Entry(bottom, font=FONT, bg=GRAY, fg=BLUE2, width=38)
message_textbox.pack(side=tk.LEFT, padx=15)
message_button = tk.Button(bottom, text="Send", font=FONT2, bg=GRAY, fg=BLUE2, command=send_message)
message_button.pack(side=tk.LEFT, padx=2)


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

    root.mainloop() #renders window frame by frame


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
