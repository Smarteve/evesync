import os
import socket
import sys


host = "localhost"
port = 9999

"""
requirement
create a file
send the file to server 
server sync the file to another client 

"""
# support multiple clients by passing path of the file as command line arguments
# first client will send the file to the server


def create_file(filename):
    if not os.path.exists(
        filename
    ):  # if not provided a path, by default check if the file exists in the current directory
        with open(filename, "w") as f:
            f.write(
                ""
            )  # do i have to write something as a placeholder in creating a new file
            print("file created")


def send_file(filename, client):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            content = f.read(1024)
        filename_length = len(filename).to_bytes(
            4, "big"
        )  # one character is one byte,using len to get the length of the filename
        client.send(filename_length)
        client.send(filename.encode())
        client.send(content)
    else:
        print("file not found")


if __name__ == "__main__":

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    n = len(sys.argv)

    if n > 1:
        filename = sys.argv[1]
    else:
        raise ValueError("please provide a file path")

    create_file(filename)

    client.connect((host, port))
    data = client.recv(1024).decode().strip()
    print(data)
    if data == "GET":
        send_file(filename, client)
        print("file sent successfully")

    # when send multiple data, how would server know which data is for which
    # define protocal
