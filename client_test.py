import socket
import os

def send_data(socket_path="/Users/wmb/.emacs_sync", message='emacs'):
    # Create a UNIX socket
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_socket:
        # Connect to the server
        client_socket.connect(socket_path)
        
        # Send data to the server
        client_socket.sendall(message.encode('utf-8'))
        

if __name__ == "__main__":
    send_data()  # Send a message to the UNIX domain socket server
