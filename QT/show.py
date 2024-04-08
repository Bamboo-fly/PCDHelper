import sys
import time
from copy import deepcopy

import open3d as o3d
from PyQt5.QtWidgets import QInputDialog, QColorDialog, QApplication, QMainWindow, QWidget, QPushButton, QFileDialog, \
    QDialog, QVBoxLayout, QRadioButton, QLabel, QMessageBox, QDoubleSpinBox
from PyQt5.QtGui import QWindow, QIcon
import win32gui
from open3d.cpu.pybind import camera
from pyntcloud import PyntCloud


import third
import numpy as np
from open3 import displaySettings
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt  # 导入 Qt 模块


class MainWindow(QMainWindow):
    # 这里是类的构造函数，创建类的实例时做初始化工作
    # 这里的self作为实例对象本身，用于处理传入的参数
    # parent=none是传入的父实例，可以是none，也可以是其它值看需求
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        # 调用父类构造函数，确保父类的初始化工作顺利完成

        self.ui = third.Ui_MainWindow()
        # 使用引入的third类初始化UI界面，赋值给类的属性ui
        # 这里的ui属性没什么特别的，不是继承自父类，只是自己定义的一个属性
        self.ui.setupUi(self)
        self.setupActions()
        # 这行代码是菜单栏动作响应代码，修改这里就可以添加菜单栏动作

        # 设置窗口图标
        icon_path = 'C:\\Users\\Bamboo\\Desktop\\小米账号.png'  # 你的图标文件路径
        self.setWindowIcon(QIcon(icon_path))

        self.nowpath="C:\\Users\\Bamboo\\Desktop\\rabbit.pcd"
        # 这里初始化open3D的一个窗口，但是要设置关闭，它和要打开的qt窗口不是一个含义
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window(visible=False)  # visible=False窗口不显示，避免启动时一闪而过

        self.geometries = []  # 用于存储添加到可视化器中的几何体

        self.winid = win32gui.FindWindow('GLFW30', None)
        # 找到 Open3D 窗口的句柄，并将其存储在 self.winid 变量中
        self.sub_window = QWindow.fromWinId(self.winid)
        # 根据之前找到的 Open3D 窗口句柄，创建了一个对应的 QWindow 对象
        self.displayer = QWidget.createWindowContainer(self.sub_window)
        # 将之前创建的 QWindow 对象包装在一个 QWidget 内，准备将其嵌入到用户界面中显示
        self.ui.grid_display.addWidget(self.displayer)
        # 将包装好的 QWidget 添加到用户界面中的布局中，这样 Open3D 的窗口就能显示在 PyQt5 的界面上

        self.clock = QTimer(self)
        self.clock.timeout.connect(self.draw_update)
        # 没20毫秒触发一次更新渲染函数
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
        # 更新相机参数以确保窗口高度和宽度与相机参数匹配

    def draw_update(self):
        self.vis.poll_events()
        self.vis.update_renderer()


    def load_pcd_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "选择PCD文件", "", "PCD文件 (*.pcd)", options=options)
        if file_path:
            try:
                self.vis.clear_geometries()
                new_pcd = o3d.io.read_point_cloud(file_path)
                color = [1, 0, 0]  # 设置为红色
                if hasattr(new_pcd, 'points'):
                    new_pcd.paint_uniform_color(color)

                self.vis.add_geometry(new_pcd)
                self.vis.update_geometry(new_pcd)
                self.nowpath=file_path

            except Exception as e:
                print(f"发生异常：{e}")

    def save_pcd_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "保存PCD文件", "", "PCD文件 (*.pcd)", options=options)
        if file_path:
            try:
                pcd_to_save = o3d.geometry.PointCloud()
                for geometry in self.geometries:
                    if isinstance(geometry, o3d.geometry.PointCloud):
                        pcd_to_save += geometry

                o3d.io.write_point_cloud(file_path, pcd_to_save)
                print(f"文件成功保存至：{file_path}")
            except Exception as e:
                print(f"保存PCD文件时发生异常：{e}")
                print(f"文件路径：{file_path}")

    def turnoff(self):
        try:
            self.vis.clear_geometries()
            self.vis.destroy_window()
            self.vis = None
            self.sub_window.destroy()  # 显式销毁子窗口对象
            time.sleep(0.5)  # 添加适当的延迟
            self.close()
        except Exception as e:
            print(f"关闭窗口时发生异常：{e}")
            self.close()

    def render_direction_dialog(self):
        dialog = RenderDirectionDialog()
        if dialog.exec_() == QDialog.Accepted:
            selected_axis = dialog.selected_axis
            if selected_axis:
                self.update_point_cloud(selected_axis)

    def update_point_cloud(self, selected_axis):
        print(f"Selected Axis: {selected_axis}")  # 添加调试语句，检查选择的坐标轴

        if selected_axis == "X":
            new_pcd = o3d.io.read_point_cloud(self.nowpath)
            transformation = np.identity(4)
            transformation[0, 0] = -1  # Flip along X-axis
            new_pcd.transform(transformation)

            self.vis.clear_geometries()
            self.vis.add_geometry(new_pcd)
            self.vis.update_geometry(new_pcd)

        elif selected_axis == "Y":
            new_pcd = o3d.io.read_point_cloud(self.nowpath)
            transformation = np.identity(4)
            transformation[1, 1] = -1  # Flip along Y-axis
            new_pcd.transform(transformation)

            self.vis.clear_geometries()
            self.vis.add_geometry(new_pcd)
            self.vis.update_geometry(new_pcd)

        elif selected_axis == "Z":
            new_pcd = o3d.io.read_point_cloud(self.nowpath)
            transformation = np.identity(4)
            transformation[2, 2] = -1  # Flip along Z-axis
            new_pcd.transform(transformation)

            self.vis.clear_geometries()
            self.vis.add_geometry(new_pcd)
            self.vis.update_geometry(new_pcd)

    def change_point_cloud_color(self):
        try:
            if self.nowpath:
                color_dialog = QColorDialog.getColor()
                if color_dialog.isValid():
                    color = color_dialog.getRgbF()

                    new_pcd = o3d.io.read_point_cloud(self.nowpath)
                    if hasattr(new_pcd, 'points'):
                        new_color = [color[0], color[1], color[2]]  # 提取 RGB 值
                        new_pcd.paint_uniform_color(new_color)

                        self.vis.clear_geometries()
                        self.vis.add_geometry(new_pcd)
                        self.vis.update_geometry(new_pcd)

                        print("点云颜色已更新")  # 打印消息指示颜色已更新
                else:
                    print("未选择有效颜色")
            else:
                print("未指定点云文件路径，请先加载一个点云文件")
        except Exception as e:
            print(f"更改点云颜色时发生异常：{e}")

    def change_point_cloud_size(self):
        try:
            if self.nowpath:
                custom_dialog = CustomInputDialog(self)
                if custom_dialog.exec_():
                    size = custom_dialog.double_spinbox.value()

                    new_pcd = o3d.io.read_point_cloud(self.nowpath)
                    if hasattr(new_pcd, 'points'):
                        new_pcd.scale(size, center=new_pcd.get_center())
                        self.vis.clear_geometries()
                        self.vis.add_geometry(new_pcd)
                        self.vis.update_geometry(new_pcd)
                        print("点云大小已更新")  # 打印消息指示大小已更新
                else:
                    print("未设置有效的点云大小")
            else:
                print("未指定点云文件路径，请先加载一个点云文件")
        except Exception as e:
            print(f"更改点云大小时发生异常：{e}")

    #ISS关键点检测
    def process_and_visualize_point_cloud(self):
        try:
            dialog = ISSParametersDialog(self)
            if dialog.exec_():
                salient_radius = dialog.get_salient_radius()
                nms_radius = dialog.get_nms_radius()
                scale_ratio = dialog.get_scale_ratio()

                pcd_path = self.nowpath
                self.process_and_visualize_point_cloud_internal(pcd_path, salient_radius, nms_radius, gamma_21=0.975, gamma_32=0.975)

        except Exception as e:
            print(f"处理并可视化点云时发生异常：{e}")

    #ISS关键点检测
    def process_and_visualize_point_cloud_internal(self, pcd_path, radius=0.01, non_max_radius=0.005, gamma_21=0.975, gamma_32=0.975):
        self.vis.clear_geometries()
        point_cloud_o3d = o3d.io.read_point_cloud(pcd_path)

        def extract_iss_keypoints(point_cloud, radius, non_max_radius, gamma_21, gamma_32):
            keypoints = o3d.geometry.keypoint.compute_iss_keypoints(point_cloud,
                                                                    salient_radius=radius,
                                                                    non_max_radius=non_max_radius,
                                                                    gamma_21=gamma_21,
                                                                    gamma_32=gamma_32,
                                                                    min_neighbors=5)
            return keypoints

        keypoints = extract_iss_keypoints(point_cloud_o3d, radius, non_max_radius, gamma_21, gamma_32)

        num_keypoints = len(keypoints.points)
        print("关键点的数量：", num_keypoints)

        point_cloud_o3d.paint_uniform_color([1, 1, 0])  # 设置为黄色
        all_points_colors = np.full((len(point_cloud_o3d.points), 3), [1, 0, 0])  # 红色
        keypoints_array = np.asarray(keypoints.points)
        keypoints_indices = [np.where((np.asarray(point_cloud_o3d.points) == kp).all(axis=1))[0][0] for kp in keypoints_array]
        all_points_colors[keypoints_indices] = [0, 0, 0]  # 黑色
        point_cloud_o3d.colors = o3d.utility.Vector3dVector(all_points_colors)

        self.vis.add_geometry(point_cloud_o3d)
        self.vis.update_geometry(point_cloud_o3d)
        self.vis.poll_events()
        self.vis.run()

    #设置每个按键的动作函数
    def setupActions(self):
        action = self.ui.action
        action.triggered.connect(self.load_pcd_file)

        action_2 = self.ui.action_2
        action_2.triggered.connect(self.save_pcd_file)

        action_3 = self.ui.action_3
        action_3.triggered.connect(self.turnoff)

        action_4 = self.ui.action_4
        action_4.triggered.connect(lambda: displaySettings.modify_background_color(self))

        action_5 = self.ui.action_5
        action_5.triggered.connect(self.change_point_cloud_color)

        action_6 = self.ui.action_6
        action_6.triggered.connect(self.change_point_cloud_size)

        action_7 = self.ui.action_7
        action_7.triggered.connect(self.render_direction_dialog)

        actionISS = self.ui.actionISS
        actionISS.triggered.connect(self.process_and_visualize_point_cloud)

