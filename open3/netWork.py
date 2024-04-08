import socket

def net_work():
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