import os
import socket
import sys


host = "localhost"
port = 10000

# support multiple clients by passing path of the file as command line arguments
# first client will send the file to the server
# server sync the file to other clients
# if any client made the change, server will sync the change to other clients


def create_file(filename):
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write(
                "test"
            )  # do i have to write something as a placeholder in creating a new file
            print("file created")


def send_file(filename, client):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            file_size = os.path.getsize(filename)
            client.send(file_size.to_bytes(4, "big"))
            chunk = f.read(1024)
            while chunk:
                client.send(chunk)
                chunk = f.read(1024)

    else:
        print("file not found")


def change_file(filename):
    with open(filename, "w") as f:
        f.write("change")


# how can i change file, should user pass in command line arguement ?


if __name__ == "__main__":
    # first client send the file to the server, assume first client always provide a file
    # rest client receive the file from the server

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    data = client.recv(1024).decode().strip()
    print(data)
    if data == "GET":
        if len(sys.argv) < 2:
            raise ValueError("please provide a file path")
        filename = sys.argv[1]
        create_file(filename)
        send_file(filename, client)
        print("file sent successfully")
    else:
        client.send(b"file received\n")

        with open(
            "/home/evelyn/Desktop/engineer/miniproject/evesync/received_file.txt", "w"
        ) as f:
            f.write(data)
        client.send(b"file saved as received_file.txt\n")
