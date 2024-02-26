 app to synce folders between different users in different machines 

client passing folder path via command line arguments 
example python3 client.py (folder path)

Client initialization (after connecting to the server)
1 if first client:
    do nothing 
2 if not first client:
    server sends a get message to any random client before the new client. random client send the folder content via pickle. server send the folder content to new client. 


monitor changes in the folder
1 create new file:
    send new file name, new file content to server, broadcast to other clients 
2 update file:
    checking modified time, send updated file content
3 delete file:
    send file name to other clients, delete file 
 

Server

Connection initialization
    It is the First client:
        Don’t do anything
    Else:
        GET to any of the client
        Send the content to the new client
        Add the new client to the client list
Broadcast Update
