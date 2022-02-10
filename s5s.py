import traceback
import ipaddress
import socket
import struct
import select
import sys

HOST = '0.0.0.0'
SERVER_PORT = 8080
VER = b'\x05' # SOCKS version
NAUTH = b'\x01' # Number of authentication methods supported
CAUTH = b'\x00' # chosen authentication method: 0x00: No authentication - 0x02: Username/password
STATUS_SUCCESS = b'\x00'
STATUS_FAIL = b'\xff'

def create_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print("Socket created")
        return sock
    except socket.error as err:
        print("Failed to create socket", err)
        sys.exit(0)

def binding(sock):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, SERVER_PORT))
        print(f"IP & Port assigned")
        return sock
    except socket.error as err:
        print("Can not assigns an IP address and a port number to the socket", err)
        sock.close()
        sys.exit(0)

def listening(sock):
    try:
        sock.listen(10)
        print(f"Listening {HOST}:{SERVER_PORT}")
        return sock
    except socket.error as err:
        print(f"Can't listen to {HOST}:{SERVER_PORT} -", err)
        sock.close()
        sys.exit(0)

def accept(sock):
    try:
        sock_handle, remote_address = sock.accept()
        sock_handle.setblocking(1)
        print(f"Connected with {remote_address[0]}:{remote_address[1]}")
        return sock_handle, None
    except socket.timeout:
        None, 'socket.timeout'
    except socket.error:
        traceback.print_exc()
        None, 'socket.error'
    except TypeError:
        return None, 'TypeError'

def greeting(sock_handle):
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
    server_choice = VER + CAUTH
    try:
        sock_handle.sendall(server_choice)
        print(f"Server sent: \t{server_choice}")
    except socket.error:
        traceback.print_exc()
        return False

    print(f">Greeting complete")
    return sock_handle


def main():

    sock = create_socket()
    sock = binding(sock)
    sock = listening(sock)
    sock_handle , error = accept(sock)
    if error != None:
        traceback.print_exc()
        sys.exit(0)
    
    sock_handle = greeting(sock_handle)

    while True:

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
        print(f"client_authentication_request:>{client_authentication_request}<")
        if client_authentication_request[0] == b'\x02':
            ID_RANGE_END = 2 + client_authentication_request[1]         # VER + IDLEN = 2
            ID = client_authentication_request[2:ID_RANGE_END].decode()
            PW_RANGE_START = 2 + client_authentication_request[1] + 1   # VER + IDLEN = 2 & PWLEN = 1
            PW = client_authentication_request[PW_RANGE_START:].decode()

            if ID == 'username' and PW == '123456':
                SERVER_AUTHENTICATION_RESPONSE = CAUTH + STATUS_SUCCESS
                print(f">Good username/password")
            else:
                SERVER_AUTHENTICATION_RESPONSE = CAUTH + STATUS_FAIL
                print(f">Bad username/password")
            try:
                sock_handle.sendall(SERVER_AUTHENTICATION_RESPONSE)
                print(f"Server sent: \t{SERVER_AUTHENTICATION_RESPONSE}")
            except socket.error:
                traceback.print_exc()
                return False
        else:
            SERVER_AUTHENTICATION_RESPONSE = CAUTH + STATUS_SUCCESS
            sock_handle.sendall(SERVER_AUTHENTICATION_RESPONSE)
            print(f"Server sent: \t{SERVER_AUTHENTICATION_RESPONSE}")

        print(f">Client authentication complete")

        """
        Connection
        """

        try:
            client_connection_request = sock_handle.recv(1024)
            print(f"client_connection_request")
        except socket.error:
            print(f"socket.error")
            traceback.print_exc()
            sys.exit(0)

        print(f"Server got: \t{client_connection_request}")

        SIZE_DOMAIN = client_connection_request[4]
        IP =  socket.inet_ntoa(client_connection_request[4:-2]) # ipv4
        # IP = client_connection_request[4:-2] # ipv6
        PACKED_PORT = client_connection_request[-2:]
        # print(f"IP: {IP} (4)")
        PORT = struct.unpack('>H', PACKED_PORT)[0]
        CLEAR_IP = ipaddress.ip_address(IP)
        print(f">IP: {CLEAR_IP} ({len(IP)}) PORT:{PORT}")

        try:
            remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_sock.settimeout(5)
        except socket.error as err:
            print("Failed to create socket", err)
            sys.exit(0)

        try:
            remote_sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_BINDTODEVICE,
                "".encode(),
            )
        except PermissionError as err:
            print("PermissionError to set OUTGOING_INTERFACE")
            sys.exit(0)

        try:
            remote_sock.connect((IP, PORT))
        except socket.error as err:
            print("Failed to connect to destination", err)

        BNDADDR = socket.inet_aton(remote_sock.getsockname()[0])
        BNDPORT = struct.pack(">H", remote_sock.getsockname()[1])
        REP = b'\x00'
        RSV = b'\x00'
        TYPE = b'\x01' # 0x01: IPv4 address - 0x04: IPv6 address
        RESPONSE_PACKET_FROM_SERVER = VER + REP + RSV + TYPE + BNDADDR + BNDPORT
        sock_handle.sendall(RESPONSE_PACKET_FROM_SERVER)

        try:
            sock_handle.sendall(RESPONSE_PACKET_FROM_SERVER)
            print(">Connected to destination")
        except socket.error:
            if sock_handle != 0:
                print("Failed to connect to destination", socket.error)
                sock_handle.close()

       # start proxy

       
        while True:
            try:
                reader, _, _ = select.select([sock_handle, remote_sock], [], [], 1)
            except select.error as err:
                print("Select failed", err)
                sys.exit(0)
            if not reader:
                continue
            try:
                for sock in reader:
                    data = sock.recv(1024)
                    if not data:
                        pass
                        # print("No data")
                        # sys.exit(0)
                    if sock is remote_sock:
                        print(">>>")
                        sock_handle.send(data)
                    else:
                        print("<<<")
                        remote_sock.send(data)
            except socket.error as err:
                print("Loop failed", err)
                sys.exit(0)

    sock.close()
    
if __name__ == '__main__':
    main()