#调整渲染方向的界面类
class RenderDirectionDialog(QDialog):
    def __init__(self):
        super(RenderDirectionDialog, self).__init__()

        self.setWindowTitle("选择渲染方向")
        layout = QVBoxLayout()

        self.x_radio = QRadioButton("沿着 X 轴方向")
        self.y_radio = QRadioButton("沿着 Y 轴方向")
        self.z_radio = QRadioButton("沿着 Z 轴方向")

        layout.addWidget(QLabel("请选择渲染方向："))
        layout.addWidget(self.x_radio)
        layout.addWidget(self.y_radio)
        layout.addWidget(self.z_radio)

        self.ok_button = QPushButton("确定")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        font = QFont("Microsoft YaHei", 12)
        self.setStyleSheet("font-family: Microsoft YaHei; font-size: 12pt")
        self.setFont(font)
        self.resize(400, 200)

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def on_ok_clicked(self):
        selected_axis = ""
        if self.x_radio.isChecked():
            selected_axis = "X"
        elif self.y_radio.isChecked():
            selected_axis = "Y"
        elif self.z_radio.isChecked():
            selected_axis = "Z"

        if selected_axis:
            self.selected_axis = selected_axis
            self.accept()
        else:
            QMessageBox.warning(self, "警告", "请选择一个渲染方向！")

