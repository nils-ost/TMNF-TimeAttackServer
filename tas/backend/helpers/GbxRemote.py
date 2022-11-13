import socket
from xmlrpc.client import loads as xmlloads
from xmlrpc.client import dumps as xmldumps
from xmlrpc.client import Fault as xmlFault


class GbxRemote():
    def __init__(self, host, port, user, pw):
        self.connection_info = (host, port, user, pw)

    def connect(self):
        try:
            host, port, user, pw = self.connection_info
            self.handler = 0x80000000
            self.callback_enabled = False
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((socket.gethostbyname(host), port))

            # recieve and validate header
            data = self.socket.recv(4)
            headerLength = data[0] | (data[1] << 8) | (data[2] << 16) | (data[3] << 24)

            header = self.socket.recv(headerLength)
            if not header.decode() == 'GBXRemote 2':
                print('Invalid header.')
                exit(0)

            self.callMethod('Authenticate', user, pw)
            return True
        except OSError:
            return False

    def _incHandler(self):
        self.handler += 1
        if self.handler > 0xFFFFFFFF:
            self.handler = 0x80000000

    def callMethod(self, method, *argv):
        handlerBytes = bytes([
            self.handler & 0xFF,
            (self.handler >> 8) & 0xFF,
            (self.handler >> 16) & 0xFF,
            (self.handler >> 24) & 0xFF])

        data = xmldumps(argv, method).encode('utf-8')
        packetLen = len(data)
        packet = bytes([
            packetLen & 0xFF,
            (packetLen >> 8) & 0xFF,
            (packetLen >> 16) & 0xFF,
            (packetLen >> 24) & 0xFF
        ])
        packet += handlerBytes
        packet += data

        self.socket.send(packet)

        header = self.socket.recv(8)
        size = header[0] | (header[1] << 8) | (header[2] << 16) | (header[3] << 24)
        responseHandler = header[4] | (header[5] << 8) | (header[6] << 16) | (header[7] << 24)
        if responseHandler != self.handler:
            print('Response handler does not match!')
            exit(0)

        response = self.socket.recv(size)
        while len(response) < size:
            response += self.socket.recv(size - len(response))
        try:
            params, func = xmlloads(response.decode('utf-8'))
        except xmlFault as fault:
            print(f'GbxRemote call of method "{method}" with params {argv} faulted with code {fault.faultCode} saying: {fault.faultString}')
            params, func = (list(), None)

        self._incHandler()
        if func is None:
            return params
        else:
            return (func, params)

    def receiveCallback(self):
        if not self.callback_enabled:
            self.callMethod('EnableCallbacks', True)
            self.callback_enabled = True

        header = self.socket.recv(8)
        size = header[0] | (header[1] << 8) | (header[2] << 16) | (header[3] << 24)
        # responseHandler = header[4] | (header[5] << 8) | (header[6] << 16) | (header[7] << 24)

        response = self.socket.recv(size)
        while len(response) < size:
            response += self.socket.recv(size - len(response))

        params, func = xmlloads(response.decode('utf-8'))
        return (func, params)
