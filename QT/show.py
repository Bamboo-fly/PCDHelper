import sys
import open3d as o3d
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QFileDialog
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import QTimer
import win32gui
import third
import numpy as np


class MainWindow(QMainWindow):

    #这里是类的构造函数，创建类的实例时做初始化工作
    #这里的self作为实例对象本身，用于处理传入的参数
    #parent=none是传入的父实例，可以是none，也可以是其它值看需求
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        #调用父类构造函数，确保父类的初始化工作顺利完成

        self.ui = third.Ui_MainWindow()
        #使用引入的third类初始化UI界面，赋值给类的属性ui
        #这里的ui属性没什么特别的，不是继承自父类，只是自己定义的一个属性
        self.ui.setupUi(self)

        #这里初始化open3D的一个窗口，但是要设置关闭，它和要打开的qt窗口不是一个含义
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=False)  # visible=False窗口不显示，避免启动时一闪而过

        self.geometries = []  # 用于存储添加到可视化器中的几何体

        self.winid = win32gui.FindWindow('GLFW30', None)
        #找到 Open3D 窗口的句柄，并将其存储在 self.winid 变量中
        self.sub_window = QWindow.fromWinId(self.winid)
        #根据之前找到的 Open3D 窗口句柄，创建了一个对应的 QWindow 对象
        self.displayer = QWidget.createWindowContainer(self.sub_window)
        #将之前创建的 QWindow 对象包装在一个 QWidget 内，准备将其嵌入到用户界面中显示
        self.ui.grid_display.addWidget(self.displayer)
        #将包装好的 QWidget 添加到用户界面中的布局中，这样 Open3D 的窗口就能显示在 PyQt5 的界面上

        self.load_button = QPushButton("选取点云文件", self)
        self.load_button.clicked.connect(self.load_pcd_file)
        self.ui.grid_display.addWidget(self.load_button)

        self.save_button = QPushButton("保存点云文件", self)
        self.save_button.clicked.connect(self.save_pcd_file)
        self.ui.grid_display.addWidget(self.save_button)

        self.clock = QTimer(self)
        self.clock.timeout.connect(self.draw_update)
        #没20毫秒触发一次更新渲染函数
        self.clock.start(20)
        self.draw_test()

    def draw_test(self):
        # 添加几何体时同时将其添加到 self.geometries 列表中
        pcd = o3d.io.read_point_cloud(r'C:\Users\Bamboo\Desktop\rabbit.pcd')
        self.vis.add_geometry(pcd)
        self.geometries.append(pcd)

        # 计算点云的尺寸、密度和异常点数量
        num_points = len(np.asarray(pcd.points))
        size_info = pcd.get_max_bound() - pcd.get_min_bound()
        density = num_points / np.prod(size_info)
        cl, ind = pcd.remove_statistical_outlier(nb_neighbors=20, std_ratio=2.0)
        num_outliers = len(ind)

        # 使用另一种方法来计算曲率信息
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
            lines = pcd.compute_mahalanobis_distance()
            avg_curvature = np.mean(lines)

        # 更新 textBrowser_2 控件显示点云信息
        self.ui.textBrowser.append(f"点云尺寸信息: {size_info}")
        self.ui.textBrowser.append(f"点云密度: {density}")
        self.ui.textBrowser.append(f"异常点数量: {num_outliers}")
        self.ui.textBrowser.append(f"平均曲率: {avg_curvature}")

        # 更新 textBrowser_2 控件显示点云数据的个数和点云文件的个数
        num_data_points = len(np.asarray(pcd.points))
        num_files = len(self.geometries)
        self.ui.textBrowser_2.append(f"加载的点云数据个数: {num_data_points}\n点云文件个数: {num_files}")



    def draw_update(self):
        self.vis.poll_events()
        self.vis.update_renderer()

    #加载点云数据的函数
    def load_pcd_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Choose PCD File", "", "PCD Files (*.pcd)", options=options)
        if file_path:
            try:
                self.vis.clear_geometries()  # 清除当前显示的几何体
                new_pcd = o3d.io.read_point_cloud(file_path)

                # 统一设置点云颜色
                color = [1, 0, 0]  # 设置为红色
                if hasattr(new_pcd, 'points'):
                    new_pcd.paint_uniform_color(color)

                self.vis.add_geometry(new_pcd)
                self.vis.update_geometry(new_pcd)

            except Exception as e:
                print(f"An exception occurred: {e}")

    #保存点云数据的函数
    def save_pcd_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PCD File", "", "PCD Files (*.pcd)", options=options)
        if file_path:
            try:
                pcd_to_save = o3d.geometry.PointCloud()
                for geometry in self.geometries:
                    if isinstance(geometry, o3d.geometry.PointCloud):
                        pcd_to_save += geometry

                o3d.io.write_point_cloud(file_path, pcd_to_save)
                print(f"File saved successfully to: {file_path}")
            except Exception as e:
                print(f"An exception occurred while saving PCD file: {e}")
                print(f"File path: {file_path}")

    def __del__(self):
        self.vis.destroy_window()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())