#调整点大小的界面类
class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super(CustomInputDialog, self).__init__(parent)

        self.setWindowTitle("修改点云大小")
        self.setFixedSize(300, 150)  # 设置对话框大小

        self.double_spinbox = QDoubleSpinBox()
        self.double_spinbox.setRange(0.1, 100.0)
        self.double_spinbox.setValue(1.0)

        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("请输入新的点云大小："))
        layout.addWidget(self.double_spinbox)
        layout.addWidget(ok_button)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setLayout(layout)

#实现ISS关键点提取的界面类
class ISSParametersDialog(QDialog):
    def __init__(self, parent=None):
        super(ISSParametersDialog, self).__init__(parent)

        self.setWindowTitle("设置ISS关键点提取参数")
        self.setFixedSize(450, 300)  # 设置对话框大小

        self.double_spinbox_salient_radius = QDoubleSpinBox()
        self.double_spinbox_salient_radius.setRange(0.001, 10.0)
        self.double_spinbox_salient_radius.setValue(0.008)
        self.double_spinbox_salient_radius.setDecimals(3)  # 设置小数位数为 4

        self.double_spinbox_nms_radius = QDoubleSpinBox()
        self.double_spinbox_nms_radius.setRange(0.001, 10.0)
        self.double_spinbox_nms_radius.setValue(0.007)
        self.double_spinbox_nms_radius.setDecimals(3)  # 设置小数位数为 4

        self.double_spinbox_scale_ratio = QDoubleSpinBox()
        self.double_spinbox_scale_ratio.setRange(0.001, 10.0)
        self.double_spinbox_scale_ratio.setValue(0.4)
        self.double_spinbox_scale_ratio.setDecimals(4)  # 设置小数位数为 4

        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("显著性半径："))
        layout.addWidget(self.double_spinbox_salient_radius)
        layout.addWidget(QLabel("非极大值抑制半径："))
        layout.addWidget(self.double_spinbox_nms_radius)
        layout.addWidget(QLabel("关键点尺度的比率："))
        layout.addWidget(self.double_spinbox_scale_ratio)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def get_salient_radius(self):
        return self.double_spinbox_salient_radius.value()

    def get_nms_radius(self):
        return self.double_spinbox_nms_radius.value()

    def get_scale_ratio(self):
        return self.double_spinbox_scale_ratio.value()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    def clean_up():
        global window
        if window:
            window.vis.clear_geometries()
            window.vis.destroy_window()
            window.vis = None
            window.sub_window.destroy()
            del window

    app.aboutToQuit.connect(clean_up)
    sys.exit(app.exec_())