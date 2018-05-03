#################################### python-http-middleman ####################################
# This is a simple python3 program that listens over HTTP for GET requests.
# When it gets a request it puts it into a queue for later processing.
# If the processing fails the request goes into a retry queue and tries again.
# SQLite databases are used to persist the queues.
# Secondary threads are used to handle the queues.
# It takes a queue entry, removes some of the JSON that we don't want.
# Only servers that are in the config file get requests forwarded to them.
# This setup seems to be pretty good at handling lots of connections coming in quickly.
# The request handler can take a while to catch up to tons of queued results, but it works.
###############################################################################################

# Requests get sent to: middleman.quade.co
# URL format: https://middleman.quade.co/{destination_domain}/{destination_path}
# Example old URL: https://sensorseed.quade.co/HomeOutsideWeatherStation/Data/Get?....
# Example new URL: https://middleman.quade.co/sensorseed.quade.co/HomeOutsideWeatherStation/Data/Get?....

from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import requests
import json
import queue
from threading import Thread
import fnmatch
import time
import math
from persistqueue import FIFOSQLiteQueue

class request_object:
    def __init__(self, command, path):
        self.command = command
        self.path = path

class retry_object:
    def __init__(self, request):
        self.request = request
        self.remaining_tries = 7
        self.last_run_time = time.time()

# FIFO queues
requestsQ = FIFOSQLiteQueue(path="./requestsQ", multithreading=True)
retryQ = FIFOSQLiteQueue(path="./retryQ", multithreading=True)

# Send a get request to a server address
def sendget(request):
    try:
        address = request.path.split("/")[1]
        path = request.path.replace("/" + address + "/", "/")
        print("http://" + address + path)
        r = requests.get("http://" + address + path)
        return r.status_code
    except:
        return '503'

# Handle the retry queue
def handleretries():
    while True:
        retry_data = retryQ.get()
        now = time.time()
        # Wait some time before retrying the request (factorial minutse of the number of tries that have been made: 1, 2, 6, 24, 120,...)
        if (now - retry_data.last_run_time) > (math.factorial(8 - retry_data.remaining_tries) * 60):
            print("Retrying to send request")
            status_code =  sendget(retry_data.request)
            # if the response isn't ok, decriment the retry count and requeue if there's a try left
            if int(status_code) != int('200'):
                retry_data.remaining_tries = retry_data.remaining_tries - 1
                print("Retry failed, tries left: " + str(retry_data.remaining_tries));
                retry_data.last_run_time = now
                if retry_data.remaining_tries > 0:
                    retryQ.put(retry_data)
        else:
            # Add back to end of queue if it isn't time yet
            # Always going through queue might not be the most efficient as the queue grows large, but it works
            retryQ.put(retry_data)

# Handle the HTTP requests in the queue by routing the requests where they need to go
def handlerequests():
    while True:
        request = requestsQ.get()
        with open('config.json', 'r') as configFile:
            config_json = json.load(configFile)
        for server_element in config_json['servers']:
            # Make sure the server is in the config file
            if fnmatch.fnmatch(server_element['address'], request.path.split("/")[1]):
                # send request, add to retry queue if fail
                status_code = sendget(request)
                print(status_code)
                if int(status_code) != int('200'):
                    print("Adding request to retry queue")
                    retryQ.put(retry_object(request))
                break

# Basic HTTP server class
class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    # Handle HTTP requests by putting them into a queue
    def do_POST(self):
        self._set_headers()
        self.wfile.write("wrong".encode("utf-8"))

    def do_GET(self):    
        requestsQ.put(request_object(self.command, self.path))
        print("queued request")        
        self._set_headers()
        self.wfile.write("ok".encode("utf-8"))

# Run the HTTP server on all addresses on a specific port
def runserver(server_class=HTTPServer, handler_class=S, port=8123):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting httpd...')
    httpd.serve_forever()

# main(): setup a second thread to handle the server request queue, and start the HTTP server
if __name__ == "__main__":
    from sys import argv

    requestworker = Thread(target=handlerequests)
    requestworker.setDaemon(True)
    requestworker.start()

    retryworker = Thread(target=handleretries)
    retryworker.setDaemon(True)
    retryworker.start()

    runserver()
