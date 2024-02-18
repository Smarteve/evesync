 
Client initialization (after connecting to the server)
File exists
 If it is the first client: all good!
 else:
 Throw an error
File doesn’t exist
 if it is the first client:
   Throw an error!
else
    Create a new file with the content from server.

Client updates
File changes
Send an update to the server

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
