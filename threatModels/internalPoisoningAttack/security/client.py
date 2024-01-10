#open listening port on car on port 6107

#message format
#0000000000
#HMAC, (ID, MSG) \n

#buffer size 1024
#receive message ->
#get shared secret of RSU -> verify
#if correct -> take action

import socket, hmac, hashlib, threading, time
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256


class Client:
    def __init__(self, IP, port):
        self.secret_key = b"papaekayqltwwcmgjdvi"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.RSUkey = b"euoyuheffgnwxtocacmcxvuyiytfzd"
        self.public_key = RsaKey(n=157068234422428490129594143980843888692240498464893289378996534900275163027272028752035382174400043949611131240805058562534350929610244955974829997556672507967425805474967536925012029406716056199883898915244912337843270853730822937694022149546268993927630924149378344166390005565204552685528919202396005406999, e=65537)
        self.IP = IP
        self.port = port
        
    
    def verify(self, MSG):
        try:
            signature = MSG[0:128]
            msg = MSG[128:len(MSG)-1]
            timestamp = int(MSG[128:140])
            if timestamp < (int(time.time()) -5) or timestamp > int(time.time()):
                return False
            print(msg)
            hmacValue = SHA256.new(self.RSUkey + msg)
            try:
                pkcs1_15.new(self.public_key).verify(hmacValue, signature)
                return True
            except Exception:
                return False
        except Exception:
            return False
        
    def Listening(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        client.bind(("", 6107))
        while True:
            data, addr = client.recvfrom(1024)
            if self.verify(data) == True:
                self.onVerifiedMessage(data)     

    def onVerifiedMessage(self, data):
        print("this function should be replaced")

    def publish(self,msg):
        self.sock.connect((self.IP, self.port))
        timestamp = str(int(time.time()))
        if len(timestamp) == 10:
            timestamp = "00" + timestamp
        elif len(timestamp) == 11:
            timestamp = "0" + timestamp
        hmac_value = hmac.new(self.secret_key, timestamp.encode()+msg, hashlib.sha256).hexdigest()
        
        self.sock.send(hmac_value.encode()+timestamp.encode()+msg +b"\n")
        self.sock.close()

    def startListening(self):
        listenToRSU = threading.Thread(target=self.Listening)
        listenToRSU.start()

msg = b"0000000001Don't go left"





