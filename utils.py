import enum
import socket
import os
import pickle
from typing import Any

from dataclasses import dataclass


class MessageType(enum.Enum):
    UPDATE = "UPDATE"
    NOT_FIRST = "NOT_FIRST"
    FIRST = "FIRST"
    DELETE = "DELETE"
    GET = "GET"


@dataclass
class Message:
    type: str
    body: Any = None


def request(conn: socket.socket, message: Message | str) -> Message:
    send_message(conn, message)
    return receive_message(conn)


def receive_message(conn: socket.socket) -> Message:
    data = conn.recv(1024)
    return pickle.loads(data)


def send_message(conn: socket.socket, message: Message):
    data = pickle.dumps(message)
    conn.send(data)


def try_receive(conn: socket.socket) -> str | None:
    """Try to receive data from a socket. If there is nothing available, return None."""
    conn.setblocking(False)
    try:
        return receive_message(conn)
    except BlockingIOError:
        return None
    finally:
        conn.setblocking(True)


def set_dict(folder_path: str) -> dict:
    files_dict = {}
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "r") as f:
            file_content = f.read()
            files_dict[file_name] = file_content
    return files_dict


# send all files in the folder to server:
def send_folder(folder_path: str, conn: socket.socket):
    # set up a dictionary of key file name, value file content
    # sending the dictionary to server via pickle
    files_dict = set_dict(folder_path)
    send_message(conn, files_dict)


def receive_folder(conn: socket.socket):
    print("receving folder....")
    data = conn.recv(1024)
    files_dict = pickle.loads(data)
    return files_dict


def write_folder(folder_path: str, files_dict: dict):
    for file_name, file_content in files_dict.items():
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w") as f:
            f.write(file_content)

    print("folder synced")


def send_file(file_name: str, file_content: bytes, client: socket.socket):
    file_d = {}
    file_d["file_name"] = file_name
    file_d["file_content"] = file_content
    data = pickle.dumps(file_d)
    client.send(data)


def receive_file(conn: socket.socket) -> dict:
    print("receiving file")
    data = conn.recv(1024)
    file_d = pickle.loads(data)
    return file_d


def write_file(file_content: bytes, file_path: str):
    with open(file_path, "wb") as f:
        f.write(file_content)


def read_file(filename: str) -> bytes:
    with open(filename, "rb") as f:
        return f.read()
