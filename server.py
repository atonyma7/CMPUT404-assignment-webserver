#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Anthony Ma
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

# Sources used:
# https://stackoverflow.com/a/32628115
# https://www.codementor.io/@joaojonesventura/building-a-basic-http-server-from-scratch-in-python-1cedkg0842
# https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/


class MyWebServer(socketserver.BaseRequestHandler):
    #helper functions
    def send_content(self, file_path):
        mt = mimetypes.guess_type(file_path)
        if mt:
            print("Mime Type:", mt[0])
            mime_type = mt[0]
        else:
            #default to html
            mime_type = 'text/html'
        f = open(file_path, 'r+b')
        self.request.sendall(bytearray("HTTP/1.1 200 OK\r\n",'utf-8'))
        self.request.sendall(bytearray("Content-Type: {}\r\n".format(mime_type), 'utf-8'))
        self.request.sendall(bytearray("\r\n", 'utf-8'))
        content = f.read()
        self.request.sendall(content)
        f.close()
        
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        #we can just split on whitespace, the first argument will be the method used and the second will be the 
        http_method = self.data.decode().split()[0]
        requested_path = self.data.decode().split()[1]
        print (http_method)
        print (requested_path)       
        mime_type = 'text/html'
        if (http_method == 'GET'):
            #requested path is the requested path we parsed from the http request data
            #whereas file path is the path of the file that exists on our system that we want to open later
            file_path = os.path.join(os.getcwd(), 'www' + requested_path)  

            #check that the absolute path of the requested file path isn't trying to access something outside of the www directory
            if (os.path.join(os.getcwd(), 'www') not in os.path.abspath(file_path)):
                self.request.sendall(bytearray("HTTP/1.1 404 Not found\r\n",'utf-8'))
            else:
                #specifically check for request path that do not end with '/', if they don't, check that the file path that was 
                #created in the above code is an existing directory or not, if it is, add '/'
                #the next if block should then handle this file path and serve the index.html file contained in the directory
                if not requested_path.endswith('/'):
                    if os.path.isdir(file_path):
                        file_path += '/'
                        self.request.sendall(bytearray("HTTP/1.1 301 Moved Permanently\r\n",'utf-8'))
                        self.request.sendall(bytearray("Location: http://127.0.0.1:8080" + requested_path +"/\r\n",'utf-8'))
                if not os.path.isfile(file_path):
                    #serve index.html if possible (meaning the path given is that of a directory)
                    if os.path.isfile(file_path + 'index.html'):
                        file_path += 'index.html'
                        self.send_content(file_path)
                    else:
                        self.request.sendall(bytearray("HTTP/1.1 404 not found\r\n",'utf-8'))
                else:
                    self.send_content(file_path)

        else:
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n", 'utf-8'))


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
