import socket
import sys
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Function to generate a key pair (private key and corresponding public key)
def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

# Function to serialize a key (convert key to bytes)
def serialize_key(key):
    return key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

# Function to receive data from a socket
def receive_data(socket, buffer_size=1024):
    try:
        data = socket.recv(buffer_size)
        return data
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None

# Function to send data through a socket
def send_data(socket, data):
    try:
        socket.sendall(data)
    except Exception as e:
        print(f"Error sending data: {e}")

# Function to encrypt a message using a symmetric key
def encrypt_message(message, symmetric_key):
    iv = os.urandom(16)  # Generate a random initialization vector
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padded_message = message.encode('utf-8') + b'\0' * (32 - len(message) % 32)  
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()
    return iv + encrypted_message

# Function to decrypt a message using a symmetric key
def decrypt_message(encrypted_message, symmetric_key):
    iv = encrypted_message[:16]  # Extract the initialization vector
    ciphertext = encrypted_message[16:]
    cipher = Cipher(algorithms.AES(symmetric_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_message.rstrip(b'\0').decode('utf-8')

# Main function
def main():
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        return

    # Extract server IP and port from command-line arguments
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    try:
        # Create a client socket and connect to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        # Generate a key pair for the client (private key and public key)
        private_key, public_key = generate_key_pair()

        # Send the client's public key to the server
        send_data(client_socket, serialize_key(public_key))

        # Receive the server's public key
        server_public_key_data = receive_data(client_socket)
        if server_public_key_data:
            server_public_key = serialization.load_pem_public_key(server_public_key_data, backend=default_backend())
        else:
            print("Error receiving server's public key.")
            return

        # Receive the encrypted symmetric key and decrypt it with the client's private key
        symmetric_key_encrypted = receive_data(client_socket)
        symmetric_key = private_key.decrypt(
            symmetric_key_encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),  # Use SHA-512
                algorithm=hashes.SHA512(),  # Use SHA-512
                label=None
            )
        )

        # Main communication loop
        while True:
            message = input("Enter a message (or 'exit' to quit): ")
            if message.lower() == 'exit':
                break

            # Encrypt the message with the symmetric key and send it
            encrypted_message = encrypt_message(message, symmetric_key)
            print(f"Original message: {message}")
            print(f"Encrypted message: {encrypted_message}")

            send_data(client_socket, encrypted_message)

        # Close the connection
        client_socket.close()

    except Exception as e:
        print(f"An error occurred: {e}")

# Entry point of the script
if __name__ == "__main__":
    main()

