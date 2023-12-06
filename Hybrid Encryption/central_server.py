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
    if len(sys.argv) != 2:
        print("Usage: python server.py <server_port>")
        return

    # Extract server port from command-line arguments
    server_port = int(sys.argv[1])

    try:
        # Create a server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', server_port))
        server_socket.listen()
        print("Waiting for connections!")

        # Accept a connection from a client
        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        # Generate a key pair for the server (private key and public key)
        private_key, public_key = generate_key_pair()

        # Send the server's public key to the client
        conn.sendall(serialize_key(public_key))

        # Receive the client's public key
        client_public_key_data = conn.recv(1024)
        if not client_public_key_data:
            raise Exception("Error receiving client's public key")

        # Deserialize the client's public key
        client_public_key = serialization.load_pem_public_key(client_public_key_data, backend=default_backend())

        # Generate a random symmetric key for secure communication
        symmetric_key = os.urandom(32)

        # Encrypt the symmetric key with the client's public key and send it
        encrypted_symmetric_key = client_public_key.encrypt(
            symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA512()),  
                algorithm=hashes.SHA512(),  
                label=None
            )
        )
        conn.sendall(encrypted_symmetric_key)

        # Main communication loop
        while True:
            message = conn.recv(1024)
            if not message:
                break

            # Decrypt the received message using the symmetric key
            decrypted_message = decrypt_message(message, symmetric_key)
            print(f"Received encrypted message: {message}")
            #print(f"Decrypted message: {decrypted_message}")

        # Close the connection
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

# Entry point of the script
if __name__ == "__main__":
    main()

