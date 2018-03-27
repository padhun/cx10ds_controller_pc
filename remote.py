import socket
import pygame
from pygame.locals import *
import threading

step = 5

class RemoteCX10DS:
    def __init__(self):
        self.IP = "192.168.4.1"
        self.PORT = 8033
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.header = b'\xcc' #first byte of every payload
        self.footer = b'\x33' # last byte of every payload

        self.throttle = 128 # controls the throttle range 0-255
        self.rudder = 128 # controls the rudder range 48-208
        self.aileron = 128 #todo: range check
        self.elevator = 128 #todo: range check
        self.crc = 0 #crc calculated from thr, rdr, ail, elev, mode xor product
        self.mode = 0 # 0 = idle, 1 = takeoff, 2 = land

        #initialize the pygame module for keyboard interrupts
        pygame.init()
        self.screen = pygame.display.set_mode((600, 400))

        self.message = ''


    #sends out a message to the given IP/PORT every 0.5 seconds
    def send(self):
        self.t = threading.Timer(0.5, self.send)
        self.t.start()
        self.createMSG()
        self.sock.sendto(self.message, (self.IP, self.PORT))
        print ":".join(x.encode('hex') for x in self.message)

    # crc calculation
    def crc_calculate(self):
        self.crc = self.throttle ^ self.rudder ^ self.aileron ^ self.elevator ^ self.mode

    # create the message from the actual values of the virtual remote, must be called before each send
    def createMSG(self):
        self.crc_calculate()
        data = chr(self.aileron) + chr(self.elevator) + chr(self.throttle) + chr(self.rudder) + chr(self.mode) + chr(self.crc)

        self.message = self.header + data + self.footer

    # validate the step function with constraints
    def valid_step(self, value, step, MIN = 0, MAX = 255):
        return max(min(MAX, value+step), MIN)

    # main loop for handling keyboard inputs
    def loop(self):
        while True:
            events = pygame.event.get()
            for evt in events:
                if evt.type == pygame.KEYDOWN:
                    if evt.key == K_w:
                        self.throttle = self.valid_step(self.throttle, step)
                        print "Throttle {0}".format(self.throttle)

                    if evt.key == K_s:
                        self.throttle = self.valid_step(self.throttle, -step)
                        print "Throttle {0}".format(self.throttle)

                    if evt.key == K_a:
                        self.rudder = self.valid_step(self.rudder, -step, 48, 208)
                        print "Rudder {0}".format(self.rudder)

                    if evt.key == K_d:
                        self.rudder = self.valid_step(self.rudder, step, 48, 208)
                        print "Rudder {0}".format(self.rudder)

                    if evt.key == K_UP:
                        self.elevator = self.valid_step(self.elevator, step)
                        print "elevator {0}".format(self.elevator)

                    if evt.key == K_DOWN:
                        self.elevator = self.valid_step(self.elevator, -step)
                        print "elevator {0}".format(self.elevator)

                    if evt.key == K_LEFT:
                        self.aileron = self.valid_step(self.aileron, -step)
                        print "aileron {0}".format(self.aileron)

                    if evt.key == K_RIGHT:
                        self.aileron = self.valid_step(self.aileron, step)
                        print "aileron {0}".format(self.aileron)

                    if evt.key == K_p:
                        self.mode = 1
                        print "Mode {0} //takeoff".format(self.mode)

                    if evt.key == K_l:
                        self.mode = 2
                        print "Mode {0} //land".format(self.mode)

                    if evt.key == K_SPACE:
                        self.throttle = 128
                        self.rudder = 128
                        self.aileron = 128
                        self.elevator = 128
                        self.mode = 0

                        print "Reset commands"

                    if evt.key == K_ESCAPE:
                        print "Exiting.."
                        self.t.cancel()
                        raise SystemExit

                elif evt.type == pygame.QUIT:
                    print "Exiting.."
                    self.t.cancel()
                    raise SystemExit


# example for using the class
if __name__ == "__main__":
    rmt = RemoteCX10DS()
    rmt.send()
    rmt.loop()
