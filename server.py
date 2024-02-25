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

MessageType = utils.MessageType


def init_client(client):
    if not CLIENTS:
        utils.send_message(client, utils.Message(type=MessageType.FIRST))
    else:
        random_client = random.choice(CLIENTS)
        with LOCKS[random_client]:
            print("Requesting folder content from", random_client)
            folder_content = utils.request(
                random_client, utils.Message(type=MessageType.GET)
            )  # get the file dict binary content from a random client before this newly joined client
            print("Received")

        utils.send_message(
            client, utils.Message(type=MessageType.NOT_FIRST, body=folder_content)
        )
    CLIENTS.append(client)


def handle_client(client):
    with LOCKS[
        client
    ]:  # ensure a connection is only used by a single thread at a given time
        init_client(client)

    while True:  # have a while loop to keep the connection open
        with LOCKS[client]:
            message = utils.try_receive(client)
        if message is None:
            time.sleep(5)
            continue
        match message.type:
            case MessageType.UPDATE | MessageType.DELETE:
                broadcast(message, client)
            case _:
                raise ValueError("Invalid operation")


def broadcast(msg, conn):
    print("Broadcasting: ", msg)
    for client in CLIENTS:
        if client != conn:
            with LOCKS[client]:
                utils.send_message(client, msg)


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
