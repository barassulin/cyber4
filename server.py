"""
HTTP Server Shell
Author: Barak Gonen and Nir Dweck
Purpose: Provide a basis for Ex. 4
Note: The code is written in a simple way, without classes, log files or
other utilities, for educational purpose
Usage: Fill the missing functions and constants
"""

import os
import socket
import re
import logging

# Constants
WEB_ROOT = "C:/cyber/cyber4n/webroot"  # Adjust this to your web document root
DEFAULT_URL = "/index.htmll"

QUEUE_LEN = 1
IP = '0.0.0.0'
PORT = 8080
SOCKET_TIMEOUT = 2
REDIRECTION_DICTIONARY = {"/moved": DEFAULT_URL}

LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """
    file_path = WEB_ROOT + file_name
    with open(file_path, "rb") as file:
        data = file.read()
    return data


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    if resource == '/':
        uri = DEFAULT_URL
    else:
        uri = resource
    http_response = "HTTP/1.1 404 Not Found\r\n\r\n"
    http_response=http_response.encode()
    if uri in REDIRECTION_DICTIONARY:
        new_uri = REDIRECTION_DICTIONARY[uri]
        http_response = f"HTTP/1.1 302 Found\r\nLocation:{new_uri}\r\n\r\n".encode()

    elif uri == "/forbidden":
        http_response = "HTTP/1.1 403 forbidden\r\n\r\n"
        http_response = http_response.encode()
    elif uri == "/error":
        http_response = "HTTP/1.1 500 ERROR SERVER INTERNAL\r\n\r\n"
        http_response=http_response.encode()
    else:
        file_type = uri.split(".")[-1]
        if file_type == "html" or file_type =="jpg" or file_type =="gif" or file_type =="css" or file_type =="js" or file_type =="txt" or file_type =="ico" or file_type =="png":
            data = get_file_data(uri)
            leng = len(data)
            if file_type == "html":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "jpg":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == 'gif':
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "css":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/css\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "js":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/javascript;charset=UTF-8\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "txt":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "ico":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "png":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: {leng}\r\n\r\n"
            http_response = http_header.encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    pattern = r"^GET (.*) HTTP/1.1"
    mch = re.search(pattern, request)
    if mch:
        req_url = mch.group(1)
        return True, req_url
    return False, None


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        client_request = client_socket.recv(1024).decode()
        logging.debug("getting client request " + client_request)
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
        else:
            http_header = "HTTP/1.1 400 Request Bad\r\n\r\n"
            client_socket.send(http_header.encode())
            logging.debug("sending response" + http_header)
            print('Error: Not a valid HTTP request')
            #break
    print('Closing connection')
    """,
        "/forbidden": "FORBIDDEN .403",
        "/error": "500 ERROR SERVER INTERNAL",
        400: "400 REQUEST BAD" - get valid
        404: "404 FOUND NOT" - uri
    """

def main():
     my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     try:
         my_socket.bind((IP, PORT))
         my_socket.listen(QUEUE_LEN)
         while True:
            client_socket, client_address = my_socket.accept()
            handle_client(client_socket)

     except socket.error as err:
         """logging.error("received socket error on server socket" + str(err))"""
         print('received socket error on server socket' + str(err))

     finally:
         my_socket.close()

if __name__ == "__main__":
     main()
