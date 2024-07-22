import socket
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import UDPServer, BaseRequestHandler
from urllib.parse import parse_qs
from pymongo import MongoClient
from multiprocessing import Process


mongo_client = MongoClient("mongodb://mongo:27017/")
db = mongo_client.messages_db
messages_collection = db.messages


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("templates/index.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/message.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("templates/message.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/style.css":
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()
            with open("static/style.css", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/logo.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("static/logo.png", "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("templates/error.html", "rb") as file:
                self.wfile.write(file.read())

    def do_POST(self):
        if self.path == "/message":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            post_data = parse_qs(post_data.decode("utf-8"))
            username = post_data["username"][0]
            message = post_data["message"][0]
            data = {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "username": username,
                "message": message,
            }
            send_to_socket_server(data)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()


def send_to_socket_server(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(data).encode(), ("localhost", 5000))


class SocketHandler(BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        message = json.loads(data.decode())
        messages_collection.insert_one(message)


def run_http_server():
    httpd = HTTPServer(("0.0.0.0", 3000), SimpleHTTPRequestHandler)
    httpd.serve_forever()


def run_socket_server():
    udp_server = UDPServer(("0.0.0.0", 5000), SocketHandler)
    udp_server.serve_forever()


if __name__ == "__main__":
    http_server_process = Process(target=run_http_server)
    socket_server_process = Process(target=run_socket_server)

    http_server_process.start()
    socket_server_process.start()

    http_server_process.join()
    socket_server_process.join()
