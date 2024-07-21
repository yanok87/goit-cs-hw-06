import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import socket
import threading
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

HTTPServerPort = 3000


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self, data):
        save_data(data)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def start_web_server():
    server_address = ("localhost", 3000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Serving on port 3000...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
        print("Shutdown server")


# MONGODB
def save_data(data):
    client = MongoClient(uri, server_api=ServerApi("1"))
    db = client.book
    data_parse = urllib.parse.unquote_plus(data.decode())

    result_one = db.messages.insert_one(
        {
            "date": datetime.now(),
            "username": 3,
            "message": ["ходить в капці", "дає себе гладити", "рудий"],
        }
    )


# SOCKET
UDP_IP = "127.0.0.1"
UDP_PORT = 5000


# Підключення до сервера
def run_socket_server(ip, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = ip, port
    client.bind(server)
    try:
        while True:
            data, address = client.recvfrom(1024)
            print(f"Received data: {data.decode()} from {address}")

    except KeyboardInterrupt:
        print("Close server")

    finally:
        client.close()


if __name__ == "__main__":

    # Запуск потоків для прослуховування та письма
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=run_socket_server(UDP_IP, UDP_PORT))
    write_thread.start()

    receive_thread.join()
    write_thread.join()
