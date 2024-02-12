import socket
import threading
from queue import Queue

host = "localhost"
port = 10000

# requirement: multiple clients, but each client has one file and they are syncing the file
# first client will send the file to the server
# server sync the file to other clients


client_list = []
file_content = None


def handle_client(client):
    global file_content
    content = b""
    if len(client_list) == 1:
        conn.send(b"GET\n")
        file_size = int.from_bytes(client.recv(4), "big")

        while True:
            data = client.recv(1024)
            if not data:
                break
            content += data
        print(file_size)
        print(len(content))

        if len(content) != file_size:
            raise ValueError("file not completely received")
        file_content = content
    else:
        if file_content is not None:
            client.send(file_content)


def broadcast_update(file_content, conn):
    for client in client_list:
        if client != conn:
            client.send(file_content)


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
            client_list.append(conn)
            t = threading.Thread(target=handle_client, args=(conn,))
            t.start()
            thread_queue.put(t)
        except KeyboardInterrupt:
            pass
        finally:
            while not thread_queue.empty():
                thread_queue.get().join()
