import socket
import threading
import random
import time

import utils

# TODO: use command line arguments --host and --port
host = "0.0.0.0"
port = 10000


CLIENTS = []
LOCKS = {}


def init_client(client):
    if not CLIENTS:
        client.send(b"FIRST\n")
    else:
        client.send(b"NOT_FIRST\n")
        random_client = random.choice(CLIENTS)
        with LOCKS[random_client]:
            random_client.send(
                b"GET FOLDER\n"
            )  # get the file dict binary content from a random client before this newly joined client
            folder_content = random_client.recv(1024)

        client.send(folder_content)
        ack = client.recv(1024).decode().strip()
        print(ack)
    CLIENTS.append(client)


def handle_client(client):
    with LOCKS[
        client
    ]:  # ensure a connection is only used by a single thread at a given time
        init_client(client)

    while True:  # have a while loop to keep the connection open
        with LOCKS[client]:
            message = utils.try_receive(client)
            match message:
                case "UPDATE":
                    client.send(b"ACK\n")
                    binary_dict = client.recv(1024)
                    print(binary_dict)
                    broadcast_update(binary_dict, client)
                case "DELETE":
                    client.send(b"ACK\n")
                    file_name = client.recv(1024).decode().strip()
                    broadcast_delete(file_name, client)

        time.sleep(5)


def broadcast_delete(file_name, conn):
    print("Broadcasting delete")
    for client in CLIENTS:
        if client != conn:
            with LOCKS[client]:
                client.send(b"DELETE\n")
                message = client.recv(1024).decode().strip()
                if message == "ACK":
                    client.send(file_name.encode())
                    print("Deleted file sent to client")


def broadcast_update(binary_dict, conn):
    print("Broadcasting update")
    for client in CLIENTS:
        if client != conn:
            print(client)
            with LOCKS[client]:
                print("acquired lock")
                client.send(b"SET\n")
                message = client.recv(1024).decode().strip()
                if message == "ACK":
                    client.send(binary_dict)


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
            LOCKS[conn] = threading.Lock()
            print(f"Starting thread {t.name}")
            t.start()
        except KeyboardInterrupt:
            break
