from asyncio.tasks import sleep
import socket
import json
import struct
import select

CONNECTION_SIZE = 5

class NetworkHost:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port

    def __str__(self) -> str:
        return "Host[name: {}, ip: {}, port: {}]".format(self.name, self.ip, self.port)

class FCSocketServer:
    def __init__(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, CONNECTION_SIZE)
        self.socket.settimeout(3.0)
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        self.host = NetworkHost(host_name, host_ip, port)
    
    def getSocketAddress(self) -> tuple:
        return (self.host.ip, self.host.port)

    def startListen(self):
        self.socket.bind(self.getSocketAddress())
        self.socket.listen(CONNECTION_SIZE)
        print("Listening At:", self.getSocketAddress())

    def recvMsg(self, socket: socket.socket) -> str:
        raw_msglen = self.recvAll(socket, 4)
        if not raw_msglen:
            return None
        msgLen = struct.unpack(">I", raw_msglen)[0]
        return self.recvAll(socket, msgLen).decode("utf-8", errors='ignore')

    # def recvUDP(self, socket: socket.socket):
    #     raw_msglen, addr = self.recvAllUDP(socket, 4)
    #     if not raw_msglen:
    #         return None
    #     msgLen = struct.unpack(">I", raw_msglen)[0]
    #     return self.recvAllUDP(socket, msgLen).decode("utf-8", errors='ignore')

    def sendMsg(self, socket: socket.socket, msg):
        msg = struct.pack(">I", len(msg)) + msg
        socket.sendall(msg)

    def recvAll(self,socket: socket.socket, count) -> bytes:
        buf = b''
        ready = select.select([socket], [], [], 5)
        while count:
            if(ready[0]):
                newbuf = socket.recv(count)
                if not newbuf:
                    return None
                buf += newbuf
                count -= len(newbuf)
        return buf

    # def recvAllUDP(self,socket: socket.socket, count):
    #     buf = b''
    #     ready = select.select([socket], [], [], 5)
    #     addr = None
    #     while count:
    #         if(ready[0]):
    #             newbuf, tmpAddr = socket.recvfrom(count)
    #             if(addr != None): addr = tmpAddr
    #             if not newbuf:
    #                 return None
    #             buf += newbuf
    #             count -= len(newbuf)
    #     return buf, addr

class SocketRequest:
    def __init__(self, command, data):
        self.command = command
        self.data = data

    def send(self, s: socket.socket):
        s.sendall((self.toJSON()+"\n").encode())

    def toJSON(self) -> str:
        return json.dumps({
            "command": self.command,
            "data": self.data
        })

class SocketResponse:
    def __init__(self, raw):
        # print(raw)
        res = json.loads(raw)
        self.command = res["command"]
        self.data = res["data"]