import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import os
from Crypto.Cipher import DES, AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib

HOST = '127.0.0.1'
PORT = 1234

#constants for GUI design
BLUE = 'lightsteelblue'
BLUE2 = 'white'
BLUE3 = 'azure'
GRAY = 'lightslategray'
WHITE = 'white'
FONT = ("Helvetica", 17)
FONT2 = ("Helvetica", 13)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def derive_key(key_text, bits):
    #for both hashes using sha256 but only takes however many bytes each option needs
    if bits == "56-bit":
        return hashlib.sha256(key_text.encode()).digest()[:8] #takes the first 8 bytes (64 bits)
    return hashlib.sha256(key_text.encode()).digest()[:16] #takes the first 16 bytes (128 bits)

def encrypt_file_bytes(data, key, bits):
    if bits == "56-bit":
        iv = get_random_bytes(8) #different for each encryption for better security
        cipher = DES.new(key, DES.MODE_CBC, iv) 
        encrypted = cipher.encrypt(pad(data, DES.block_size)) #pads and then encrypts
    else:
        iv = get_random_bytes(16) #aes needs longer iv
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
    return iv + encrypted #combines IV and encryption so it can be decrypted with same iv by other user

def decrypt_file_bytes(data, key, bits):
    try:
        if bits == "56-bit":
            iv = data[:8] #gets first bits which are the iv
            encrypted = data[8:] #gets all the bits after the iv
            cipher = DES.new(key, DES.MODE_CBC, iv) #creates the cipher with key from receiver
            return unpad(cipher.decrypt(encrypted), DES.block_size) #removes padding and decrypts to get og data
        else:
            iv = data[:16] #gets first bits which are the iv
            encrypted = data[16:] #gets all the bits after the iv
            cipher = AES.new(key, AES.MODE_CBC, iv) #creates the cipher with key from receiver
            return unpad(cipher.decrypt(encrypted), AES.block_size) #removes padding and decrypts to get og data
    except:
        return data

def add_message(message): #adds message to the stream visible by both users
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

def connect():
    try:
        client.connect((HOST, PORT))
        add_message("[SERVER] Connected")
    except:
        messagebox.showerror("Connection Error", f"Unable to connect to {HOST}:{PORT}")
        return

    username = username_text.get()
    #making sure that there is in fact a user connected
    if username != '':
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid Username", "Username cannot be empty")
        exit(0)

    #creating thread for each user listening for incoming messages/files
    threading.Thread(target=listen_for_messages, args=(client,)).start()

def send_message():
    message = message_textbox.get() #takes message from textbox at the bottom
    key_input = password_text.get() #gets the key from the password box at the top
    bits = bit_var.get() #checks whether using 56 or 128 bits

    #user needs to pick a bit value
    if not message or not key_input or bits not in ["56-bit", "128-bit"]:
        add_message("ERROR: Missing message, key, or bit selection")
        return

    key = derive_key(key_input, bits)
    encrypted = encrypt_file_bytes(message.encode(), key, bits)
    client.sendall(encrypted) #sending encrypted data to all the users via the server
    message_textbox.delete(0, tk.END) #getting rid of what was just typed after sending 

def send_file(): #functions similarly to the send_message function
    filename = message_textbox.get()
    key_input = password_text.get()
    bits = bit_var.get()

    if not os.path.exists(filename):
        add_message("ERROR: File not found")
        return
    if key_input == "" or bits not in ["56-bit", "128-bit"]:
        add_message("ERROR: Missing key or bit selection")
        return

    key = derive_key(key_input, bits)
    #the only differece from the send_message function is that the file is opened, read, and the text is sent
    with open(filename, 'rb') as f: 
        plaintext = f.read()
    encrypted_data = encrypt_file_bytes(plaintext, key, bits)

    #adds tag for easy identification and reading later
    client.sendall(f"FILE:{filename}".encode()) 
    client.sendall(encrypted_data)
    client.sendall(b"ENDFILE")

    add_message(f"[YOU] Sent encrypted file {filename}")
    message_textbox.delete(0, tk.END)

