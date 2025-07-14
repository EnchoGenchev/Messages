import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import os

HOST = '127.0.0.1'
PORT = 1234

#fonts and colors to be used
BLUE ='lightsteelblue'
BLUE2 = 'white'
BLUE3 = 'azure'
GRAY = 'lightslategray'
WHITE ='white'
FONT = ("Helvitica", 17)
FONT2 = ("Helvitica", 13)

#creating socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #same format as server side

#functions so gui works
def add_message(message):
    message_box.config(state=tk.NORMAL) #temporarily able to change the textbox
    message_box.insert(tk.END, message + '\n') #so that newer messages are seen at the bottom
    message_box.config(state=tk.DISABLED)

def connect():
    #connect to the server
    try:
        client.connect((HOST, PORT))
        add_message("[SERVER] Successfully connected")
    except:
        #error message for gui
        messagebox.showerror("Unable to connect to server", f"unable to connect to server {HOST} {PORT}")

    username = username_text.get() #getting what the user inputted in the gui
    if username != '':
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid username","Username cannot be empty")
        exit(0)

    threading.Thread(target=listen_for_messages, args=(client, )).start()

def send_message():
    message = message_textbox.get() #getting what was typed in the textbox by the user
    client.sendall(message.encode())

def send_file():
    filename = message_textbox.get()
    if not os.path.exists(filename):
        add_message("ERROR: File not found")
    else:
        #making a tag so that can be identified as file in server
        client.sendall(f"FILE:{filename}".encode()) 
        with open(filename, 'rb') as file: #readbytes mode
            while True:
                file_data = file.read(1024)
                if not file_data:
                    break
                client.sendall(file_data)
        client.sendall(b"ENDFILE")  # signal end of file

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
top.grid(row=0, column=0, sticky=tk.NSEW) 
#adding features to window
username_label = tk.Label(top, text="Username:", font=FONT, bg=GRAY, fg=BLUE2)
username_label.pack(side=tk.LEFT, padx=3)
username_text = tk.Entry(top, font=FONT, bg=GRAY, fg=BLUE2, width=9)
username_text.pack(side=tk.LEFT)
username_button = tk.Button(top, text="Join", font=FONT2, bg=GRAY, fg=BLUE2, command=connect)
username_button.pack(side=tk.LEFT,padx=10)
password_label = tk.Label(top, text="Key:", font=FONT, bg=GRAY, fg=BLUE2)
password_label.pack(side=tk.LEFT, padx=3)
password_text = tk.Entry(top, font=FONT, bg=GRAY, fg=BLUE2, width=9)
password_text.pack(side=tk.LEFT)
#dropdown menu for bits
bit_var = tk.StringVar(top)
bit_var.set("Bits")  # Initial display
bit_dropdown = tk.OptionMenu(top, bit_var, "56-bit", "128-bit")
bit_dropdown.config(font=FONT2, bg=GRAY, fg=BLUE2)
bit_dropdown.pack(side=tk.LEFT, padx=5)


middle = tk.Frame(root, width=600, height=400, bg=BLUE2)
middle.grid(row=1,column=0, sticky=tk.NSEW)
message_box = scrolledtext.ScrolledText(middle, font=FONT2, bg=BLUE2, width=60, height=23)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.LEFT,padx=15)

bottom = tk.Frame(root, width=600, height = 100, bg=GRAY)
bottom.grid(row=2, column=0, sticky=tk.NSEW)
message_textbox = tk.Entry(bottom, font=FONT, bg=GRAY, fg=BLUE2, width=34)
message_textbox.pack(side=tk.LEFT, padx=15)
message_button = tk.Button(bottom, text="Text", font=FONT2, bg=GRAY, fg=BLUE2, command=send_message)
message_button.pack(side=tk.LEFT, padx=2)
file_button = tk.Button(bottom, text="File", font=FONT2, bg=GRAY, fg=BLUE2, command=send_file)
file_button.pack(side=tk.LEFT, padx=2)

def listen_for_messages(client):
    while 1:
        try:
            message = client.recv(2048)
            if message.startswith(b"FILE:"):
                filename = message.decode().split(":", 1)[1]
                add_message(f"[SERVER] Receiving file: {filename}")
                with open("RECEIVED_" + os.path.basename(filename), 'wb') as f:
                    data = client.recv(1024)
                    f.write(data)
                add_message(f"[SERVER] File {filename} received successfully")
            else:
                decoded = message.decode('utf-8')
                username = decoded.split("~")[0]
                content = decoded.split("~")[1]
                add_message(f"[{username}] {content}")
        except:
            break

def main():
    root.mainloop()

if __name__ == '__main__':
    main()
