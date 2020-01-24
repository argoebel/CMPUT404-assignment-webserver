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
        self.f = ''
        self.baseAddress = "http://localhost:8080"
        self.data = self.request.recv(1024).strip()
        print("Got a request of: %s\n" % self.data)
        # self.request.sendall(bytearray("OK", 'utf-8'))

        self.method, self.directory = self.splitRequest(
            self.data.decode())

        print("self.method: ", self.method)
        print("self.directory: ", self.directory)

        self.code = self.checkMethod(self.method)

        print("self.code: ", self.code)

        self.code, self.contentType, self.fileDir = self.checkDirectory(
            self.directory)

        print("self.code: ", self.code)
        print("self.contentType: ", self.contentType)
        print("self.fileDir: ", self.fileDir)

        print(self.fileDir)

        if self.code == "200 OK\r\n":
            self.f = open(self.fileDir, 'r').read()
            newRequest = self.generateRequest(
                self.code, self.contentType, self.f)

        elif self.code == "301 Moved Permanently\r\n":
            self.fileDir = "Location: " + self.fileDir
            newRequest = self.generateRequest(
                self.code, self.contentType, self.fileDir)

        # print("HTTP/1.1 200 OK\r\n" + self.contentType + self.f)

        print(newRequest)
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
            return "HTTP/1.1 200 OK\r\n"

    def checkDirectory(self, directory):
        print("CHECK DIR")

        # calls to localhost:8080/deep/
        # REDIRECT 301
        if directory[len(directory)-1] == '/' and (len(directory) > 1):
            directory = self.baseAddress + directory
            print("301")
            return "301 Moved Permanently\r\n", "text/html\r\n" + "Location: " + directory[:len(directory)-1] + "\r\n", ''

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
                print('ONE')
            else:
                print('TWO')
                fileDir += "/index.html"
            contentType = "text/html\r\n"
            return "200 OK\r\n", contentType, fileDir

        # ALL calls below are dealing with either "/index.html" or "/base.css" or "deep/deep.css"
        elif extension[1] == ".css":
            contentType = "text/css\r\n"
            print("extension .css")
            # base case: base.css is in www/
            path = os.path.abspath(os.getcwd() + "/www")

            print("fileDir: ", fileDir)

            print(os.listdir(path))

            for root, dirs, files, in os.walk(os.getcwd() + "/www"):
                for name in files:
                    if name == directory[1:]:
                        print(os.path.join(root, name))
                        fileDir = (os.path.join(root, name))

            return "200 OK\r\n", contentType, fileDir

        elif extension[1] == ".html":
            contentType = "text/html\r\n"
            return "200 OK\r\n", contentType, fileDir

        else:
            contentType = "text/html\r\n"
            return "404", contentType, ''

    def errorCheck(self, errorCode):
        if errorCode == "":
            return False

    def generateRequest(self, code, contentType, content):
        httpResponse = "HTTP/1.1 " + code + \
            contentType + "\r\n" + content + "\r\n\r\n"
        print(httpResponse)
        return httpResponse


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
