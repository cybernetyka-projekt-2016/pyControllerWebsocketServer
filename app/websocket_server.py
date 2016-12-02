###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import json
from math import sin, cos, pi, radians
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import a_star

class ServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            data = json.loads(payload.decode('utf8'))
            x, y = data['x'], data['y']
            x, y = rotate2d(-45, (float(x), float(y)), (0, 0))
            robot.motors(int(x), int(y))
            try:
            	self.check_distance()
            except Exception as e:
                print(e)
            if self.obstacle_in_front is False:
                robot.motors(int(x), int(y))   
            elif self.obstacle_in_front is True and ( x and y ) < 0:
                robot.motors(int(x), int(y))
            else:
                # nie mozna jechac na przeszkode
                pass
            print("{}    {}".format(x, y))
        
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def check_distance(self):
        distance = robot.read_distance()
        if distance in xrange(0, 2000):
            self.handle_obstacle_in_front()
        else:
            self.obstacle_in_front = False

    def handle_obstacle_in_front(self):
        self.obstacle_in_front = True
        # tu ewentualna komenda robota o przeszkodzie
        pass

def rotate2d(degrees,point,origin):
    x = point[0] - origin[0]
    yorz = point[1] - origin[1]
    newx = (x*cos(radians(degrees))) - (yorz*sin(radians(degrees)))
    newyorz = (x*sin(radians(degrees))) + (yorz*cos(radians(degrees)))
    newx += origin[0]
    newyorz += origin[1] 
    return newx, newyorz
    


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor
    
    log.startLogging(sys.stdout)

    robot = a_star.AStar()
    factory = WebSocketServerFactory(u"ws://0.0.0.0:9000")
    factory.protocol = ServerProtocol
    factory.setProtocolOptions(maxConnections=2)

    reactor.listenTCP(9000, factory)
    reactor.run()
