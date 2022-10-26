# important imports
import json
import math
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time

# port for the server
hostName = "localhost"
serverPort = 8082

# empty queue which will store received data
queue_3 = []

# parameters for transmitting / receiving the data
headers = {'Content-Type': 'application/json'}
params = {'access_token': "params"}


# class MyServer which implements some http methods
class MyServer(BaseHTTPRequestHandler):

    # implements method for GET requests
    def do_GET(self):
        self.send_response(200)
        self.end_headers()

    # implements method for POST requests
    def do_POST(self):

        global queue_3

        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

        # receiving data via POST request from another server
        length = int(self.headers.get('Content-length', 0))
        data = json.loads(self.rfile.read(length).decode())

        # adding the received element to a queue
        queue_3.append(data['int'])
        print(queue_3)

def extract_to_2():
    global queue_3
    global headers
    global params

    while True:
        if len(queue_3) > 0:
            last = queue_3.pop()
            requests.post("http://localhost:8081", headers=headers, params=params, json={'int': last*10, 's': 3})
            time.sleep(3)
            print(queue_3)
        else:
            # continue
            time.sleep(3)


# initializing 4 extractor threads, with function extract as target
extractor_threads = [threading.Thread(target=extract_to_2) for i in range(4)]


# runner code
if __name__ == "__main__":

    # starting the threads
    for thread in extractor_threads:
        thread.start()

    # starting the web server
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
