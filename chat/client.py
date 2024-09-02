import socket
import sys

def start_client():
    # IP주소와 Port번호 입력 에러 처리
    if len(sys.argv) != 3:
        print("사용법: client <IP주소> <PORT>")
        sys.exit(1)

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    print(f"Connecting to {HOST}:{PORT} ...", end=" ")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            print("Success!")

            while True:
                message = input("chat> ")
                if message.lower() == "quit":
                    print("Bye!")
                    break
                client_socket.sendall(message.encode())
                response = client_socket.recv(1024)
                print(f"Server: {response.decode()}")
    except Exception as e:
        print(f"연결 실패: {e}")

if __name__ == "__main__":
    start_client()