#open listening port on car on port 6107

#message format
#0000000000
#HMAC, (ID, MSG) \n

#buffer size 1024
#receive message ->
#get shared secret of RSU -> verify
#if correct -> take action

import socket, hmac, hashlib, threading, time


class Client:
    def __init__(self, IP, port):
        self.secret_key = b"papaekayqltwwcmgjdvi"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.RSUkey = b"euoyuheffgnwxtocacmcxvuyiytfzd"
        self.IP = IP
        self.port = port
        
    
    def verify(self, MSG):
        try:
            hmac_value = MSG[0:64]
            timestamp = int(MSG[64:76])
            msg = MSG[64:len(MSG)-1]
            
            if timestamp < (int(time.time()) -5) or timestamp > int(time.time()):
                return False

            return hmac.new(self.RSUkey, msg, hashlib.sha256).hexdigest() == hmac_value.decode()
        except Exception as e:
            print(e)
            return False
            

    def Listening(self):
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            client.bind(("", 6107))
            while True:
                data, addr = client.recvfrom(1024)
                if self.verify(data) == True:
                    self.onVerifiedMessage(data)     
        except Exception as e:
            print(e)
    
    def onVerifiedMessage(self, data):
        print("this function should be replaced")

    def publish(self,msg):
        try:
            self.sock.connect((self.IP, self.port))
            timestamp = str(int(time.time()))
            if len(timestamp) == 10:
                timestamp = "00" + timestamp
            elif len(timestamp) == 11:
                timestamp = "0" + timestamp
            hmac_value = hmac.new(self.secret_key, timestamp.encode()+msg, hashlib.sha256).hexdigest()
            
            print(hmac_value.encode()+timestamp.encode()+msg +b"\n")
            self.sock.send(hmac_value.encode()+timestamp.encode()+msg +b"\n")
            self.sock.close()
        except Exception as e:
            print(e)


    def startListening(self):
        listenToRSU = threading.Thread(target=self.Listening)
        listenToRSU.start()


if __name__ == "__main__":
    msg = b"0000000001Don't go left"
    c = Client("127.0.0.1", 1344)
    c.publish(msg)