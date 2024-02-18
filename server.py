import socket
import threading
from queue import Queue
import random

host = "localhost"
port = 10000


client_list = []

def handle_client(client):
    if len(client_list) == 0:
        client.send(b"FIRST\n")
        client_list.append(client)

    else:
        client.send(b"NOT_FIRST\n")
        random_client = random.choice(client_list)
        random_client.send(b"GET\n") #get the file from a random client before this newly joined client
        file_content = receive_file(random_client)
        client.send(file_content)
        ack = client.recv(1024).decode().strip()
        print(ack)
        client_list.append(client)
    
    while True: # have a while loop to keep the connection open
        pass
        # message = client.recv(1024).decode().strip()
        # if message == "UPDATE":
        #     client.send(b"GET\n")
        #     file_content = receive_file(client)
        #     broadcast_update(file_content, client)



def broadcast_update(file_content, conn):
    for client in client_list:
        if client != conn:
            client.send(b"SET\n")
            message = client.recv(1024).decode().strip()
            if message == "ACK":
                client.send(file_content)

def receive_file(conn: socket.socket) -> bytes:
    print("receiving file")
    file_size = int.from_bytes(conn.recv(4),"big")
    print(file_size)
    content = conn.recv(file_size)
    print(content)
    return content

thread_queue = Queue()
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(
        socket.SOL_SOCKET, socket.SO_REUSEADDR, 1
    )  # release the port immediately

    s.bind((host, port))
    s.listen()
    print("server is listening on port", port)

    while True:
        try:
            conn, address = s.accept()
            print(address[0], "connected")
            t = threading.Thread(target=handle_client, args=(conn,))
            t.start()
            thread_queue.put(t)
        except KeyboardInterrupt:
            break