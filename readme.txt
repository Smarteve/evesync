 
Client initialization (after connecting to the server)
client passing folder path via command line arguments 
having a set keep track of the files in the folder 
monitor changes in the folder
    1 create new file:
        if new file not in set
        send file content to server, broadcast to other clients 
    2 update file:
        checking modified time 
    3 delete file:
        send file name to other clients, delete file 

non-first client connects:
    server send a get message to random client before him 
    random client sends all the files in the folder to that client 
    send and receive dictionary using pickle 
    key as the file name, value as file content 


Server
UPDATE (client sends the updated file content)
    Broadcast it to all the clients (except the one which sent the update)

Connection initialization
    It is the First client:
        Don’t do anything
    Else:
        GET to any of the client
        Send the content to the new client
        Add the new client to the client list
