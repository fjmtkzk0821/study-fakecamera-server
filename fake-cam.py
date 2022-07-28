import base64
from socket import timeout
import cv2
import numpy as np
import pyvirtualcam
from device import Device
from fcss import FCSocketServer, SocketRequest, SocketResponse
from process_pool import ProcessPool
from util import generateAlphaDigit, generateNumber
import multiprocessing as mp

DEFAULT_FPS = 12
isInit = False

def mainCommandLoop(que: mp.Queue):
    global isInit
    try:
        server = FCSocketServer(6767)#6767
        server.startListen()
        __pairCode = generateNumber(6)
        __pairedDevice = None
        print("please use "+__pairCode+" for pairing")
        while True:
                if(__pairedDevice is not None):
                    try:
                        s, addr = server.socket.accept()
                        if(__pairedDevice.ip[0] == addr[0]):
                                raw = server.recvMsg(s)
                                if raw is not None:
                                    response = SocketResponse(raw)
                                    if(response.command == "COMU"):
                                        np_frame = np.frombuffer(base64.b64decode(response.data["frame"]), dtype=np.uint8)
                                        frame = cv2.imdecode(np_frame, 1)
                                        que.put(frame[:, :, ::-1])
                                        if(not isInit and que.qsize() > 3):
                                            isInit = True
                                        
                    except timeout:
                        print("timeout, disconnected ["+__pairedDevice.name+"]")
                        __pairedDevice = None
                else:
                    try:
                        s, addr = server.socket.accept()
                        raw = server.recvMsg(s)
                        if raw is not None:
                            response = SocketResponse(raw)
                            if(response.command == "PAIR"):
                                code = response.data["code"]
                                # print("recvCode: "+ code)
                                if(code == __pairCode):
                                    __secret = generateAlphaDigit(16)
                                    __pairedDevice = Device(response.data["device"], addr, __secret)
                                    sr = SocketRequest("PAIR", {"status": 200, "secret": __secret})
                                    sr.send(s)
                                else:
                                    __secret = generateAlphaDigit(16)
                                    __pairedDevice = Device(response.data["device"], addr, __secret)
                                    sr = SocketRequest("PAIR", {"status": 200})
                                    sr.send(s)
                    except timeout:
                        pass
    except KeyboardInterrupt:
        print('mainCommandLoop KeyboardInterrupt')
        # s, addr = server.socket.accept()
        # sr = SocketRequest("DISC", {})
        # sr.send(s)
    except BaseException as err:
        print(f"mainCommandLoop {err=}, {type(err)=}")
    server.socket.close()
    cv2.destroyAllWindows()
    
def showFrameLoop(que):
    try:
        global isInit
        #0.8
        # with pyvirtualcam.Camera(width=640, height=480, fps=DEFAULT_FPS) as cam:
        with pyvirtualcam.Camera(width=320, height=240, fps=DEFAULT_FPS) as cam:
        # with pyvirtualcam.Camera(width=512, height=384, fps=DEFAULT_FPS) as cam:
            print(f'Using virtual camera: {cam.device}')
            while True:
                if(not que.empty()):
                    frame = que.get()
                    cam.send(frame)
                    del frame
                    cam.sleep_until_next_frame()
    # except KeyboardInterrupt:
    #     print('showFrameLoop KeyboardInterrupt')
    except BaseException as err:
        print(f"showFrameLoop {err=}, {type(err)=}")

if __name__ == "__main__":
    q = mp.Queue()
    # que = queue.Queue()
    pp = ProcessPool()
    try:
        pp.append(mp.Process(target=mainCommandLoop, args=(q,)))
        pp.append(mp.Process(target=showFrameLoop, args=(q,)))
        pp.start()
        pp.join()
    except KeyboardInterrupt:
        print("User KeyboardInterrupt")
        pp.kill()
    except:
        print("all")
