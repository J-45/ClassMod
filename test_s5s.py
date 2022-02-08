from truth.truth import AssertThat
import struct
import socket

HOST = '127.0.0.1'
PORT = 8080
VER = b'\x05' # SOCKS version (0x05)
NAUTH = b'\x01' # Number of authentication methods supported, uint8
AUTH = b'\x02' # Authentication method = Username/password
STATUS_SUCCESS = b'\x00' # 0x00 success, otherwise failure, connection must be closed
CMD = b'\x01' # Zstablish a TCP/IP stream connection
RSV = b'\x00'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_handle:
    socket_handle.connect((HOST, PORT))
    CLIENT_GREETING = VER + NAUTH + AUTH
    print(f"Client sent:\t{CLIENT_GREETING}")
    socket_handle.sendall(CLIENT_GREETING)
    server_response = socket_handle.recv(1024)
    print(f"Client got:\t{server_response}")
    AssertThat(server_response).IsEqualTo(VER + AUTH)

    ID = 'username'.encode()
    IDLEN = struct.pack('B', len(ID))
    PW = '123456'.encode()
    PWLEN = struct.pack('B', len(PW))
    
    CLIENT_AUTHENTICATION_REQUEST = AUTH + IDLEN + ID + PWLEN + PW
    print(f"Client sent:\t{CLIENT_AUTHENTICATION_REQUEST}")
    socket_handle.sendall(CLIENT_AUTHENTICATION_REQUEST)
    server_response = socket_handle.recv(1024)
    print(f"Client got:\t{server_response}")
    AssertThat(server_response).IsEqualTo(AUTH + STATUS_SUCCESS)

    TYPE = b'\x03' # Domain name
    DOMAIN = 'j45.eu'.encode()
    DSTADDR = TYPE + struct.pack('B', len(DOMAIN)) + DOMAIN
    DSTPORT = struct.pack(">H", 80)
    CLIENT_CONNECTION_REQUEST = VER + CMD + RSV + DSTADDR + DSTPORT
    print(f"Client sent:\t{CLIENT_CONNECTION_REQUEST}")
    socket_handle.sendall(CLIENT_CONNECTION_REQUEST)
    server_response = socket_handle.recv(1024)
    print(f"Client got:\t{server_response}")
    AssertThat(server_response).IsEqualTo(AUTH + STATUS_SUCCESS)

# AND

# curl -x "socks5://username:123456@127.0.0.1:8080" "https://j45.eu/ip"