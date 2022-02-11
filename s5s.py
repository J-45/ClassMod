"""
 Small Socks5 Proxy Server in Python
 from https://github.com/MisterDaneel/
"""

# Network
import socket
import select
from struct import pack, unpack
# System
import traceback
from threading import Thread, activeCount
from signal import signal, SIGINT, SIGTERM
from time import sleep
import sys
import struct

#
# Configuration
#
MAX_THREADS = 200
BUFSIZE = 2048
TIMEOUT_SOCKET = 5
LOCAL_ADDR = '0.0.0.0'
LOCAL_PORT = 8080
# Parameter to bind a socket to a device, using SO_BINDTODEVICE
# Only root can set this option
# If the name is an empty string or None, the interface is chosen when
# a routing decision is made
# OUTGOING_INTERFACE = "eth0"
OUTGOING_INTERFACE = ""

#
# Constants
#
'''Version of the protocol'''
# PROTOCOL VERSION 5
VER = b'\x05'
'''Method constants'''
# '00' NO AUTHENTICATION REQUIRED
M_NOAUTH = b'\x00'
PWD_AUTH = struct.pack('B', 2)
# 'FF' NO ACCEPTABLE METHODS
M_NOTAVAILABLE = b'\xff'
'''Command constants'''
# CONNECT '01'
CMD_CONNECT = b'\x01'
'''Address type constants'''
# IP V4 address '01'
ATYP_IPV4 = b'\x01'
# DOMAINNAME '03'
ATYP_DOMAINNAME = b'\x03'
STATUS_SUCCESS = struct.pack('B', 0)

class ExitStatus:
    """ Manage exit status """
    def __init__(self):
        self.exit = False

    def set_status(self, status):
        """ set exist status """
        self.exit = status

    def get_status(self):
        """ get exit status """
        return self.exit


def error(msg="", err=None):
    """ Print exception stack trace python """
    if msg:
        traceback.print_exc()
        print("{} - Code: {}, Message: {}".format(msg, str(err[0]), err[1]))
    else:
        traceback.print_exc()


def proxy_loop(socket_src, socket_dst):
    """ Wait for network activity """
    while not EXIT.get_status():
        try:
            reader, _, _ = select.select([socket_src, socket_dst], [], [], 1)
        except select.error as err:
            error("Select failed", err)
            return
        if not reader:
            continue
        try:
            for sock in reader:
                data = sock.recv(BUFSIZE)
                if not data:
                    return
                if sock is socket_dst:
                    socket_src.send(data)
                else:
                    socket_dst.send(data)
        except socket.error as err:
            error("Loop failed", err)
            return


def connect_to_dst(dst_addr, dst_port):
    """ Connect to desired destination """
    sock = create_socket()
    if OUTGOING_INTERFACE:
        try:
            sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_BINDTODEVICE,
                OUTGOING_INTERFACE.encode(),
            )
        except PermissionError as err:
            print("Only root can set OUTGOING_INTERFACE parameter")
            EXIT.set_status(True)
    try:
        sock.connect((dst_addr, dst_port))
        print("connect_to_dst ok")
        return sock
    except socket.error as err:
        error("Failed to connect to DST", err)
        return 0


def request_client(wrapper):
    """ Client request details """
    # +----+-----+-------+------+----------+----------+
    # |VER | CMD |  RSV  | ATYP | DST.ADDR | DST.PORT |
    # +----+-----+-------+------+----------+----------+
    try:
        s5_request = wrapper.recv(BUFSIZE)
    except ConnectionResetError:
        if wrapper != 0:
            wrapper.close()
        error()
        return False
    # Check VER, CMD and RSV
    if (
            s5_request[0:1] != VER or
            s5_request[1:2] != CMD_CONNECT or
            s5_request[2:3] != b'\x00'
    ):
        return False
    # IPV4
    if s5_request[3:4] == ATYP_IPV4:
        dst_addr = socket.inet_ntoa(s5_request[4:-2])
        dst_port = unpack('>H', s5_request[8:len(s5_request)])[0]
    # DOMAIN NAME
    elif s5_request[3:4] == ATYP_DOMAINNAME:
        sz_domain_name = s5_request[4]
        dst_addr = s5_request[5: 5 + sz_domain_name - len(s5_request)]
        port_to_unpack = s5_request[5 + sz_domain_name:len(s5_request)]
        dst_port = unpack('>H', port_to_unpack)[0]
    else:
        return False
    print(dst_addr, dst_port)
    return (dst_addr, dst_port)


