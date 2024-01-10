import hmac, hashlib, sqlite3, socket, time, threading

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

def handleRequest(conn, addr):
    try:
        #receive data until the trailer of \n
        data = conn.recv(1024)
        while True:
            if b'\n' in data:
                break
            data = conn.recv(1024)
        
        #remove the car ID then broadcast the message
        MSG = data[10:len(data)-1]
        broadcastMessage(b"0000000001"+MSG)
    except Exception:
        return False
    
  

def broadcastMessage(msg):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server.settimeout(0.2)
        #broadcast 10 times
        for x in range(10):
            server.sendto(msg+b'\n', ("255.255.255.255", 6107))
            print("message sent!", flush=True)
            time.sleep(0.1)
    except Exception:
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