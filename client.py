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
    data = utils.receive_message(client)
    print(data)
    match data.type:
        case utils.MessageType.FIRST:  # first client connects, do nothing
            pass
        case (
            utils.MessageType.NOT_FIRST
        ):  # non-first clients connect, receive folder dict from source client
            utils.write_folder(folder_path, data.body)
            print("folder received")
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
            dir_content = os.listdir(folder_path)
            # if a file is deleted
            if len(dir_content) < num_of_files:
                for file_name in list(mtime_dict.keys()):
                    if file_name not in dir_content:
                        utils.send_message(
                            client,
                            utils.Message(
                                type=utils.MessageType.DELETE, body=file_name
                            ),
                        )
                        print("Deleted file sent")
                        del mtime_dict[file_name]

            else:
                for file_name in dir_content:
                    # check if new file has been created:
                    file_path = os.path.join(folder_path, file_name)
                    if (
                        file_name not in mtime_dict
                        or os.path.getmtime(file_path) > mtime_dict[file_name]
                    ):
                        update_msg = utils.Message(
                            type=utils.MessageType.UPDATE,
                            body={
                                "file_name": file_name,
                                "file_content": utils.read_file(file_path),
                            },
                        )
                        utils.send_message(client, update_msg)
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
        if data is None:
            time.sleep(5)
            continue

        if data.type == utils.MessageType.GET:
            utils.send_folder(folder_path, client)
            print("folder sent successfully")
        elif data.type == utils.MessageType.UPDATE:
            file_name = data.body["file_name"]
            file_content = data.body["file_content"]
            file_path = os.path.join(folder_path, file_name)
            print(f"file content is {file_content}")
            utils.write_file(file_content, file_path)
            mtime_dict[file_name] = os.path.getmtime(file_path)
            print(f"{file_name} updated")
        elif data.type == utils.MessageType.DELETE:
            os.remove(os.path.join(folder_path, data.body))
            del mtime_dict[file_name]
            print("file deleted")

        des_files_dict = utils.set_dict(folder_path)

        time.sleep(5)
