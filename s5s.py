import traceback
import socket
import sys

HOST = '0.0.0.0'
PORT = 8080

VER = b'\x05' # SOCKS version
NAUTH = b'\x01' # Number of authentication methods supported
CAUTH = b'\x02' # chosen authentication method
STATUS_SUCCESS = b'\x00'
STATUS_FAIL = b'\xff'
def main():

    """
    Socket creation
    """

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print("Socket created")
    except socket.error as err:
        print("Failed to create socket", err)
        sys.exit(0)

    """
    Binding
    """

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        print(f"IP & Port assigned")
    except socket.error as err:
        print("Can not assigns an IP address and a port number to the socket", err)
        sock.close()
        sys.exit(0)

    """
    Listening
    """

    try:
        sock.listen(10)
        print(f"Listening {HOST}:{PORT}")
    except socket.error as err:
        print(f"Can't listen to {HOST}:{PORT} -", err)
        sock.close()
        sys.exit(0)
    
    while True:

        """
        Accept connection
        """

        try:
            sock_handle, remote_address = sock.accept()
            sock_handle.setblocking(1)
            print(f"Connected with {remote_address[0]}:{remote_address[1]}")
        except socket.timeout:
            continue
        except socket.error:
            traceback.print_exc()
            continue
        except TypeError:
            traceback.print_exc()
            sys.exit(0)

        """
        Greeting
        """
        
        try:
            client_greeting = sock_handle.recv(1024)
        except socket.error:
            traceback.print_exc()
            sys.exit(0)

        if VER != client_greeting[0:1]:
            print("Wrong sock version of client")

        client_nauth = client_greeting[1]
        client_auth_list = client_greeting[2:]

        if len(client_auth_list) != client_nauth:
            print("Bad client greeting: wrong number of methods")
            print(client_greeting)
        supported_method_found = False
        for client_auth_method in client_auth_list:
            if client_auth_method == ord(CAUTH):
                supported_method_found = True
        if not supported_method_found:
            print("No authentication method provided is supported")
            sys.exit(0)
        
        print(">Good authentication method found")
        print(f"Server got: \t{client_greeting}")

        """
        Server answer to greeting
        """

        server_choice = VER + CAUTH
        try:
            sock_handle.sendall(server_choice)
            print(f"Server sent: \t{server_choice}")
        except socket.error:
            traceback.print_exc()
            return False

        print(f">Greeting complete")
        
        """
        Client Authentication
        """

        try:
            client_authentication_request = sock_handle.recv(1024)
        except socket.error:
            traceback.print_exc()
            sys.exit(0)

        print(f"Server got: \t{client_authentication_request}")

        """
        Server answer to client Authentication
        """

        ID_RANGE_END = 2 + client_authentication_request[1]         # VER + IDLEN = 2
        ID = client_authentication_request[2:ID_RANGE_END].decode()
        PW_RANGE_START = 2 + client_authentication_request[1] + 1   # VER + IDLEN = 2 & PWLEN = 1
        PW = client_authentication_request[PW_RANGE_START:].decode()

        if ID == 'username' and PW == '123456':
            server_authentication_response = CAUTH + STATUS_SUCCESS
            print(f">Good username/password")
        else:
            server_authentication_response = CAUTH + STATUS_FAIL
            print(f">Bad username/password")
        try:
            sock_handle.sendall(server_authentication_response)
            print(f"Server sent: \t{server_authentication_response}")
        except socket.error:
            traceback.print_exc()
            return False

        print(f">Client authentication complete")

        """
        Connection
        """

        # def request(wrapper):


    sock.close()
    
if __name__ == '__main__':
    main()