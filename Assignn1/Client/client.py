import argparse
import ntpath
import os
from glob import glob
from socket import AF_INET, SOCK_STREAM, socket

BUFFER = 4096
FORMAT = 'utf-8'
PORT = 5000


def path_leaf(path):
    """
    Returns a file name from a path
    :param path: string (path)
    :return:
    """
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def send_file_info(sock, file):
    """
    Sends the filename and file size to server
    :param sock: a socket object
    :param file: string (path)
    :return:
    """
    stat = float(os.stat(file).st_size)
    msg1 = f"{path_leaf(file)}\n{stat}\n"
    print(f"\n[SENDING] Sending file {path_leaf(file)} information.")
    sock.send(msg1.encode(FORMAT))


def send_file(sock, file):
    """
    Sends the file to the server
    :param sock: a socket object
    :param file: string (path)
    :return:
    """
    print(f"\n[SENDING] Sending {path_leaf(file)} data.")
    f = open(file, 'rb')
    while True:
        data = f.read()
        if not data:
            break
        sock.send(data)
    f.close()


def handle_connection(sock, files):
    """
    Handles the connection with server
    :param sock: a socket object
    :param files: string (path)
    :return:
    """
    for filename in files:
        send_file_info(sock, filename)
        print(f"[SERVER MSG] " + sock.recv(BUFFER).decode(FORMAT))
        send_file(sock, filename)
        print(f"[SERVER MSG] " + sock.recv(BUFFER).decode(FORMAT))
    print(f"\n[DISCONNECTING] disconnecting from {sock.getpeername()}.")
    sock.close()


def main():
    parser = argparse.ArgumentParser()

    # -s Server IP (required), -p Server port\
    parser.add_argument("-s", "--server_ip", dest="server_ip", default=0, help="Server IP", required=True)
    parser.add_argument("-p", "--port", dest="port", default=PORT, help="Server Port", type=int)
    parser.add_argument("files", nargs='+')
    args = parser.parse_args()

    flist = []
    for i in args.files:
        if '*' in i:
            print(f"[SENDING] '*' detected: Extension provided{os.path.splitext(i)[1]}")
            flist += glob(i)
        else:
            flist.append(i)
    args.files = flist
    socket_obj = socket(AF_INET, SOCK_STREAM)
    socket_obj.connect((args.server_ip, args.port))
    print(f"\n[CONNECTED] connected to {socket_obj.getpeername()}")
    handle_connection(socket_obj, args.files)


if __name__ == '__main__':
    main()