def request(wrapper):
    """
        The SOCKS request information is sent by the client as soon as it has
        established a connection to the SOCKS server, and completed the
        authentication negotiations.  The server evaluates the request, and
        returns a reply
    """
    dst = request_client(wrapper)
    # Server Reply
    # +----+-----+-------+------+----------+----------+
    # |VER | REP |  RSV  | ATYP | BND.ADDR | BND.PORT |
    # +----+-----+-------+------+----------+----------+
    rep = b'\x07'
    bnd = b'\x00' + b'\x00' + b'\x00' + b'\x00' + b'\x00' + b'\x00'
    socket_dst = 0
    if dst:
        socket_dst = connect_to_dst(dst[0], dst[1])
    if not dst or socket_dst == 0:
        rep = b'\x01'
        print(dst, socket_dst, rep)
    else:
        rep = b'\x00'
        bnd = socket.inet_aton(socket_dst.getsockname()[0])
        bnd += pack(">H", socket_dst.getsockname()[1])
    print('request', rep)
    reply = VER + rep + b'\x00' + ATYP_IPV4 + bnd
    try:
        wrapper.sendall(reply)
    except socket.error:
        if wrapper != 0:
            wrapper.close()
        return
    # start proxy
    if rep == b'\x00':
        proxy_loop(wrapper, socket_dst)
    if wrapper != 0:
        wrapper.close()
    if dst and socket_dst != 0:
        socket_dst.close()


def subnegotiation_client(wrapper):
    """
        The client connects to the server, and sends a version
        identifier/method selection message
    """
    # Client Version identifier/method selection message
    # +----+----------+----------+
    # |VER | NMETHODS | METHODS  |
    # +----+----------+----------+
    try:
        identification_packet = wrapper.recv(BUFSIZE)
    except socket.error:
        error()
        return M_NOTAVAILABLE
    # VER field
    if VER != identification_packet[0:1]:
        return M_NOTAVAILABLE
    # METHODS fields
    nmethods = identification_packet[1]
    methods = identification_packet[2:]
    print("identification_packet:", identification_packet)
    if len(methods) != nmethods:
        return M_NOTAVAILABLE
    for method in methods:
        if PWD_AUTH in methods:
            return PWD_AUTH
        if M_NOAUTH in methods:
            return M_NOAUTH

    return M_NOTAVAILABLE


def subnegotiation(wrapper):
    """
        The client connects to the server, and sends a version
        identifier/method selection message
        The server selects from one of the methods given in METHODS, and
        sends a METHOD selection message
    """
    CAUTH = subnegotiation_client(wrapper)
    # Server Method selection message
    # +----+--------+
    # |VER | METHOD |
    # +----+--------+
    if CAUTH == M_NOAUTH or CAUTH == PWD_AUTH:
        reply = VER + CAUTH
        try:
            wrapper.sendall(reply)
        except socket.error:
            error()
            return False
        
    if CAUTH == PWD_AUTH:

        try:
            client_authentication_request = wrapper.recv(4096)
        except socket.error:
            traceback.print_exc()
            sys.exit(0)

        # print(f"Server got: \t{client_authentication_request}")

        """
        Server answer to client Authentication
        """
        # print(f"client_authentication_request:>{client_authentication_request}<")
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
            wrapper.sendall(SERVER_AUTHENTICATION_RESPONSE)
            # print(f"Server sent: \t{SERVER_AUTHENTICATION_RESPONSE}")
        except socket.error:
            error()
            return False
        # print(f">Client authentication complete")

    return True


