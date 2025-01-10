import socket
import time


central_server_host = "10.184.58.128"
central_server_port = 9805
server_host = "vayu.iitd.ac.in"
server_port = 9801
command = "SENDLINE\n"
total_lines = 1000
lines_per_second = 100
time_interval = 1 / lines_per_second
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_host, server_port))

central_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
central_socket.connect((central_server_host, central_server_port))

received_lines = 0
start_time = time.time()
dic = {}
done = False


ans = ""
ans += "SUBMIT\n"
ans += "2020CS10317@deepthought\n"
ans += "1000\n"

while len(dic)!= total_lines:
    client_socket.send(command.encode())
    response = ""
    while response=="" or response[-1] != "\n":
        response += client_socket.recv(4096).decode()
    if (not (response[0] <= '9' and response[0] >= '0')):
        continue

    input_string = response
    newline_index = input_string.index("\n")
    number_str = input_string[:newline_index]
    rest_line= input_string[newline_index+1:]
    number = int(number_str)

    if number not in dic:
        dic[number] = rest_line
        # print(f"Received line {number}")
        message = '[' + number_str + ']' + rest_line
        central_socket.send(message.encode()) 
        res = ""
        note_time = time.time() 
        while res=="" or res[len(res)-2:]!= "##":
            res += central_socket.recv(4096).decode()
            # print(res) 
            # if (res[len(res)-2:]=="##") : break ; 
        if (res != "bkl##"): 
            # print("DONE")
            # print("time for message transfer is ", time.time() - note_time)
            ans += res 
            break  
        received_lines += 1


# message += res 
# print("hello world")
ans = ans[:len(ans)-2]
# print(ans)
j = 0
client_socket.send(ans.encode())

response_f = ""
while response_f == "" or response_f[-1]!="\n":
    response_f += client_socket.recv(4096).decode()
    # print("in")
print(response_f)
print(time.time() - start_time)

client_socket.close()
