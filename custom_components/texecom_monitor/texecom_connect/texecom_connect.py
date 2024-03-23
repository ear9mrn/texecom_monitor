import time, select, requests
import sys, socket
from threading import Thread

class texecom_cestron:

    def __init__(self, host, port=1234, code="", data_type="basic", log=1):

        self.host = host
        self.port = port
        self.code = code
        self._callbacks = []
        #self.data = None
        self.data_type = data_type
        self.log = log #logging 0 = none, 1 = basic, 2 = all.
        self.message = None
        #self.inputs = None
        #self.user_input = None
        self._client_input = None
        self.thread = None
        self.threadstop = False
        self.connected = False
        self.connect()

    def connect(self):

        while True:

            try:

                # connect to Texecom Panel
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                if self.log > 0:
                    print("Connected to Texecom panel...\n\n",flush=True)
                self.connected = True
                # Add sys.stdin to inputs list for user input
                self.inputs = [self.socket, sys.stdin ]
                return

            except Exception as e:
                print(f'Couldnt connect to texecom on {self.host}:{self.port}\nError:{e}\nCheck configuration...',flush=True)
                time.sleep(10)

    def client_input(self, text):
        self._client_input = text

    def add_callback(self, func):

        if func not in self._callbacks:
            self._callbacks.append(func)

    #this is where to listen to the EPSHome device that sends teh Texecom messages.
    def listen(self):
        self.thread = Thread(target = self.client)
        self.thread.start()

    def client(self):

        while True:

            try:
                #three second timeout
                readable, _, _ = select.select(self.inputs, [], [], 3)

                for sock in readable:

                    if sock == self.socket:

                        # Handle data received from server
                        tmp = str(sock.recv(100), encoding='utf-8')

                        if not tmp:
                            print("Lost connection. Trying to reconnect...\n",flush=True)
                            self.socket.close()
                            self.connect()
                        else:
                            tmp = tmp.strip('\n')
                            tmp = tmp.strip('\r')
                            tmp = tmp.split('"')
                            tmp.pop(0)
                            for j in tmp:
                                self.data = '"' + j
                                self.event()

                    else:
                        # Handle user input or clase input
                        self.user_input = sys.stdin.readline()
                        if self.user_input:
                            self.input()


                time.sleep(1)
                #await asyncio.sleep(1)

            except socket.error as e:
                print(f"Socket error: {e}", flush=True)
                self.socket.close()
                self.connect()

            if self._client_input:
                self.user_input = self._client_input
                self._client_input = None
                self.input()

            if self.threadstop:
                break


    def sendkeys(self,key_input):

        for i in key_input:
            j = f"KEY{i}"
            self.sendcom(j)
            time.sleep(0.4)


    def sendcom(self,command):

        self.socket.sendall(command.encode('utf-8'))


    def input(self):

        self.user_input = self.user_input.strip('\n')
        self.user_input = self.user_input.upper()

        match self.user_input:

            case "QUIT":
                self.stop()
            case "LSTATUS":
                self.sendcom(self.user_input)
            case "ASTATUS":
                self.sendcom(self.user_input)
            case "ARM":
                if self.log > 0:
                    print("Arming the system...",flush=True)
                self.sendkeys([self.code,'Y'])
            case "DISARM":
                if self.log > 0:
                    print("Disarming the system...",flush=True)
                self.sendkeys([self.code,'Y'])
            case "PARTARM":
                if self.log > 0 :
                    print(f'Part arming the system...',flush=True)
                self.sendkeys([self.code,'N','Y','Y'])
            case _:
                if self.log > 0:
                    print(self.user_input,flush=True)
                self.sendcom(self.user_input)

    def respond(self,info):

        for func in self._callbacks:
            func(info)

    def event(self):

        if self.data_type == "raw":
            for func in self._callbacks:
                func(self.data)
            return

        #just print the screen messages
        if len(self.data) > 6 :
            self.respond(self.data)
            return

        try:
            zora = int(self.data[2:5])
        except:
            pass

        if self.data_type == "basic":

            t = time.localtime()
            c_time = time.strftime("%H:%M:%S", t)

            match self.data[1]:

                case "Z":
                    for func in self._callbacks:
                        func({'code':self.data[1:6],'zone':zora,
                              'state':self.data[5],'time':c_time})
                case "U":
                    for func in self._callbacks:
                        func({'code':self.data[1:6],
                              'values':self.data[2:6],'time':c_time})
                case "X":
                    for func in self._callbacks:
                        func({'code':self.data[1:6],
                              'zone':zora,'time':c_time})
                case "A":
                    for func in self._callbacks:
                        func({'code':self.data[1:6],
                              'zone':zora,'time':c_time})
                case "L":
                    for func in self._callbacks:
                        func({'code':self.data[1:6],
                              'zone':zora,'time':c_time})
                case "E":
                    for func in self._callbacks:
                            func({'code':self.data[1:6],
                                  'zone':zora,'time':c_time})
                case "Y":
                    for func in self._callbacks:
                        func({'code':self.data[1:5],'A': self.data[1],
                              'B':self.data[2],'C':self.data[3],
                              'D':self.data[4],'time':c_time})
                case "N":
                    for func in self._callbacks:
                        func({'code':self.data[1:5],'A': self.data[1],
                              'B':self.data[2],'C':self.data[3],
                              'D':self.data[4],'time':c_time})
            return

        if self.data_type == "info":

            match self.data[1]:

                case "Z":
                    for func in self._callbacks:
                        text = f"Triger Event\n"
                        text += "Event code: {self.data}\n"
                        text += f"Zone: {zora}\n"
                        text += f"Status: {self.data[5]}\n"
                        func(text)
                case "U":
                    for func in self._callbacks:
                        text = f"Code event: {self.data}\n"
                        func(text)
                case "X":
                    for func in self._callbacks:
                        text = f"Arming event: {self.data}\n"
                        text += f"Area: {zora} Arming\n"
                        func(text)
                case "A":
                    for func in self._callbacks:
                        text = f"Armed event: {self.data}\n"
                        text += f"Area: {zora} Armed\n"
                        func(text)
                case "D":
                    for func in self._callbacks:
                        text = f"Disarm event: {self.data}\n"
                        text += f"Area: {zora} Disamed\n"
                        func(text)
                case "L":
                    for func in self._callbacks:
                        text = f"Trigger event: {self.data}\n"
                        text += f"Area: {zora} Alarmed\n"
                        func(text)
                case "E":
                    for func in self._callbacks:
                        text = f"Entry event: {self.data}\n"
                        text += f"Area: {zora} Triggered\n"
                        func(text)
                case "Y":
                    for func in self._callbacks:
                        text = f"Area Status: {self.data}"

                        for area, j in enumerate(self.data[1:5]):
                            state = "Not Armed"
                            if j == "Y":
                                state = "Armed"
                            text += f"Area {chr(area+65)}: {state}\n\n"

                case "N":
                    for func in self._callbacks:
                        text = f"Area Status: {self.data}\n"
                        for area, j in enumerate(self.data[1:5]):
                            state = "Not Armed"
                            if j == "Y":
                                state = "Armed"
                            text += f"Area {chr(area+65)}: {state}\\n"

    def stop(self):

        print("Texecom client teminated...")
        self.threadstop = True
        self.socket.close()
        self.connected = False

    def reconnect(self):

        print(f"Lost connection... Trying to reconnect to Texecom panel on {self.host}:{self.port}",flush=True)

        timeout = time.time() + 30   # 30 seconds from now
        while not self.socket:

            if time.time() > timeout:
                print(f'Unable to reconnect (timeout) to Texecom panel on {self.host}:{self.port}',flush=True)
                sys.exit()

            try:
                self.socket.connect((self.host, self.port))

            except socket.error as e:
                print(f'Couldnt connect to Texecom panel on {self.host}:{self.port}\nError:{e}. Will try again.',flush=True)
                time.sleep(10)
