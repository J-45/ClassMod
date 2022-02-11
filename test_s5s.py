from truth.truth import AssertThat
import struct
import socket

HOST = '127.0.0.1'
PORT = 8080

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_handle:
    socket_handle.connect((HOST, PORT))
    VER = struct.pack('B', 5) # SOCKS version (0x05) >>> b'\x05'
    NAUTH = struct.pack('B', 2) # Number of authentication methods supported, uint8
    AUTH = struct.pack('B', 2) # Authentication method = Username/password
    CLIENT_GREETING = VER + NAUTH + struct.pack('B', 0) + struct.pack('B', 2)

    print(f"Client sent:\t{CLIENT_GREETING}")
    socket_handle.sendall(CLIENT_GREETING)
    server_response = socket_handle.recv(4096)
    print(f"Client got:\t{server_response}")
    AssertThat(server_response).IsEqualTo(VER + AUTH)

    AUTH = struct.pack('B', 2)
    ID = 'username'.encode()
    IDLEN = struct.pack('B', len(ID))
    PW = '123456'.encode()
    PWLEN = struct.pack('B', len(PW))
    
    CLIENT_AUTHENTICATION_REQUEST = AUTH + IDLEN + ID + PWLEN + PW
    # AUTH = b'\x00'
    # CLIENT_AUTHENTICATION_REQUEST = AUTH
    print(f"Client sent:\t{CLIENT_AUTHENTICATION_REQUEST}")
    socket_handle.sendall(CLIENT_AUTHENTICATION_REQUEST)
    server_response = socket_handle.recv(4096)
    print(f"Client got:\t{server_response}")
    STATUS_SUCCESS = b'\x00' # 0x00 success, otherwise failure, connection must be closed
    AssertThat(server_response).IsEqualTo(AUTH + STATUS_SUCCESS)

    CMD = struct.pack('B', 1) # Zstablish a TCP/IP stream connection
    RSV = struct.pack('B', 0) # reserved, must be 0x00
    TYPE = struct.pack('B', 1) # Domain name
    DOMAIN = 'j45.eu'
    IPV4 = socket.gethostbyname(DOMAIN)
    print(f"IPV4:\t{IPV4}")
    IPV4_BYTES = socket.inet_aton(IPV4)
    DSTADDR = TYPE + IPV4_BYTES
    DSTPORT = struct.pack(">H", 80)

    CLIENT_CONNECTION_REQUEST = VER + CMD + RSV + DSTADDR + DSTPORT
    print(f"Client sent:\t{CLIENT_CONNECTION_REQUEST}")
    socket_handle.sendall(CLIENT_CONNECTION_REQUEST)
    server_response = socket_handle.recv(4096)
    print(f"Client got:\t{server_response}")


    print(f"Client sent:\tGET / HTTP/1.0\r\nHost: j45.eu\r\n\r\n")
    # send some data 
    socket_handle.send(b'GET / HTTP/1.0\r\nHost: j45.eu\r\n\r\n')
    server_response = socket_handle.recv(4096)
    print(f"Client got:\t{server_response.decode()}")
    socket_handle.close()

# AND

# curl -x "socks5://username:123456@127.0.0.1:8080" "https://j45.eu/ip"
