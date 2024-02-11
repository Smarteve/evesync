import socket
import threading
from queue import Queue

from client import send_file

host = "localhost"
port = 9999

# requirement: multiple clients, but each client has one file and they are syncing the file
# first client will send the file to the server
# server sync the file to other clients


client_list = []


def receive_file(client):
    filename_length = int.from_bytes(client.recv(4), "big")
    filename = client.recv(filename_length).decode()
    content = b""

    while True:
        data = client.recv(1024)
        if not data:
            break
        content += data

    with open(filename, "wb") as f:
        f.write(content)

    return filename


def broadcast_file(filename):
    for client in client_list:
        if client != conn:
            send_file(filename, client)


thread_queue = Queue()
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen()
    print("server is listening on port", port)

    while True:
        try:
            conn, address = s.accept()
            print(address[0], "connected")
            client_list.append(conn)
            if len(client_list) == 1:
                conn.send(b"GET")
                filename = receive_file(conn)
                broadcast_file(filename)

            t = threading.Thread(target=receive_file, args=(conn,))
            t.start()
            thread_queue.put(t)
        except KeyboardInterrupt:
            pass
        finally:
            while not thread_queue.empty():
                thread_queue.get().join()