def listen_for_messages(client):
    while True:
        try:
            message = client.recv(2048) #limiting message length 
            if message.startswith(b"FILE:"): #reads tag added 
                filename = message.decode().split(":", 1)[1] 
                add_message(f"[SERVER] Receiving file: {filename}")
                buffer = b""

                #reads the chunks and appends them to buffer until ENDFILE is reached
                while True:
                    chunk = client.recv(1024)
                    if b"ENDFILE" in chunk:
                        buffer += chunk.replace(b"ENDFILE", b"")
                        break
                    buffer += chunk

                #creates key from receivers info to decrypt
                key_input = password_text.get() 
                bits = bit_var.get()
                key = derive_key(key_input, bits)

                decrypted_data = decrypt_file_bytes(buffer, key, bits)
                with open("RECEIVED_" + os.path.basename(filename), 'wb') as f:
                    f.write(decrypted_data)
                add_message(f"[SERVER] File {filename} received")
                #if the key or bits are incorrect, the reciever just gets a junk file

            else: #if just sending a regular message
                username, encrypted = message.split(b"~", 1)

                #creates key from receivers info to decrypt
                key_input = password_text.get()
                bits = bit_var.get()
                key = derive_key(key_input, bits)

                #try-catch because a lot of the encrypted symbols don't like being printed to the message stream
                try:
                    decrypted = decrypt_file_bytes(encrypted, key, bits).decode('utf-8')
                    add_message(f"[{username.decode()}] {decrypted}")
                except:
                    add_message(f"[{username.decode()}] <INCORRECT KEY>")
                
        except Exception as e:
            add_message(f"Connection lost: {e}")
            break

# GUI setup
root = tk.Tk()
root.geometry("600x600")
root.title("Messenger")
root.resizable(False, False) #since each widget is a fixed size

#setting the sizes of each widget
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=4)
root.grid_rowconfigure(2, weight=1)

top = tk.Frame(root, width=600, height=100, bg=GRAY)
top.grid(row=0, column=0, sticky=tk.NSEW)
username_label = tk.Label(top, text="Username:", font=FONT, bg=GRAY, fg=BLUE2)
username_label.pack(side=tk.LEFT, padx=3)
username_text = tk.Entry(top, font=FONT, bg=GRAY, fg=BLUE2, width=9)
username_text.pack(side=tk.LEFT)
username_button = tk.Button(top, text="Join", font=FONT2, bg=GRAY, fg=BLUE2, command=connect)
username_button.pack(side=tk.LEFT, padx=10)
password_label = tk.Label(top, text="Key:", font=FONT, bg=GRAY, fg=BLUE2)
password_label.pack(side=tk.LEFT, padx=3)
password_text = tk.Entry(top, font=FONT, bg=GRAY, fg=BLUE2, width=9)
password_text.pack(side=tk.LEFT)
bit_var = tk.StringVar(top)
bit_var.set("Bits")
bit_dropdown = tk.OptionMenu(top, bit_var, "56-bit", "128-bit")
bit_dropdown.config(font=FONT2, bg=GRAY, fg=BLUE2)
bit_dropdown.pack(side=tk.LEFT, padx=5)

middle = tk.Frame(root, width=600, height=400, bg=BLUE2)
middle.grid(row=1, column=0, sticky=tk.NSEW)
message_box = scrolledtext.ScrolledText(middle, font=FONT2, bg=BLUE2, width=60, height=23)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.LEFT, padx=15)

bottom = tk.Frame(root, width=600, height=100, bg=GRAY)
bottom.grid(row=2, column=0, sticky=tk.NSEW)
message_textbox = tk.Entry(bottom, font=FONT, bg=GRAY, fg=BLUE2, width=34)
message_textbox.pack(side=tk.LEFT, padx=15)
message_button = tk.Button(bottom, text="Text", font=FONT2, bg=GRAY, fg=BLUE2, command=send_message)
message_button.pack(side=tk.LEFT, padx=2)
file_button = tk.Button(bottom, text="File", font=FONT2, bg=GRAY, fg=BLUE2, command=send_file)
file_button.pack(side=tk.LEFT, padx=2)


def main():
    root.mainloop()

#so only run when called upon
if __name__ == '__main__':
    main()
