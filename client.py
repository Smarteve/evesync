import os
import socket
import sys
import time
import threading


host = "localhost"
port = 10000

# support multiple clients by passing path of the file as command line arguments
# first client will send the file to the server
# server sync the file to other clients
# if any client made the change, server will sync the change to other clients



def send_file(filename, client):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            file_size = os.path.getsize(filename)
            print(file_size)
            client.send(file_size.to_bytes(4, "big"))
            client.send(f.read())

    else:
        raise ValueError("file does not exist")


def monitor_thread(filename,client) -> None:
    last_modified_time = os.path.getmtime(filename)
    while True:
        current_modified_time = os.path.getmtime(filename)
        if current_modified_time > last_modified_time:
            client.send(b"UPDATE")
            last_modified_time = current_modified_time
            print("file updated")
        time.sleep(1)

 

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    if len(sys.argv) < 2:
        raise ValueError("please provide a file path")
    filename = sys.argv[1]
    data = client.recv(1024).decode().strip()
    print(data)
    if data == "FIRST":  #first client connects, the file should already exist
        if not os.path.exists(filename):
            raise ValueError("file does not exist")
    
    elif data == "NOT_FIRST": # rest clients connect, the file should not exist, waiting for the server to send the file content then update the file
        if os.path.exists(filename):
            raise ValueError("file already exist")
        else:
            file_content = client.recv(1024).decode().rstrip()
            with open(filename, "w") as f:
                f.write(file_content)
            client.send(f"file saved as {filename}\n".encode())
    # t = threading.Thread(target=monitor_thread, args=(filename,client))
    # t.start()
    while True:  # first and no first is one-time thing, after that, the client will be waiting for the server to send the file content, hence the while loop to keep the connection open
        try:
            data = client.recv(1024).decode().strip()
            if data == "GET":    
                send_file(filename, client)
                print("file sent successfully")  
            elif data == "SET":
                ack = client.send(b"ACK\n")
                file_content = client.recv(1024).decode().strip()
                with open(filename, "w") as f:
                    f.write(file_content)
                print("file updated")
        except KeyboardInterrupt:
            break 




     