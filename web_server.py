#!/usr/bin/env python

import roslib
roslib.load_manifest('rospy')
roslib.load_manifest('actionlib')
roslib.load_manifest('actionlib_msgs')
roslib.load_manifest('geometry_msgs')

import rospy
import BaseHTTPServer
import urlparse
import os
from mimetypes import types_map
from geometry_msgs.msg import (
    Twist,
    Vector3,
    Point
)
from std_msgs.msg import String
from controller import Controller

controller = None

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    # def __init__(self):
    #     self.msg = Twist()
    #     self.cmd_vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist, queue_size=10)
    #     self.music_commands_pub = rospy.Publisher('music_commands', String)

    def do_GET(self):
        query_string = urlparse.urlparse(self.path).query
        parameters = urlparse.parse_qs(query_string)

        # print "YOOO\n"
        print self.path

        if 'type' not in parameters:
            try:
                if self.path == "/":
                    self.path = "/index.html"
                if self.path == "favicon.ico":
                    return
                fname,ext = os.path.splitext(self.path)
                if ext in (".html", ".css", ".js", ".png", ".jpg"):
                    with open(os.path.join(os.getcwd(),self.path[1:])) as f:
                        self.send_response(200)
                        self.send_header('Content-type', types_map[ext])
                        self.end_headers()
                        self.wfile.write(f.read())
                return
            except IOError:
                self.send_error(404)

        command_type = parameters['type'][0]
        
        if command_type == 'base':
            base_x = 0.0
            if 'x' in parameters:
                base_x = float(parameters['x'][0])
            base_y = 0.0
            if 'y' in parameters:
                base_y = float(parameters['y'][0])
            base_z = 0.0
            if 'z' in parameters:
                base_z = float(parameters['z'][0])

            # twist_msg = Twist(Vector3(base_x, 0.0, 0.0), Vector3(0.0, 0.0, 0))
            # self.cmd_vel_pub.publish(twist_msg)

            controller.move_base(base_x, base_y, base_z)

        elif command_type == 'music':
            msg = parameters['play'][0]
            if (msg == "play"):
                controller.play_music("play")

        # response
        self.send_response(204)
        return

    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    server_address = ('', 31337)
    httpd = BaseHTTPServer.HTTPServer(server_address, RequestHandler)
    httpd.timeout = 5  # set timeout to 5 seconds to check for shutdown
    rospy.init_node('web_server', anonymous=True)

    controller = Controller()

    print "HTTP server started at {}:{}".format(httpd.server_name, httpd.server_port)

    # twist_msg = Twist(Vector3(0.3, 0.0, 0.0), Vector3(0.0, 0.0, 0))
    # cmd_vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist)
    # cmd_vel_pub.publish(twist_msg)

    # spin for request
    # r = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        httpd.handle_request()
        # r.sleep()

    print "\nHTTP server stopped"
