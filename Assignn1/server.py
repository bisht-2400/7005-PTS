import argparse
import os
from socket import *


BUFFER = 4096
FORMAT = 'utf-8'
PORT = 5000


def socket_setup(port):
    """
    This function takes in a port number and sets up a socket object
    :param port: an int
    :return: a socket object
    """
    socket_object = socket(AF_INET, SOCK_STREAM)
    socket_object.bind((get_ip_address(), int(port)))
    return socket_object


def get_ip_address():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def make_unique(directory, file):
    """
    make_unique takes in a directory and a file the returns a unique filename
    :param directory: string (path)
    :param file: string (path)
    :return: string (path)
    """
    not_unique = os.path.exists(directory + '/' + file)
    count = 1
    filename, extension = os.path.splitext(file)
    print(f"\n[RECEIVING] Receiving File: Name: {file}")
    while not_unique:
        print(f"[FILE EXISTS] Making another version of {file}.")
        file = filename + "V" + str(count) + extension
        not_unique = os.path.exists(directory + '/' + file)
        count += 1
    print(f"[FILENAME] Filename on server: {file}.")
    return file


def get_file(sock, directory):
    """
    Receives a file from the sock connection
    :param sock: a socket object
    :param directory: string (path)
    """
    msg1 = sock.recv(BUFFER).decode(FORMAT)
    while msg1:
        file = msg1.split('\n', 1)
        sock.send(b'File information received')
        file_name = make_unique(directory, file[0])
        file_size = float(file[1])
        recv_file(sock, file_name, file_size, directory)
        msg1 = sock.recv(BUFFER).decode(FORMAT)


def recv_file(sock, filename, filesize, directory):
    """
    Receives the file from the socket
    :param sock: string (path)
    :param filename: string (path)
    :param filesize: string (path)
    :param directory: string (path)
    :return:
    """
    f = open(directory + '/' + filename, 'wb')
    size_recv = 0.0
    while True:
        data = sock.recv(BUFFER)
        size_recv += BUFFER
        if size_recv >= filesize:
            f.write(data)
            break
        f.write(data)
    sock.send(b'File Received')
    f.close()


def make_dir(directory, ip):
    """
    Makes a directory with the ip
    :param directory: string (path)
    :param ip: ip of the client
    :return:
    """
    directory = directory + '/' + ip
    os.makedirs(directory, exist_ok=True)
    return directory


def handle_connection(conn, addr, directory):
    """
    Handles the connection with the client
    :param conn: a socket object
    :param addr: tuple
    :param directory: string (path)
    :return:
    """
    print(f"\n[NEW CONNECTION] {addr} established.")
    directory = make_dir(directory, addr[0])
    get_file(conn, directory)
    conn.close()
    print(f"\n[DISCONNECTING] disconnected from {addr}\n{'-' * 100}")


def main():
    parser = argparse.ArgumentParser()

    # -d Root Directory -p Server Port
    parser.add_argument("-d", "--directory", dest="dir", default="recv_files", help="Path to Dir")
    parser.add_argument("-p", "--port", dest="port", default=PORT, help="Server Port")

    args = parser.parse_args()

    print(f"\n[STARTING] server is starting  port: {args.port},  dir: {args.dir},  ip: {get_ip_address()}")
    socket_obj = socket_setup(args.port)

    socket_obj.listen(5)

    while True:
        print(f"\n[LISTENING] server is listening on {get_ip_address()}")
        conn, addr = socket_obj.accept()
        handle_connection(conn, addr, args.dir)


if __name__ == '__main__':
    main()
