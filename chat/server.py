#!/usr/bin/env python3

import socket
import sys
import threading


clients = []
stop_event = threading.Event()
server_socket = None

def start_server():
    global server_socket
    if len(sys.argv) != 2:
        print("사용법: server <PORT>")
        sys.exit(1)

    PORT = int(sys.argv[1])
    HOST = '0.0.0.0'

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    exit_thread = threading.Thread(target=listen_for_exit, daemon=True)
    exit_thread.start()

    while not stop_event.is_set():
        try:
            client_socket, client_addr = server_socket.accept()
            client_thread = threading.Thread(target=handle_clients, args=(client_socket, client_addr))
            client_thread.start()
            print(f"Waiting for connection...", end=" ")
        except OSError:
            break

def handle_clients(client_socket, client_addr):
    print(f"Connected! from")
    print(f"{client_addr[0]}:{client_addr[1]}")
    clients.append(client_socket)
    print(f"[접속자] {clients}")

    while not stop_event.is_set():
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                print("서버가 정상적으로 종료됨")
            if not message or message.lower() == "quit":
                print(f"클라이언트: {client_addr[0]}:{client_addr[1]}에서 접속을 종료")
                break
            print(f"{client_addr[0]}: {message}")

        except (ConnectionResetError, ConnectionAbortedError):
            print(f"[ERROR] {client_addr[0]}:{client_addr[1]} 강제종료.")
        except OSError:
            print(f"[ERROR] {client_addr[0]}:{client_addr[1]} 소켓이 닫힘")
        finally:
            clients.remove(client_socket)
            print(f"[접속자] {clients}")
            client_socket.close()

def listen_for_exit():
    global server_socket
    while True:
        command = input().strip().lower()
        if command == "quit":
            print("서버 종료 단계 시작")

            for client in clients:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                stop_event.set()
                client.close()

            if server_socket is not None:
                server_socket.close()
            break


if __name__ == "__main__":
    start_server()