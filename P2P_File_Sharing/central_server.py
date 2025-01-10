import socket
import threading
import time

# Central server information
central_server_host = "10.184.58.128"
central_server_port = 9805


# Shared dictionary to store received line numbers
main_dictionary = {}
total_unique_lines = 1000  # Change this to 1000
start_time = 0 
# Central server handling client connections
def handle_client(client_socket):
    while True:
        try : 
            # client_socket.send(msg.encode()) 
            data = client_socket.recv(4096).decode()
            if not data : 
                break 
            while data[-1]!='\n' : 
                data += client_socket.recv(4096).decode()
            if(len(data)<2): 
                break 
            num = "" 
            i = 1 
            while i<len(data) and data[i]!= ']': 
                num+= data[i] 
                i+= 1
            i+= 1
            main_dictionary[int(num)] = data[i:]
            if len(main_dictionary)%50==0 : 
                print(len(main_dictionary)) 
                print(time.time()- start_time)
            # print(len(main_dictionary))
            if len(main_dictionary)==total_unique_lines: 
                print(time.time() - start_time)
                try:
                    message = ""
                    # message += "SUBMIT\n"
                    # message += "deepthought@col334-672\n"
                    # message += "1000\n"
                    for i in range(0,1000):
                        message += str(i) + '\n'
                        message += main_dictionary[i]
                    client_socket.send(message.encode())
                    client_socket.send("##".encode()) 
                except socket.timeout:
                    break
                return 
            else :
                m = "bkl##"
                client_socket.send(m.encode())

        except :
            client_socket.close() 

    client_socket.close()

def central_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((central_server_host, central_server_port))
    server_socket.listen(5)

    print("Central server listening on", central_server_host, central_server_port)

    while len(main_dictionary) < total_unique_lines:
        client_socket, _ = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        start_time= time.time() 
        client_thread.start()
    server_socket.close()
    print(time.time() - start_time)


if __name__ == "__main__":
    start_time = time.time()
    central_server_thread = threading.Thread(target=central_server)
    central_server_thread.start()

    # print(time.time() - start_time)