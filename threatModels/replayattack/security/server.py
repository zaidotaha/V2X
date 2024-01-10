import hmac, hashlib, sqlite3, socket, time, threading


#publish -> send a message to a listening port on the server

#subscribe -> have a listening port on the car and send the message
# from server as a broadcast

#0000000000
#HMAC, (timestamp, ID, MSG) \n

#open listening port on server on port 1344
#buffer size 1024
#receive message -> open new thread
#get shared secret key from database -> verify
#if correct -> broadcast message 50

#always log everything

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
    except Exception as e:
        print(e)

def verify(MSG):
    try:
        global db
        #parse the message
        hmac_value = MSG[0:64]
        timestamp = int(MSG[64:76])
        ID = int(MSG[76:86])
        msg = MSG[64:len(MSG)-1]
        
        #check the validity of the timestamp
        if timestamp < (int(time.time()) -5) or timestamp > int(time.time()):
            return False
        
        
        #get shared key from data base
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