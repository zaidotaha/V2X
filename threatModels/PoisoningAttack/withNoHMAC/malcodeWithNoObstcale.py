from picarx import Picarx
from time import sleep
from notSecureClient import *

# Too many global variables

# left_turn should be generalized into turn. We should be able to pass a parameter to decide 
#   whether it should turn left or right

# Movement function

# Understand client.on_message = on_message

# we propose that the name of the client should be the IP of the car


accident_left = False
accident_right = False
turned_left = False
turned_right = False
# By using the accident variable, we can make decisions based on MQTT messages

# class myClient:
    
#     def __init__(self, ip, port):
#         self.ip = ip
#         self.port = port
#         self.client = Client(ip, port)
    
#     def subscribe(self,topic):
#         self.client.startListening()
        

class car:
    
    def __init__(self):
        self.px = Picarx()
        self.current_state = None
        self.pers = 0
        
    def stop(self):
        self.px.stop()
    
    def turn(self,direction):
        print("car is turning")
        if (direction == "left"):
            direction = -1
        elif (direction == "right"):
            direction = 1
        try:
            self.px.forward(30)
            sleep(0.13)
            self.px.set_dir_servo_angle(0)
            self.px.forward(30)
            sleep(.05)
            for angle in range(0,35):
                self.px.set_dir_servo_angle(direction * angle)
                sleep(0.01)
            self.px.forward(30)
            sleep(0.7)
            self.px.set_dir_servo_angle(0)
        finally:
            self.px.forward(30)
            sleep(0.3)
            
    def line_tracking(self, px_power, offset, client):
        gm_val_list = self.px.get_grayscale_data()
        gm_state = self.px.get_line_status(gm_val_list)
        if gm_state == 'forward':
            self.px.set_dir_servo_angle(0)
            self.px.forward(px_power)
        elif gm_state == 'stop':
            print("junction")
            if accident_left == False:
                    self.turn("left")
                    client.publish(b"0000000001Don't go left")
                    global turned_left
                    turned_left = True
            elif accident_right == False:
                self.turn("right")
                global turned_right
                turned_right = True
            else:
                return False
                # returning false means there is an accident, the car will exit the loop and stop
        elif gm_val_list[0] < gm_val_list[2]:
            self.px.set_dir_servo_angle(-offset)
            self.px.forward(px_power+1)
        else:
            self.px.set_dir_servo_angle(offset)
            self.px.forward(px_power+1)
        return True

    def obstacle_avoidance(self, client):
        distance = self.px.ultrasonic.read()
        print("distance: ",distance)
        if (distance < 20) and (distance!=-1):
            global pers
            pers = pers + 1
        else:
            pers = 0
        if (pers >= 3):
            self.px.stop()
            print("yo")
            if(turned_left == True):
                client.publish(b"0000000001Don't go left")
            elif(turned_right == True):
                client.publish(b"0000000001Don't go right")
            quit()  
    
    def get_status(self,val_list):
        _state = self.px.get_line_status(val_list)  # [bool, bool, bool], 0 means line, 1 means background
        if _state == [0, 0, 0]:
            return 'stop'
        elif _state[1] == 1:
            return 'forward'
        elif _state[0] == 1:
            return 'right'
        elif _state[2] == 1:
            return 'left'

def onVerifiedMessage(data):
        print("thread")
        global accident_left, accident_right
        message = data[10:len(data)-1]
        print(message.decode())
        if("Don't go left" == message.decode()):
            accident_left = True
        elif ("Don't go right" == message.decode()):
            accident_right = True
        print("Received message: ", str(data))
    
 # We tried to omit loop_start and loop_end while including the subscribe and on_message functions in the loop and it worked 
if __name__=='__main__':
    ip = "192.168.114.39"
    port = 1344
    car1 = car()
    client1 = Client(ip,port)
    client1.onVerifiedMessage = onVerifiedMessage
    
    client1.startListening()
    

    try:
        while True:
            car1.obstacle_avoidance(client1)
            if(car1.line_tracking(3,15, client1)==False):
                break
    finally:
        car1.stop()
        



    