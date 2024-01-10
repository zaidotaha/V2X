#open listening port on car on port 6107

#message format
#0000000000
#HMAC, (ID, MSG) \n

#buffer size 1024
#receive message ->
#get shared secret of RSU -> verify
#if correct -> take action

import socket, hmac, hashlib, threading

class Client:
    def __init__(self, IP, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = IP
        self.port = port
        
    
    
    def Listening(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            #start a UDP listener on port 6107
            client.bind(("", 6107))
            while True:
                data, addr = client.recvfrom(1024)
                if self.verify(data) == True:
                    self.onVerifiedMessage(data)   
        except Exception:
            return False  

    def onVerifiedMessage(self, data):
        print("this function should be replaced")

    def publish(self,msg):
        try:
            self.sock.connect((self.IP, self.port))
            self.sock.send(msg +b"\n")
            self.sock.close()
        except Exception:
            return False

    def startListening(self):
        listenToRSU = threading.Thread(target=self.Listening)
        listenToRSU.start()


if __name__ == "__main__":
    msg = b"0000000001Don't go left"
    


