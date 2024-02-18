import os
import socket
import sys
import time


import utils


# TODO: use command line arguments --host and --port
host = "localhost"
port = 10000

# support multiple clients by passing path of the file as command line arguments
# first client will send the file to the server
# server sync the file to other clients
# if any client made the change, server will sync the change to other clients


def init_client(host: str, port: int, filename: str) -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    data = client.recv(1024).decode().strip()
    print(data)
    match data:
        case "FIRST":  # first client connects, the file should already exist
            if not os.path.exists(filename):
                raise ValueError("file does not exist")
        case (
            "NOT_FIRST"
        ):  # non-first clients connect, the file should not exist, waiting for the server to send the file content then update the file
            if os.path.exists(filename):
                raise ValueError("file already exist")
            else:
                file_content = utils.receive_file(client)
                utils.write_file(file_content, filename)
                client.send(f"file saved as {filename}\n".encode())
        case _:
            raise ValueError("unexpected response from server")
    return client


if __name__ == "__main__":
    # validate command line arguments (always do as earliest as possible to avoid unnecessary work)
    if len(sys.argv) < 2:
        raise ValueError("please provide a file path")
    filename = sys.argv[1]

    client = init_client(host, port, filename)
    last_modified_time = os.path.getmtime(filename)
    while True:
        # non blocking call to check if there is data to be read.
        # This is done so we can use the thread time to check for file updates.
        data = utils.try_receive(client)

        if data == "GET":
            file_content = utils.read_file(filename)
            utils.send_file(file_content, client)
            print("file sent successfully")
        elif data == "SET":
            ack = client.send(b"ACK\n")
            file_content = utils.receive_file(client)
            utils.write_file(file_content, filename)
            print("file updated")

        # file update check
        if (
            data != "SET"
        ):  # when noone changes the file, client didnt recv anything from the server, try_receive gets none, it will come to this block and continously to check if there the file has been modified
            current_modified_time = os.path.getmtime(filename)
            if current_modified_time > last_modified_time:
                client.send(b"UPDATE")
                last_modified_time = current_modified_time
                print("file updated")
        else:
            last_modified_time = os.path.getmtime(filename)

        time.sleep(5)
