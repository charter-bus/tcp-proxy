import sys
import socket
import threading

# Define a hex filter that contains ASCII printable characters.
# This hex filter uses chr() and the integer value of the character to determine if the character is printable.
# If the character is printable, it is returned. Otherwise, a period is returned.
# Sometimes, when you print a character, it will be represented as a hexadecimal value, and for example, may return '6' for the length of the character,
# such as in the case of "Ctr-D" (Control-D). This is why we check the length of the character to determine if it is printable.

# We check all 256 characters and build a string of printable characters.
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
    )


def hexdump(src, length=16, show=True):
    # Check is src is a byte string. If it is, decode it.
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    # The term "word" designates 2 bytes, or 16 bits, hence the variable name "word".
    # For each 16 characters in the string...
    for i in range(0, len(src), length):
        word = str(src[i:i+length])
        printable = word.translate(HEX_FILTER)
        hexa = ''.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results

# Add received data into a new buffer.
# We set a timeout of 5 seconds, however, if your connection is to a remote host, and there is excessive (frankly, intolerable) levels of latency, adjust this timeout.
def receive_from(connection):
    buffer = b""
    connection.settimeout(5)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except Exception as e:
        pass
    return buffer

# Request Handler Function

def request_handler(buffer):
    # perform packet modifications
    return buffer

# Response Handler Function

def response_handler(buffer):
    # perform packet modifications
    return buffer

# Proxy Handler Function

# Pass in remote host and remote port to form a new socket later in the code
def proxy_handler(client_socket, remote_host, remote_port, receive_first):

    # Create a new socket object
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the remote host with the newly created socket
    remote_socket.connect(remote_host, remote_port)

    # Some servers will receive first, so, we implemented logic here to handle that, before we begin sending any data.
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

    # Run the remote_buffer data through any potential packet modification before saving it to a variable.
    # In this current implementation, no packet modification functionality has been added.
    # Receive data and save it to a variable called "remote_buffer" to represent the data received from a remote source.
    remote_buffer = response_handler(remote_buffer)
    if len(remote_buffer):
        print("[<==] Sending %d bytes to localhost." % len(remote_buffer))
        client_socket.send(remote_buffer)
    
    # Save any data to a local buffer, from the client socket object, which, we passed in to the proxy_handler function. 
    # Loop the following flow until both sockets are closed.

    # Below is the repeating path that data takes:
    # Client Socket --> Local Buffer --> Process w/ Request Handler --> Remote Socket --> Remote Buffer --> Process w/ Response Handler --> Client Socket
    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            line = "[==>] Received %d bytes from localhost." & len(local_buffer)
            print(line)
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("[<==] Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
        
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Sent to localhost.")

        if not len(local_buffer) or len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def server_loop(local_host, local_port,
                remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problem on bind: %r' % e)

        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)

    print("[*] Listening on %s:%d" % (local_host, local_port))
    server.listen(5)
    while True:
        client_socket, addr = server.accept()

        # Print local connection information to the console
        line = "> Received incoming connection from %s:%d" % (addr[0], addr[1])
        print(line)

        # Initiate a thread to talk to the remote host
        proxy_thread = threading.Thread(

            # Define the callback function for the thread. The proxy_handler function contains all logic for sending/receiving/saving data during the conversation.
            target=proxy_handler,

            # Specify any arguments that need to be passed to the callback function
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport]", end='')
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

    if __name__ == '__main__':
        main()