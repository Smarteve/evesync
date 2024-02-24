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
                b"GET\n"
            )  # get the file from a random client before this newly joined client
            file_content = utils.receive_file(random_client)
        utils.send_file(file_content, client)
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
            if message == "UPDATE":
                client.send(b"GET\n")
                file_content = utils.receive_file(client)
                broadcast_update(file_content, client)
        time.sleep(5)


def broadcast_update(file_content, conn):
    print("Broadcasting update")
    for client in CLIENTS:
        if client != conn:
            with LOCKS[client]:
                client.send(b"SET\n")
                message = client.recv(1024).decode().strip()
                if message == "ACK":
                    utils.send_file(file_content, client)


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
