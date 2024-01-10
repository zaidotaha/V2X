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
from Crypto.Util.number import bytes_to_long as b2l
from Crypto.Util.number import long_to_bytes as l2b


RSUkey = b"euoyuheffgnwxtocacmcxvuyiytfzd"
def broadcastMessage(msg):
        timestamp = str(int(time.time()))
        if len(timestamp) == 10:
            timestamp = "00" + timestamp
        elif len(timestamp) == 11:
            timestamp = "0" + timestamp
        hmac_value = hmac.new(RSUkey.encode(), timestamp.encode()+msg, hashlib.sha256).hexdigest()

        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.2)
        message = hmac_value.encode()+timestamp.encode()+msg
        for x in range(10):
            server.sendto(message+b'\n', ("255.255.255.255", 6107))
            print("message sent!", flush=True)
            time.sleep(0.1)



broadcastMessage(b"0000000001Don't go left")

