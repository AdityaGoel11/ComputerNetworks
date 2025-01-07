import socket
import hashlib
import threading
import time


def send_request(offset, num_bytes):
    request = f"Offset: {offset}\nNumBytes: {num_bytes}\n\n"
    sock.sendto(request.encode(), (SERVER_HOSTNAME, SERVER_PORT))


def data_request(size, chunk_size, recieved_data):
    offset=0
    while offset < size:
        send_request(offset,chunk_size)
        offset=offset+chunk_size
        time.sleep(5)

    while not stop_event.is_set():    
        i=0
        while i < size:
            if received_data[i] == 0:
                send_request(i,chunk_size)
                i += chunk_size
                time.sleep(5)
     


def send_md5_submission(md5_hash, entry_id):
    submission = f"Submit: {entry_id}@team\nMD5: {md5_hash}\n\n"
    sock.sendto(submission.encode(), (SERVER_HOSTNAME, SERVER_PORT))


# Server information
SERVER_HOSTNAME = "127.0.0.0.1"
SERVER_PORT = 9801
stop_event = threading.Event()

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send a request to the server to get the number of bytes to receive
send_size_command = "SendSize\n\n"
sock.sendto(send_size_command.encode(), (SERVER_HOSTNAME, SERVER_PORT))

# Receive the response from the server
response, server_address = sock.recvfrom(1448)
response = response.decode()
#print(response[6:12])
size =  int(response[6:12])
chunk_size = 1024
received_data = bytearray(size)

dataRequestThread = threading.Thread(target=data_request, args=(size,chunk_size,received_data))
dataRequestThread.start()

# Now, send requests to receive data in chunks
bytes_recieved = 0

while bytes_recieved < size:
    # Receive the response from the server
    response, server_address = sock.recvfrom(1448)
    response = response.decode()

    if response.startswith("Offset: ") and response.endswith("\n"):
        response_lines = response.strip().split("\n")
        response_offset = int(response_lines[0][len("Offset: "):])
        response_size = int(response_lines[1][len("NumBytes: "):])
        response_data = response_lines[-1].encode()
        received_data[response_offset:len(response_data)] = response_data
        bytes_recieved += response_size

    else:
        print("Unexpected response from the server:", response)

print("Received all data.")
stop_event.set()
dataRequestThread.join()

# Calculate MD5 hash of received_data
md5_hash = hashlib.md5(received_data).hexdigest()
print("MD5 Hash:", md5_hash)

# Submit the MD5 hash to the server
send_md5_submission(md5_hash, "YourEntryID")  # Replace "YourEntryID" with your actual team's entry ID

# Receive the response from the server
response, server_address = sock.recvfrom(1024)
response = response.decode()

if response.startswith("Result: "):
    result_lines = response.strip().split("\n")
    result_line = result_lines[0][len("Result: "):]
    result, time, penalty = result_line.split()

    print(f"MD5 Hash Check Result: {result}")
    print(f"Time Taken (ms): {time}")
    print(f"Penalty: {penalty}")

else:
    print("Unexpected response from the server:", response)

# Close the socket
sock.close()
