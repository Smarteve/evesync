import os
import socket
import sys
import time
import threading


import utils

host = "localhost"
port = 10000

LOCKS = {}


def init_client(host: str, port: int, folder_path: str) -> socket.socket:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    data = client.recv(1024).decode().strip()
    print(data)
    match data:
        case "FIRST":  # first client connects, do nothing
            pass

        case (
            "NOT_FIRST"
        ):  # non-first clients connect, receive folder dict from source client

            source_files_dict = utils.receive_folder(client)
            utils.write_folder(folder_path, source_files_dict)
            client.send(f"files received and saved in folder\n".encode())
        case _:
            raise ValueError("unexpected response from server")
    return client


def monitor_folder(
    folder_path: str, client: socket.socket, mtime_dict: dict, num_of_files: int
):
    # handle create new files, update files, delete files and send such updates to server
    # have another dictionary to keep track of the last modified time of each file
    with LOCKS[client]:
        while True:
            # if a file is deleted
            if len(os.listdir(folder_path)) < num_of_files:
                for file_name in list(mtime_dict.keys()):
                    if file_name not in os.listdir(folder_path):
                        client.send(b"DELETE")
                        message = client.recv(1024).decode().strip()
                        if message == "ACK":
                            client.send(file_name.encode())
                            print("Deleted file sent")
                            del mtime_dict[file_name]

            else:
                for file_name in os.listdir(folder_path):
                    # check if new file has been created:
                    file_path = os.path.join(folder_path, file_name)
                    if (
                        file_name not in mtime_dict
                        or os.path.getmtime(file_path) > mtime_dict[file_name]
                    ):
                        client.send(b"UPDATE")
                        message = client.recv(1024).decode().strip()
                        if message == "ACK":
                            file_content = utils.read_file(file_path)
                            utils.send_file(file_name, file_content, client)
                            print(f"update file{file_name} sent")
                            mtime_dict[file_name] = os.path.getmtime(file_path)
            num_of_files = len(mtime_dict)
            time.sleep(3)


if __name__ == "__main__":
    # validate command line arguments (always do as earliest as possible to avoid unnecessary work)
    if len(sys.argv) < 2:
        raise ValueError("please provide a folder path")
    folder_path = sys.argv[1]
    des_file_dict = utils.set_dict(folder_path)
    client = init_client(host, port, folder_path)
    mtime_dict = {
        file: os.path.getmtime(os.path.join(folder_path, file))
        for file in os.listdir(folder_path)
    }

    num_of_files = len(mtime_dict)

    while True:
        # non blocking call to check if there is data to be read.
        # This is done so we can use the thread time to check for file updates.
        t = threading.Thread(
            target=monitor_folder, args=(folder_path, client, mtime_dict, num_of_files)
        )
        LOCKS[client] = threading.Lock()
        t.start()

        data = utils.try_receive(client)

        if data == "GET FOLDER":
            utils.send_folder(folder_path, client)
            print("folder sent successfully")
        elif data == "SET":
            ack = client.send(b"ACK\n")
            src_file_dict = utils.receive_file(client)
            file_name = src_file_dict["file_name"]
            file_path = os.path.join(folder_path, file_name)
            file_content = src_file_dict["file_content"]
            print(f"file content is {file_content}")
            utils.write_file(file_content, file_path)
            mtime_dict[file_name] = os.path.getmtime(file_path)
            print(f"{file_name}updated")
        elif data == "DELETE":
            ack = client.send(b"ACK\n")
            file_name = client.recv(1024).decode().strip()
            os.remove(os.path.join(folder_path, file_name))
            del mtime_dict[file_name]
            print("file deleted")

        num_of_files = len(mtime_dict)
        des_files_dict = utils.set_dict(folder_path)

        # file update check
        # if (
        #     data != "SET"
        # ):  # when noone changes the file, client didnt recv anything from the server, try_receive gets none, it will come to this block and continously to check if there the file has been modified
        #     current_modified_time = os.path.getmtime(filename)
        #     if current_modified_time > last_modified_time:
        #         client.send(b"UPDATE")
        #         print("file updated")
        # else:
        #     last_modified_time = os.path.getmtime(filename)

        time.sleep(5)
