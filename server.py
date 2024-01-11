"""
HTTP Server Shell
Author: Barak Gonen and Nir Dweck
Purpose: Provide a basis for Ex. 4
Note: The code is written in a simple way, without classes, log files or
other utilities, for educational purpose
Usage: Fill the missing functions and constants
Filled by: Bar Assulin
"""

import socket
import re
import logging

# Constants
WEB_ROOT = "C:/cyber/cyber4n/webroot"  # Adjust this to your web document root
DEFAULT_URL = "/index.html"

QUEUE_LEN = 1
IP = '0.0.0.0'
PORT = 8080
SOCKET_TIMEOUT = 2
REDIRECTION_DICTIONARY = {"/moved": "/"}

LOG_FORMAT = '%(levelname)s | %(asctime)s | %(processName)s | %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + '/server.log'


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file992/ data in a string
    """
    data = None
    try:
        file_path = WEB_ROOT + file_name
        with open(file_path, "rb") as file:
            data = file.read()
    except Exception as err:
        logging.error("received error: " + str(err))
    finally:
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
    http_response = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"
    http_response = http_response.encode()
    if uri in REDIRECTION_DICTIONARY:
        uri = REDIRECTION_DICTIONARY[uri]
        http_response = f"HTTP/1.1 302 Found\r\nLocation: {uri}\r\n\r\n".encode()
    if uri == "/forbidden":
        http_response = "HTTP/1.1 403 forbidden\r\nContent-Length: 0\r\n\r\n"
        http_response = http_response.encode()
    elif uri == "/error":
        http_response = "HTTP/1.1 500 ERROR SERVER INTERNAL\r\nContent-Length: 0\r\n\r\n"
        http_response = http_response.encode()
    else:
        file_type = uri.split(".")[-1]
        if (file_type == "html" or file_type == "jpg" or file_type == "gif" or file_type == "css" or file_type == "js"
                or file_type == "txt" or file_type == "ico" or file_type == "png"):
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
                http_header = (f"HTTP/1.1 200 OK\r\nContent-Type: text/javascript;charset=UTF-8\r\nContent-Length: "
                               f"{leng}\r\n\r\n")
            elif file_type == "txt":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "ico":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\nContent-Length: {leng}\r\n\r\n"
            elif file_type == "png":
                http_header = f"HTTP/1.1 200 OK\r\nContent-Type: image/png\r\nContent-Length: {leng}\r\n\r\n"
            else:
                http_header = "HTTP/1.1 500 ERROR SERVER INTERNAL\r\nContent-Length: 0\r\n\r\n"
                data = None
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
        try:
            client_request = client_socket.recv(1024).decode()
            while '\r\n\r\n' not in client_request:
                client_request = client_request + client_socket.recv(1).decode()
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
                break
        except Exception as err:  # Catch any unexpected errors
            logging.error("Error handling client request: " + str(err))
            break  # Close the connection to prevent further issues

    print('Closing connection')


def main():
    # Open a socket and loop forever while waiting for clients
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print("Listening for connections on port %d" % PORT)
        my_socket.bind((IP, PORT))
        my_socket.listen(QUEUE_LEN)
        while True:
            client_socket, client_address = my_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                logging.error("received socket error on client socket" + str(err))
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        logging.error("received socket error on server socket" + str(err))
        print('received socket exception - ' + str(err))
    finally:
        my_socket.close()


if __name__ == "__main__":
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)

    valid_request = "GET /index.html HTTP/1.1"
    assert validate_http_request(valid_request) == (True, "/index.html")

    invalid_request = "INVALID_REQUEST"
    assert validate_http_request(invalid_request) == (False, None)
    # Call the main handler function
    main()
