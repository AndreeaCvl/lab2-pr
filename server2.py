# important imports
import json
import math
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import time

# port for the server
hostName = "localhost"
serverPort = 8081

# empty queue which will store received data
producer_queue = []
consumer_queue = []

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

        global producer_queue
        global consumer_queue

        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()

        # receiving data via POST request from another server
        length = int(self.headers.get('Content-length', 0))
        data = json.loads(self.rfile.read(length).decode())

        # adding the received element to a queue
        if data['s'] == 1:
            producer_queue.append(data['int'])
        else:
            consumer_queue.append(data['int'])


# function which extracts the last element of the producer queue then sends it to the 3rd server
def extract_to_3():
    global producer_queue
    global headers
    global params

    while True:
        if len(producer_queue) > 0:
            last = producer_queue.pop()
            requests.post("http://localhost:8082", headers=headers, params=params, json={'int': math.sqrt(last)})
            time.sleep(3)
            print("PRODUCER QUEUE:", producer_queue)
        else:
            # continue
            time.sleep(3)

# function which extracts the last element of the consumer queue then sends it to the 1st server
def extract_to_1():
    global consumer_queue
    global headers
    global params

    while True:
        if len(consumer_queue) > 0:
            last = consumer_queue.pop()
            requests.post("http://localhost:8080", headers=headers, params=params, json={'int': last*10})
            time.sleep(3)
            print("CONSUMER QUEUE:", consumer_queue)
        else:
            # continue
            time.sleep(3)


# initializing 3 extractor threads to server 3, with function extract_to_3 as target
extractor_threads_to_3 = [threading.Thread(target=extract_to_3) for i in range(3)]

# initializing 3 extractor threads to server 1, with function extract_to_1 as target
extractor_threads_to_1 = [threading.Thread(target=extract_to_1) for i in range(3)]


# runner code
if __name__ == "__main__":

    # starting the threads
    for thread in extractor_threads_to_3:
        thread.start()

    for thread in extractor_threads_to_1:
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
