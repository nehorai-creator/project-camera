"""TCP client using Windows Winsock via ctypes (no Python socket module)."""

import ctypes
import json
import os

if os.name != "nt":
    raise OSError("This TCP client uses Windows Winsock and must run on Windows.")

winsock = ctypes.WinDLL("Ws2_32.dll")

SOCKET = ctypes.c_size_t
INVALID_SOCKET = ctypes.c_size_t(-1).value
SOCKET_ERROR = -1

AF_INET = 2
SOCK_STREAM = 1
IPPROTO_TCP = 6

SERVER_IP = b"127.0.0.1"
SERVER_PORT = 5000


class SockAddrIn(ctypes.Structure):
    _fields_ = [
        ("sin_family", ctypes.c_ushort),
        ("sin_port", ctypes.c_ushort),
        ("sin_addr", ctypes.c_uint32),
        ("sin_zero", ctypes.c_ubyte * 8),
    ]


winsock.WSAStartup.argtypes = [ctypes.c_ushort, ctypes.c_void_p]
winsock.WSAStartup.restype = ctypes.c_int

winsock.WSACleanup.argtypes = []
winsock.WSACleanup.restype = ctypes.c_int

winsock.socket.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
winsock.socket.restype = SOCKET

winsock.connect.argtypes = [
    SOCKET,
    ctypes.POINTER(SockAddrIn),
    ctypes.c_int,
]
winsock.connect.restype = ctypes.c_int

winsock.send.argtypes = [
    SOCKET,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
]
winsock.send.restype = ctypes.c_int

winsock.recv.argtypes = [
    SOCKET,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
]
winsock.recv.restype = ctypes.c_int

winsock.closesocket.argtypes = [SOCKET]
winsock.closesocket.restype = ctypes.c_int

winsock.htons.argtypes = [ctypes.c_ushort]
winsock.htons.restype = ctypes.c_ushort

winsock.inet_addr.argtypes = [ctypes.c_char_p]
winsock.inet_addr.restype = ctypes.c_uint32


def _send_all(sock, payload: bytes) -> None:
    sent_total = 0

    while sent_total < len(payload):
        chunk = payload[sent_total:]
        buffer = ctypes.create_string_buffer(chunk)

        sent = winsock.send(
            sock,
            ctypes.cast(buffer, ctypes.c_void_p),
            len(chunk),
            0,
        )

        if sent == SOCKET_ERROR or sent == 0:
            raise OSError("Failed to send TCP request")

        sent_total += sent


def _receive_line(sock) -> bytes:
    received = bytearray()
    buffer = ctypes.create_string_buffer(4096)

    while len(received) <= 65536:
        count = winsock.recv(
            sock,
            ctypes.cast(buffer, ctypes.c_void_p),
            len(buffer),
            0,
        )

        if count == SOCKET_ERROR:
            raise OSError("Failed to receive TCP response")

        if count == 0:
            break

        received.extend(buffer.raw[:count])

        if b"\n" in received:
            return bytes(received.split(b"\n", 1)[0])

    if len(received) > 65536:
        raise ValueError("TCP response is too large")

    raise OSError("Server closed the connection without a complete response")


def send_request(action: str, username: str, password: str) -> dict:
    """Send a login/register JSON request and return the server response."""

    startup_data = ctypes.create_string_buffer(512)

    startup_result = winsock.WSAStartup(
        0x0202,
        ctypes.cast(startup_data, ctypes.c_void_p),
    )

    if startup_result != 0:
        raise OSError(f"WSAStartup failed: {startup_result}")

    sock = None

    try:
        sock = winsock.socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)

        if sock == INVALID_SOCKET:
            raise OSError("Could not create TCP socket")

        address = SockAddrIn()
        address.sin_family = AF_INET
        address.sin_port = winsock.htons(SERVER_PORT)
        address.sin_addr = winsock.inet_addr(SERVER_IP)
        address.sin_zero = (ctypes.c_ubyte * 8)(*([0] * 8))

        result = winsock.connect(
            sock,
            ctypes.byref(address),
            ctypes.sizeof(address),
        )

        if result == SOCKET_ERROR:
            raise OSError(
                f"Could not connect to TCP server at "
                f"127.0.0.1:{SERVER_PORT}. "
                "Make sure tcp_server.py is running."
            )

        request = json.dumps(
            {
                "action": action,
                "username": username,
                "password": password,
            },
            ensure_ascii=False,
        ).encode("utf-8") + b"\n"

        _send_all(sock, request)

        response_bytes = _receive_line(sock)
        response = json.loads(response_bytes.decode("utf-8"))

        if not isinstance(response, dict):
            raise ValueError("Unexpected response from TCP server")

        return response

    finally:
        if sock is not None and sock != INVALID_SOCKET:
            winsock.closesocket(sock)

        winsock.WSACleanup()