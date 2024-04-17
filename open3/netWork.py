import socket
import time


def net_work_serce():
      HOST = '192.168.43.27'  # 服务器IP地址
      PORT = 8088  # 服务器端口号

      def receive_and_print_string(conn):
          print(f"Receiving and saving data...")
          with conn, conn.makefile('rb') as f:
              with open('E:\\bisheenvironment\\PythonProject\\pythonProject\\lidardata.pcd', 'w') as output_file:
                  while True:
                      print(f"")
                      data = f.readline().decode('latin1').strip()
                      if not data:
                          break  # No more data to receive
                      output_file.write(data + '\n')
                      print(f"Received string: {data}")

      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.bind((HOST, PORT))
          s.listen()
          print('服务器已启动...')
          conn, addr = s.accept()
          print('已连接到客户端：', addr)
          receive_and_print_string(conn)

import socket

def send_file(host, port, file_path):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # Send each line as a message
            client_socket.sendall(line.encode("utf-8"))

    # Send an empty message to indicate end of file
    client_socket.sendall(b"")

    # Close the socket
    client_socket.close()

if __name__ == "__main__":
    send_file("192.168.43.27", 12345, r"E:\bisheenvironment\PythonProject\Pointnet_Pointnet2_pytorch-master\Pointnet_Pointnet2_pytorch-master\data\modelnet40_normal_resampled\bed\bed_0005.txt")
