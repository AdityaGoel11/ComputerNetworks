import socket

SERVER_IP = "10.237.26.109"  # Replace with the IP address of your UDP server
SERVER_PORT = 9801       # Replace with the port number of your UDP server
BUFFER_SIZE = 1448

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Input a message to send to the server
message = input("SendSize\n \n")

# Send the message to the server
sock.sendto(message.encode(), (SERVER_IP, SERVER_PORT))

# Receive a response from the server
data, server_address = sock.recvfrom(BUFFER_SIZE)

print("Server response:", data.decode())

# Close the socket
sock.close()
