import socket

HOST = '0.0.0.0'
PORT = 1234


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Waiting for connection...")

        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"클라이언트 {client_addr} 연결 완료")
            client_socket.sendall(b"wellcome \n")
            client_socket.close()

if __name__ == "__main__":
    start_server()