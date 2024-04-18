import os
import sys
import socket

import open3d as o3d
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QVBoxLayout, QWidget, QApplication, QLabel
from PyQt5.QtGui import QIcon, QWindow
from PyQt5.QtCore import QTimer, Qt
import win32gui
from pointnet.pointnet import Ui_MainWindow
import numpy as np

class PointnetWindow(QMainWindow):
    def __init__(self, parent=None):
        super(PointnetWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.point_cloud = None
        self.setWindowTitle("Main Pointnet Window")

        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=False)

        self.geometries = []

        self.winid = win32gui.FindWindow('GLFW30', None)
        self.sub_window = QWidget.createWindowContainer(QWindow.fromWinId(self.winid))
        self.ui.gridLayout.addWidget(self.sub_window)

        self.clock = QTimer(self)
        self.clock.timeout.connect(self.draw_update)
        self.clock.start(20)

        self.ui.actionpcd_pts.triggered.connect(self.load_pcdtotxt)
        self.ui.actionpts_pcd.triggered.connect(self.load_txttopcd)
        self.ui.pushButton_2.clicked.connect(self.select_txt_file)

        # 添加一个标签用于显示结果
        self.result_label = QLabel("                                   分类结果:")
        self.result_label.setFixedSize(2000, 70)  # 设置标签的宽度为 200 像素，高度为 50 像素
        self.ui.gridLayout.addWidget(self.result_label)

    def draw_update(self):
        self.vis.poll_events()
        self.vis.update_renderer()

    def load_pcdtotxt(self):
        options = QFileDialog.Options()
        pcd_path, _ = QFileDialog.getOpenFileName(self, "Select PCD file", "", "PCD files (*.pcd)", options=options)
        if pcd_path:
            self.update_point_cloud(pcd_path)
            self.draw_point_cloud()

            # Select a txt file
            txt_path, _ = QFileDialog.getSaveFileName(self, "Select TXT file", "", "TXT files (*.txt)", options=options)
            if txt_path:
                self.send_txt_content(txt_path)

    def load_txttopcd(self):
        options = QFileDialog.Options()
        txt_path, _ = QFileDialog.getOpenFileName(self, "Select TXT file", "", "TXT files (*.txt)", options=options)

        if txt_path:
            points = []
            with open(txt_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    data = line.strip().split(',')
                    if len(data) != 6:
                        print("Error: Data format is incorrect.")
                        return

                    point = list(map(float, data))
                    points.append(point)

            pcd_path, _ = QFileDialog.getSaveFileName(self, "Save PCD file", "", "PCD files (*.pcd)", options=options)
            if pcd_path:
                try:
                    pcd = o3d.geometry.PointCloud()
                    pcd.points = o3d.utility.Vector3dVector(np.array(points)[:, :3])
                    o3d.io.write_point_cloud(pcd_path, pcd)
                    print(f"PCD file saved successfully at: {pcd_path}")
                    self.update_point_cloud(pcd_path)
                    self.draw_point_cloud()
                except Exception as e:
                    print(f"Error saving PCD file: {e}")

    def send_txt_content(self, file_path):
        if self.point_cloud:
            points = np.asarray(self.point_cloud.points)
            if points.shape[1] < 6:
                num_points_to_add = 6 - points.shape[1]
                points = np.hstack((points, np.zeros((points.shape[0], num_points_to_add))))  # 添加缺失的括号

                with open(file_path, 'w') as f:
                    for i in range(points.shape[0]):
                        f.write(
                            f"{points[i][0]:.6f},{points[i][1]:.6f},{points[i][2]:.6f},{points[i][3]:.6f},{points[i][4]:.6f},{points[i][5]:.6f}\n")
                print("Conversion completed. Data saved to", file_path)  # 调整缩进，保持在 with 语句块内

    def update_point_cloud(self, file_path):
        if self.point_cloud:
            self.vis.remove_geometry(self.point_cloud)
        self.point_cloud = o3d.io.read_point_cloud(file_path)

    def draw_point_cloud(self):
        self.vis.add_geometry(self.point_cloud)

    def select_txt_file(self):
        global txt_path
        options = QFileDialog.Options()
        txt_path, _ = QFileDialog.getOpenFileName(self, "Select TXT file", "", "Text files (*.txt)", options=options)
        print("Selected TXT file path:", txt_path)

        if txt_path:
            if os.path.exists(txt_path):
                with open(txt_path, 'r') as file:
                    txt_data = file.readlines()

                    for line in txt_data:
                        if len(line.strip().split(',')) != 6:
                            print("Error: Data format is incorrect.")
                            return

                    server_ip = "192.168.43.27"  # 服务器 IP 地址
                    server_port = 2345  # 服务器端口
                    try:
                        self.send_data_to_server(server_ip, server_port, txt_data)
                    except socket.error as e:
                        print(f"Socket Error: {e}")
            else:
                print("Error: File does not exist.")

    def update_result_label(self, result):
        self.result_label.setText(f"                                   分类结果:{result}")

    def send_data_to_server(self, server_ip, server_port, data):
        print("Connecting to server...")
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Server IP: {server_ip}, Port: {server_port}")
            client_socket.connect((server_ip, server_port))
            print("Successfully connected to server!")

            line_count = 0
            for line in data:
                client_socket.sendall(line.encode())
                line_count += 1

            # 发送特殊标记表示数据传输结束
            special_marker = "###END_OF_TRANSMISSION###\n"  # 添加换行符
            client_socket.sendall(special_marker.encode())

            print("Data sent to server successfully!")

            # 接收服务端的返回信息
            response = client_socket.recv(1024)  # 接收1024字节的数据
            print("Received response from server:", response.decode())

            # 在界面上更新显示结果的标签
            self.update_result_label(response.decode())

        except ConnectionRefusedError as e:
            print(f"Connection refused: {e}")
        except TimeoutError as e:
            print(f"Timeout error: {e}")
        except OSError as e:
            print(f"OS error: {e}")
        except Exception as e:
            print(f"Error connecting or sending data to server: {e}")
        finally:
            client_socket.close()

    def cleanup(self):
        if self.vis:
            self.vis.destroy_window()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pointnet_window = PointnetWindow()
    pointnet_window.show()
    app.aboutToQuit.connect(pointnet_window.cleanup)
    sys.exit(app.exec_())