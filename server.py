# Import required modules
import socket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Host and port number
HOST = '127.0.0.1'
PORT = 1738
LISTENER_LIMIT = 10
active_clients = [] # List of all currently connected users

# Encryption key 
KEY = b'my_secret_key_12'

# AES decryption function
def decrypt_message(encrypted_message):
    iv = base64.b64decode(encrypted_message[:24])
    ct = base64.b64decode(encrypted_message[24:])
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted_message = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    return decrypted_message

# Function to listen for upcoming messages from a client
def listen_for_messages(client, username):

    while 1:

        encrypted_message = client.recv(2048).decode('utf-8')
        if encrypted_message != '':
            message = decrypt_message(encrypted_message)
            final_msg = username + '~' + message
            send_messages_to_all(final_msg)

        else:
            print(f"The message sent from client {username} is empty")


# Function to send message to a single client
def send_message_to_client(client, message):

    client.sendall(message.encode())

# Function to send any new message to all the clients that
# are currently connected to this server
def send_messages_to_all(message):
    
    for user in active_clients:

        send_message_to_client(user[1], message)

# Function to handle client
def client_handler(client):
    
    # Server will listen for client message that will
    # Contain the username
    while 1:

        username = client.recv(2048).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
            prompt_message = "SERVER~" + f"{username} added to the chat"
            send_messages_to_all(prompt_message)
            break
        else:
            print("Client username is empty")

    threading.Thread(target=listen_for_messages, args=(client, username, )).start()

# Main function
def main():

    # Creating the socket class object
    # AF_INET: we are going to use IPv4 addresses
    # SOCK_STREAM: we are using TCP packets for communication
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creating a try catch block
    try:
        # Provide the server with an address in the form of
        # host IP and port
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")

    # Set server limit
    server.listen(LISTENER_LIMIT)

    # This while loop will keep listening to client connections
    while 1:

        client, address = server.accept()
        print(f"Successfully connected to client {address[0]} {address[1]}")

        threading.Thread(target=client_handler, args=(client, )).start()

# Main function
if __name__ == '__main__':
    main()
