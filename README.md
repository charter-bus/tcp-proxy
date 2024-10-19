# tcp-proxy
A simple TCP Proxy in Python

To test this program, you will need a live FTP server that is listening for connections.

Executing the program looks like so:
`sudo python proxy.py <local_host> <local_port> <remote_host> <remote_port> <receive_first>`

_Argument 1:_ Specify the local host IP address
_Argument 2:_ Specify the local host port *(FTP runs on port 21.)*
_Argument 3:_ Specify the remote host IP address, which, would be the IP address of your FTP server.
_Argument 4:_ Specify the remote host port *(FTP runs on port 21.)*
_Argument 5:_ Specify a boolean "True" or "False" (You may also simply not include this argument, and it will default to False.)
    The receive_first argument specifies whether or not to receive data before sending any. In many cases, an FTP server will respond with a banner, or some other data.
    In the case that the FTP server does this, specify `True` as the final command argument when executing the script.