def connection(wrapper):
    """ Function run by a thread """
    if subnegotiation(wrapper):
        request(wrapper)


def create_socket():
    """ Create an INET, STREAMing socket """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT_SOCKET)
    except socket.error as err:
        error("Failed to create socket", err)
        sys.exit(0)
    return sock


def bind_port(sock):
    """
        Bind the socket to address and
        listen for connections made to the socket
    """
    try:
        print('Bind {}'.format(str(LOCAL_PORT)))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((LOCAL_ADDR, LOCAL_PORT))
    except socket.error as err:
        error("Bind failed", err)
        sock.close()
        sys.exit(0)
    # Listen
    try:
        sock.listen(10)
    except socket.error as err:
        error("Listen failed", err)
        sock.close()
        sys.exit(0)
    return sock


def exit_handler(signum, frame):
    """ Signal handler called with signal, exit script """
    print('Signal handler called with signal', signum)
    EXIT.set_status(True)


def main():
    """ Main function """
    new_socket = create_socket()
    bind_port(new_socket)
    signal(SIGINT, exit_handler)
    signal(SIGTERM, exit_handler)
    while not EXIT.get_status():
        if activeCount() > MAX_THREADS:
            sleep(3)
            continue
        try:
            wrapper, _ = new_socket.accept()
            wrapper.setblocking(1)
        except socket.timeout:
            continue
        except socket.error:
            error()
            continue
        except TypeError:
            error()
            sys.exit(0)
        recv_thread = Thread(target=connection, args=(wrapper, ))
        recv_thread.start()
    new_socket.close()


EXIT = ExitStatus()
if __name__ == '__main__':
    main()
    
    
    
    
    
    
from threading import Thread, activeCount
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
r = True

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


def greeting(sock_handle):
    try:
        client_greeting = sock_handle.recv(4096)
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


def authentication(sock_handle):
    """
    Client Authentication
    """

    try:
        client_authentication_request = sock_handle.recv(4096)
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
            sys.exit(0)
    else:
        SERVER_AUTHENTICATION_RESPONSE = CAUTH + STATUS_SUCCESS
        sock_handle.sendall(SERVER_AUTHENTICATION_RESPONSE)
        print(f"Server sent: \t{SERVER_AUTHENTICATION_RESPONSE}")

    print(f">Client authentication complete")
    return sock_handle

def connection(sock_handle):
    """
    Connection
    """

    try:
        client_connection_request = sock_handle.recv(4096)
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
    return sock_handle, remote_sock

def proxy(sock_handle):
    sock_handle = greeting(sock_handle)
    sock_handle = authentication(sock_handle)
    sock_handle, remote_sock = connection(sock_handle)

    while r:
        try:
            reader, _, _ = select.select([sock_handle, remote_sock], [], [], 1)
        except select.error as err:
            print("Select failed", err)
            sys.exit(0)
        if not reader:
            continue
        try:
            for sock in reader:
                data = sock.recv(4096)
                if not data:
                    print("---")
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

def main():

    sock = create_socket()
    sock = binding(sock)
    sock = listening(sock)

       
    while r:
        try:
            sock_handle, remote_address = sock.accept()
            sock_handle.setblocking(1)
            print(f"Connected with {remote_address[0]}:{remote_address[1]}")
            return sock_handle, None
        except socket.timeout:
            continue
        except socket.error:
            traceback.print_exc()
            continue
        except TypeError:
            traceback.print_exc()
            sys.exit(0)

        recv_thread = Thread(target=proxy, args=(sock_handle, ))
        recv_thread.start()
    sock.close()
 
    
if __name__ == '__main__':
    main()
