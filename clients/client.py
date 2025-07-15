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

BLUE = 'lightsteelblue'
BLUE2 = 'white'
BLUE3 = 'azure'
GRAY = 'lightslategray'
WHITE = 'white'
FONT = ("Helvetica", 17)
FONT2 = ("Helvetica", 13)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def derive_key(key_text, bits):
    if bits == "56-bit":
        return hashlib.sha256(key_text.encode()).digest()[:8]
    return hashlib.sha256(key_text.encode()).digest()[:16]

def encrypt_file_bytes(data, key, bits):
    if bits == "56-bit":
        iv = get_random_bytes(8)
        cipher = DES.new(key, DES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data, DES.block_size))
    else:
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data, AES.block_size))
    return iv + encrypted

def decrypt_file_bytes(data, key, bits):
    try:
        if bits == "56-bit":
            iv, encrypted = data[:8], data[8:]
            cipher = DES.new(key, DES.MODE_CBC, iv)
            return unpad(cipher.decrypt(encrypted), DES.block_size)
        else:
            iv, encrypted = data[:16], data[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            return unpad(cipher.decrypt(encrypted), AES.block_size)
    except:
        return data

def add_message(message):
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
    if username != '':
        client.sendall(username.encode())
    else:
        messagebox.showerror("Invalid Username", "Username cannot be empty")
        exit(0)

    threading.Thread(target=listen_for_messages, args=(client,)).start()

def send_message():
    message = message_textbox.get()
    key_input = password_text.get()
    bits = bit_var.get()

    if not message or not key_input or bits not in ["56-bit", "128-bit"]:
        add_message("ERROR: Missing message, key, or bit selection")
        return

    key = derive_key(key_input, bits)
    encrypted = encrypt_file_bytes(message.encode(), key, bits)
    client.sendall(encrypted)
    message_textbox.delete(0, tk.END)

def send_file():
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
    with open(filename, 'rb') as f:
        plaintext = f.read()
    encrypted_data = encrypt_file_bytes(plaintext, key, bits)

    client.sendall(f"FILE:{filename}".encode())
    client.sendall(encrypted_data)
    client.sendall(b"ENDFILE")

    add_message(f"[YOU] Sent encrypted file {filename}")
    message_textbox.delete(0, tk.END)

def listen_for_messages(client):
    while True:
        try:
            message = client.recv(2048)
            if message.startswith(b"FILE:"):
                filename = message.decode().split(":", 1)[1]
                add_message(f"[SERVER] Receiving file: {filename}")
                buffer = b""
                while True:
                    chunk = client.recv(1024)
                    if b"ENDFILE" in chunk:
                        buffer += chunk.replace(b"ENDFILE", b"")
                        break
                    buffer += chunk

                key_input = password_text.get()
                bits = bit_var.get()
                key = derive_key(key_input, bits)

                decrypted_data = decrypt_file_bytes(buffer, key, bits)
                with open("RECEIVED_" + os.path.basename(filename), 'wb') as f:
                    f.write(decrypted_data)
                add_message(f"[SERVER] File {filename} received")
            else:
                username, encrypted = message.split(b"~", 1)
                key_input = password_text.get()
                bits = bit_var.get()
                key = derive_key(key_input, bits)
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
root.resizable(False, False)

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

if __name__ == '__main__':
    main()
