#  coding: utf-8
import socketserver
import sys
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

BUFFER_SIZE = 2048


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.method = ""            # GET, POST, PUT, DELETE, etc.
        self.response = ""          # what we send back to user
        self.filePath = "www"       # path to file such as html or css
        # type of content to be transferred (either html or css)
        self.contentType = "Content-Type: "

        print(self.request)

        self.data = self.request.recv(1024).strip()
        print("Client address:", self.client_address)
        print("Got a request of: %s\n" % self.data)
        # print("Decoded: \r", self.data.decode())
        # self.request.sendall(bytearray("OK", 'utf-8'))

        self.splitData()        # provides method and page
        self.checkRequest()     # checks if GET request
        self.checkPath()        # checks if file exists and specifies its location
        self.checkFileType()    # checks file type (css or html)

        # if there is a bad requst, send appropriate response

        print("sending html")
        f1 = open(self.filePath, 'r')
        f1 = f1.read()
        print(f1)
        print("Content type:", self.contentType)
        self.response = "HTTP/1.1 200 OK\r\n"

        print(self.response + self.contentType + f1)
        self.fullResponse = (
            self.response + self.contentType + f1).encode()
        print(self.fullResponse)
        # self.request.sendall(bytearray(
        #     self.fullResponse, 'utf-8'))
        # self.request.sendall(self.fullResponse)
        # self.request.sendall(
        #     bytearray('HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nh1 {\n    color:orange;\n    text-align:center;\n}\r\n', 'utf-8'))

    def splitData(self):
        try:
            newData = self.data.decode().split('\r\n')

            # identify type of request
            dataSplit = newData[0]
            self.method = (dataSplit.split())[0]
            self.page = (dataSplit.split())[1]
            print("method: ", self.method)
            # is equal to '/' with localhost:8080, '/deep' with localhost:8080/deep
            print("page: ", self.page)

            if (self.page[len(self.page)-1] and len(self.page) > 1) == '/':
                self.response = "HTTP/1.1 301 Moved Permanently"
                # If last character is '/' redirect to appropriate site

            return True
        except:
            return False

    def checkRequest(self):
        if self.method != "GET":
            # self.response = "HTTP/1.1 400 Bad Request\r\n\r\n"
            return False
        else:
            return True

    def checkFileType(self):
        # print(self.page)
        print(self.filePath)

        # file, extension = os.path.splitext(self.page)
        file, extension = os.path.splitext(self.filePath)
        print("extension:", extension)
        if extension == ".css":
            print("got a css")
            self.contentType += "text/css\r\n"
        else:
            print("got html")
            self.contentType += "text/html\r\n"

    def checkPath(self):
        self.filePath = os.getcwd() + "/www" + self.page

        # IF FILEPATH IS DIRECTORY, DISPLAY INDEX.HTML
        if (os.path.isdir(self.filePath)):
            if (len(self.page) == 1):
                self.filePath += "index.html"
            else:
                self.filePath += "/index.html"
        # print("filepath:", self.filePath)
        print(os.path.abspath(self.filePath))

        # if not os.path.exists(self.filePath):
        #     self.response = "HTTP/1.1 404 Not Found Error\r\n\r\n"
        #     print("path doesn't exist")


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


# https://community.zerynth.com/t/how-to-render-a-file-html-and-to-handle-get-and-post-requests/996
