import socket
import hashlib
import re
import time
import threading
from threading import Thread
import queue


def data_request(size, chunk_size, q1, q2, q3, time_period, burstSize, event):
    offset=0
    # start_time = time.time()
    ctr = 0
    while offset < size:
        if(size-offset>=chunk_size):
            send_request(offset,chunk_size)
        else:
            send_request(offset, size-offset)    
        offset += chunk_size
        ctr += 1
        q1.put(offset)
        if(ctr == burstSize):
            # curtime = time.time()
            # print(burstSize, curtime-start_time)
            ctr = 0
            q1.put(-1)
            time.sleep(time_period)
            if q3.empty() == False:
                s = q3.get()
                if burstSize == s:
                    burstSize += 1
                else:
                    burstSize = int(burstSize/2) +1
            else:
                pass         
            
        

    while event.is_set() == False:    
        offset = q2.get()
        if offset == None:
            time.sleep(time_period)
            continue
        if(size-offset>=chunk_size):
            send_request(offset,chunk_size)
        else:
            send_request(offset, size-offset) 
        ctr += 1
        q1.put(offset)
        if(ctr == burstSize):
            # curtime = time.time()
            # print(burstSize, curtime-start_time)
            ctr = 0
            q1.put(-1)
            time.sleep(time_period)
            if q3.empty() == False:
                s = q3.get()
                if burstSize == s:
                    burstSize += 1
                else:
                    burstSize = int(burstSize/2) +1 
            else:
                pass 
        


def data_accept(size, chunk_size, q1, q2, q3, event):
    received_data_dict = {}
    recieved_data_size = 0
    received_data = b""
    ctr = 0
    while recieved_data_size != size:
        try:
            ctr += 1
            expected_offset = q1.get(block=False)
            if expected_offset == -1:
                q3.put(ctr)
                expected_offset = q1.get()
                ctr = 0

            response, server_address = sock.recvfrom(2096)
            data = response.decode()
            lines = data.split('\n')
            data_contents = ""
            num = 0
            offset = 0
            for line in lines:
                if line.startswith("Offset:"):
                    offset = int(line.split(":")[1].strip())
                    num += len(line)
                elif line.startswith("NumBytes:"):
                    num_bytes = int(line.split(":")[1].strip())
                    num += len(line)
                    break       
            s = "\n\n"
            data_contents = data[data.index(s) + len(s):]
            
            if offset in received_data_dict:
                continue
            received_data_dict[offset] = data_contents
            print("Recieved data at offset = " + str(offset))
            recieved_data_size=recieved_data_size+num_bytes  
            
            if expected_offset == offset:
                continue
            else:
                q2.put(expected_offset)   
        except Exception as e:
            # print(e)
            i = 0
            while i < size:
                if i not in received_data_dict:
                    q2.put(i)
                i += chunk_size
            continue

    event.set()
    received_data = "".join(data for offset, data in sorted(received_data_dict.items()))   
    md5_hash = hashlib.md5(received_data.encode()).hexdigest()
    send_md5_submission(md5_hash, "2020CS10317")
    response, server_address = sock.recvfrom(2096)
    response = response.decode()
    print(response)
    sock.close()   


def send_request(offset, num_bytes):
    request = f"Offset: {offset}\nNumBytes: {num_bytes}\n\n"
    sock.sendto(request.encode(), (SERVER_HOSTNAME, SERVER_PORT))     


def send_md5_submission(md5_hash, entry_id):
    submission = f"Submit: {entry_id}@BroForce\nMD5: {md5_hash}\n\n"
    sock.sendto(submission.encode(), (SERVER_HOSTNAME, SERVER_PORT))


# Server information
SERVER_HOSTNAME = "127.0.0.1"
# SERVER_HOSTNAME = "vayu.iitd.ac.in"
SERVER_PORT = 9802

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1)

send_size_command = "SendSize\n\n"
sock.sendto(send_size_command.encode(), (SERVER_HOSTNAME, SERVER_PORT))

response, server_address = sock.recvfrom(1448)
response = response.decode()
size =  int(response[6:12])
chunk_size = 1448
dic = {}
timeperiod = 0.05
burstSize = 10
q1 = queue.Queue()
q2 = queue.Queue()
q3 = queue.Queue()
event = threading.Event()

dataRequestThread = threading.Thread(target=data_request, args=(size,chunk_size, q1, q2, q3, timeperiod, burstSize, event))
dataAcceptThread = threading.Thread(target=data_accept, args=(size, chunk_size, q1, q2, q3, event))
dataRequestThread.start()
dataAcceptThread.start()
