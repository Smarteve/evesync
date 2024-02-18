import socket
import os


def try_receive(conn: socket.socket) -> str | None:
    """Try to receive data from a socket. If there is nothing available, return None."""
    conn.setblocking(False)
    try:
        return conn.recv(1024).decode().strip()
    except BlockingIOError:
        return None
    finally:
        conn.setblocking(True)


def send_file(file_content: bytes, client: socket.socket):
    file_size = len(file_content)
    print(file_size)
    client.send(file_size.to_bytes(4, "big"))
    client.send(file_content)


def receive_file(conn: socket.socket) -> bytes:
    print("receiving file")
    file_size = int.from_bytes(conn.recv(4), "big")
    print(file_size)
    content = conn.recv(file_size)
    print(content)
    return content


def write_file(file_content: bytes, filename: str):
    with open(filename, "wb") as f:
        f.write(file_content)


def read_file(filename: str) -> bytes:
    with open(filename, "rb") as f:
        return f.read()
