#  coding: utf-8
import socketserver
import os
import sys

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


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):
        self.request_is_valid = False
        self.code = ""
        self.data = self.request.recv(1024).strip()
        print("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK", 'utf-8'))

        self.method, self.directory = self.splitRequest(
            self.data.decode())

        self.code = self.checkMethod(self.method)

        self.code, self.contentType, self.fileDir = self.checkDirectory(
            self.directory)

        print(self.fileDir)

        self.f = open(self.fileDir, 'r').read()

        # print("HTTP/1.1 200 OK\r\n" + self.contentType + self.f)

        newRequest = self.generateRequest(self.code, self.contentType, self.f)
        self.request.sendall(newRequest.encode())

    def splitRequest(self, requestData):
        stringArr = requestData.split(" ")
        print(stringArr)
        return stringArr[0], stringArr[1]

    def checkMethod(self, method):
        print("CHECK METHOD")
        if method != "GET":
            self.request_is_valid = False
            return "405"
        else:
            return ""

    def checkDirectory(self, directory):
        print("CHECK DIR")

        # calls to localhost:8080/ or localhost:8080/deep/
        # REDIRECT 301
        if directory[len(directory)-1] == '/':

            return "301 Moved Permanently", "text/html\r\n", ""

        # ALL calls BELOW are to localhost:8080 or localhost:8080/deep
        fileDir = os.getcwd()
        fileDir += "/www" + directory

        print("fileDir: ", fileDir)

        extension = os.path.splitext(directory)

        print("extension: ", extension)

        if extension[1] == "":
            # dealing with either "/", or "/deep" TO "/index.html" or "/deep/index.html"
            if (fileDir[len(fileDir)-1] == '/'):
                fileDir += "index.html"
            else:
                fileDir += "/index.html"
            contentType = "text/html\r\n"

        # ALL calls below are dealing with either "/index.html" or "/base.css" or "deep/deep.css"
        elif extension == ".css":
            contentType = "text/css\r\n"

        elif extension == ".html":
            contentType = "text/html\r\n"
        else:
            contentType = "text/html\r\n"

        return "404", contentType, fileDir

    def errorCheck(self, errorCode):
        if errorCode == "":
            return False

    def generateRequest(self, code, contentType, content):
        httpResponse = "HTTP/1.1 " + code + "\r\n" + \
            contentType + "\r\n" + content + "\r\n\r\n"
        return httpResponse


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
