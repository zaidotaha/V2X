import hmac, hashlib, sqlite3, socket, time, threading
from Crypto.PublicKey.RSA import RsaKey
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

#publish -> send a message to a listening port on the server

#subscribe -> have a listening port on the car and send the message
# from server as a broadcast

#0000000000
#HMAC, (ID, MSG) \n

#open listening port on server on port 1344
#buffer size 1024
#receive message -> open new thread
#get shared secret key from database -> verify
#if correct -> broadcast message 50

#always log everything

private_key = RsaKey(n=157068234422428490129594143980843888692240498464893289378996534900275163027272028752035382174400043949611131240805058562534350929610244955974829997556672507967425805474967536925012029406716056199883898915244912337843270853730822937694022149546268993927630924149378344166390005565204552685528919202396005406999, e=65537, d=3910109166733174872918089718857237963309128785960196554951139763641895852403898788607133772030054346457582138629681752975796779554436648697269254634995668947298746425446360413472868807246028898295449880865802643425515926023334762584769310766158395522112380463463859740945524456920830451783776904770776428213, p=11896080804782288883243016140964076434690605401187700276530731212331061166136759633039175714773115439106039381665256476317316839811483906916582091746593939, q=13203359745109179957747106888736551361682377548391165777184876056534443306610607679751080500425327865076808108247501794266652765314098616555480885089474541, u=5939070273206676146808970309283529981899817887535000469855169886782728466130429832287813440139891084057200744212816416340856658041876240488049191717143188)


def handleRequest(conn, addr):
    try:
        data = conn.recv(1024)
        while True:
            if b'\n' in data:
                break
            data = conn.recv(1024)
        if verify(data) :
            print(data , " is verified")
            MSG = data[86:len(data)-1]
            broadcastMessage(b"0000000001"+MSG)
        else:
            print(data, "not verified")
    except Exception as e:
        print(e)

def broadcastMessage(msg):
    try:
        timestamp = str(int(time.time()))
        if len(timestamp) == 10:
            timestamp = "00" + timestamp
        elif len(timestamp) == 11:
            timestamp = "0" + timestamp
        
        global private_key

        hmac_value = SHA256.new(RSUkey.encode()+timestamp.encode()+ msg)
        signature = pkcs1_15.new(private_key).sign(hmac_value)
        
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.2)
        message = signature+timestamp.encode()+msg
        for x in range(10):
            server.sendto(message+b'\n', ("255.255.255.255", 6107))
            print("message sent!", flush=True)
            time.sleep(0.1)
    except Exception as e:
        print(e)


def verify(MSG):
    try:
        global db
        #parsing the message
        hmac_value = MSG[0:64]
        timestamp = int(MSG[64:76])
        ID = int(MSG[76:86])
        msg = MSG[64:len(MSG)-1]

        #verifying the timestamp
        if timestamp < (int(time.time()) -5) or timestamp > int(time.time()):
            return False
        
        #get shared key from database
        cur = db.cursor()
        cur.execute("SELECT * FROM sharedKeys WHERE ID = ?" , [ID])
        try:
            shared_key = cur.fetchone()[1]
            return hmac.new(shared_key.encode(), msg, hashlib.sha256).hexdigest() == hmac_value.decode()
        except Exception:
            return False
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    db = sqlite3.connect("shared_keys.db", check_same_thread=False)
    RSUkey = "euoyuheffgnwxtocacmcxvuyiytfzd"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 1344))
    sock.listen()
    while True:
        conn, addr = sock.accept()
        print(conn)
        t = threading.Thread(target=handleRequest, args=(conn, addr))
        t.start()