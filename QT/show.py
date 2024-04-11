import sys
import time

import open3d as o3d
from PyQt5.QtWidgets import QSpinBox, QColorDialog, QApplication, QMainWindow, QWidget, QPushButton, QFileDialog, \
    QDialog, QVBoxLayout, QRadioButton, QLabel, QMessageBox, QDoubleSpinBox
from PyQt5.QtGui import QWindow, QIcon
import win32gui

import third
import numpy as np
from open3 import displaySettings
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer, Qt  # 导入 Qt 模块

from sklearn.cluster import KMeans
from open3 import filtering,surfaceReconstruction

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

    def cleanup(self):
        # 清理资源、关闭窗口等操作
        if self.vis:
            self.vis.clear_geometries()
            self.vis.destroy_window()
            self.vis = None
        if self.sub_window:
            self.sub_window.destroy()
        # 可以添加其他需要的清理操作

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

        self.ui.textBrowser_2.append(f"关键点数量: {num_keypoints}")

        self.vis.add_geometry(point_cloud_o3d)
        self.vis.update_geometry(point_cloud_o3d)
        self.vis.poll_events()
        self.vis.run()

    #采用网格滤波的方法，KMeans聚类找到关键点
    def handle_sift_action(self):
        dialog = SIFTParametersDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            num_keypoints, num_clusters, random_state = dialog.get_parameters()

            if self.nowpath:
                try:
                    extracted_keypoints = self.extract_keypoints_from_point_cloud(self.nowpath,
                                                                                  num_keypoints=num_keypoints,
                                                                                  kmeans_n_clusters=num_clusters,
                                                                                  kmeans_random_state=random_state)
                    if extracted_keypoints is not None:
                        keypoints_array = np.asarray(extracted_keypoints)
                        print("提取的关键点：\n", keypoints_array)
                except Exception as e:
                    print(f"处理点云数据时发生异常：{e}")
            else:
                print("未指定点云文件路径，请先加载一个点云文件")

    #KMeans聚类
    def extract_keypoints_from_point_cloud(self, pcd_path, voxel_size=0.005, num_keypoints=100, kmeans_n_clusters=100,
                                           kmeans_init='k-means++', kmeans_random_state=None):
        # 读取点云文件
        point_cloud = o3d.io.read_point_cloud(pcd_path)

        # 下采样，使用体素网格滤波
        downsampled_pc = point_cloud.voxel_down_sample(voxel_size)

        # 检查点云数据是否为空
        if len(downsampled_pc.points) == 0:
            print("点云数据为空，请检查输入数据")
            return None

        # 将点云数据转换为 NumPy 数组
        pcd_points = np.asarray(downsampled_pc.points)

        # 使用 KMeans 算法找出聚类中心作为关键点
        kmeans = KMeans(n_clusters=kmeans_n_clusters, init=kmeans_init, random_state=kmeans_random_state).fit(
            pcd_points)
        keypoints = kmeans.cluster_centers_

        # 将所有非关键点设置为红色
        downsampled_pc.paint_uniform_color([1, 0, 0])  # 红色

        # 将关键点设置为黑色
        keypoint_pc = o3d.geometry.PointCloud()
        keypoint_pc.points = o3d.utility.Vector3dVector(keypoints)
        keypoint_pc.paint_uniform_color([0, 0, 0])  # 黑色

        self.ui.textBrowser_2.append(f"关键点数量: { len(keypoints)}")

        # 可视化点云和关键点
        self.vis.clear_geometries()
        self.vis.add_geometry(downsampled_pc)
        self.vis.add_geometry(keypoint_pc)
        self.vis.update_geometry(downsampled_pc)
        self.vis.update_geometry(keypoint_pc)

        return keypoints

    #MLS关键点测试
    def show_MLS_dialog(self):
        try:
            dialog = MLSParametersDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                # 获取 MLS 查询半径参数
                search_radius_value = dialog.get_search_radius_value()

                if self.nowpath:
                    try:
                        # 调用 MLS 处理方法，只传递 MLS 查询半径参数
                        processed_pcd = self.find_keypoints_using_mls(self.nowpath, search_radius=search_radius_value)
                        if processed_pcd is not None:
                            self.vis.clear_geometries()
                            self.vis.add_geometry(processed_pcd)
                            self.vis.update_geometry(processed_pcd)
                    except Exception as e:
                        print(f"处理点云数据时发生异常：{e}")
                else:
                    print("未指定点云文件路径，请先加载一个点云文件")
        except Exception as e:
            print(f"处理 MLS 参数窗口时发生异常: {e}")

    # 使用MLS方法寻找关键点
    # 使用MLS方法寻找关键点，不再包含eps参数
    def find_keypoints_using_mls(self, pcd_path, search_radius=0):
        print("开始处理点云数据...")

        point_cloud = o3d.io.read_point_cloud(pcd_path)
        mls_pcd = point_cloud.voxel_down_sample(voxel_size=search_radius)
        search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=search_radius, max_nn=999)
        mls_pcd.estimate_normals(search_param)

        print("开始执行 MLS 算法...")
        keypoints = mls_pcd.cluster_dbscan(eps=0.01, min_points=99, print_progress=False)

        if keypoints is not None:
            print(f"找到 {len(keypoints)} 个关键点")
        else:
            print("未找到关键点")

        self.ui.textBrowser_2.append(f"关键点数量: {len(keypoints)}")

        # 将关键点设置为黑色，非关键点设置为红色
        colors = np.array([[1, 0, 0] for _ in range(len(mls_pcd.points))])  # 设置所有点为红色
        colors[keypoints] = [0, 0, 0]  # 将关键点设置为黑色

        mls_pcd.colors = o3d.utility.Vector3dVector(colors)

        print("处理点云数据完成")
        return mls_pcd

    #实现滤波功能
    def apply_filter(self, filter_type):
        try:
            if self.nowpath:
                point_cloud = o3d.io.read_point_cloud(self.nowpath)

                if filter_type == 'voxel':
                    voxel_size = 0.005
                    point_cloud = filtering.voxel_filter(point_cloud, voxel_size)
                elif filter_type == 'statistical_outliers':
                    point_cloud = filtering.remove_statistical_outliers(point_cloud)
                elif filter_type == 'radius_outliers':
                    radius = 0.005
                    nb_points = 3
                    point_cloud = filtering.remove_radius_outliers(point_cloud, radius, nb_points)
                elif filter_type == 'pass_through':
                    axis = 2
                    min_bound = -0.03
                    max_bound = 0.03
                    point_cloud = filtering.pass_through_filter(point_cloud, axis, min_bound, max_bound)

                self.vis.clear_geometries()
                self.vis.add_geometry(point_cloud)
                self.vis.update_geometry(point_cloud)
            else:
                print("未指定点云文件路径，请先加载一个点云文件")
        except Exception as e:
            print(f"处理点云数据时发生异常：{e}")

    # 实现曲面重建功能
    def apply_surfacebuilding(self, building_type):
        try:
            if self.nowpath:
                point_cloud = o3d.io.read_point_cloud(self.nowpath)

                # 计算法向量
                point_cloud.estimate_normals()

                mesh = None
                if building_type == "poisson_reconstruction":
                    mesh = surfaceReconstruction.poisson_reconstruction(point_cloud)
                elif building_type == "alpha_shape_reconstruction":
                    alpha = 0.007
                    mesh = surfaceReconstruction.alpha_shape_reconstruction(point_cloud,alpha)
                elif building_type == "marching_cubes_reconstruction":
                    mesh = surfaceReconstruction.marching_cubes_reconstruction(point_cloud)
                elif building_type == "surface_reconstruction":
                    mesh = surfaceReconstruction.surface_reconstruction(point_cloud)

                if mesh:
                    self.vis.clear_geometries()
                    self.vis.add_geometry(mesh)
                    self.vis.update_geometry(mesh)

            else:
                print("未指定点云文件路径，请先加载一个点云文件")
        except Exception as e:
            print(f"处理点云数据时发生异常：{e}")

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

        actionSIFT = self.ui.actionSIFT
        actionSIFT.triggered.connect(self.handle_sift_action)

        actionHarris = self.ui.actionHarris
        actionHarris.triggered.connect(self.show_MLS_dialog)

        actionVoxel = self.ui.actionVoxel
        actionVoxel.triggered.connect(lambda: self.apply_filter('voxel'))

        action_8 = self.ui.action_8
        action_8.triggered.connect(lambda: self.apply_filter('statistical_outliers'))

        action_9 = self.ui.action_9
        action_9.triggered.connect(lambda: self.apply_filter('radius_outliers'))

        action_10 = self.ui.action_10
        action_10.triggered.connect(lambda: self.apply_filter('pass_through'))

        actionPoission = self.ui.actionPoission
        actionPoission.triggered.connect(lambda: self.apply_surfacebuilding('poisson_reconstruction'))

        action_11 = self.ui.action_11
        action_11.triggered.connect(lambda: self.apply_surfacebuilding('alpha_shape_reconstruction'))

        actionAlpha_Shape = self.ui.actionAlpha_Shape
        actionAlpha_Shape.triggered.connect(lambda: self.apply_surfacebuilding('marching_cubes_reconstruction'))

        actionMarching_Cubes = self.ui.actionMarching_Cubes
        actionMarching_Cubes.triggered.connect(lambda: self.apply_surfacebuilding('surface_reconstruction'))



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

#实现ISS关键点参数窗口类
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

#KMeans关键点参数窗口类
class SIFTParametersDialog(QDialog):
    def __init__(self, parent=None):
        super(SIFTParametersDialog, self).__init__(parent)

        self.setWindowTitle("设置关键点检测参数")
        self.resize(300, 150)

        self.num_keypoints_spinbox = QSpinBox()
        self.num_keypoints_spinbox.setRange(1, 1000)
        self.num_keypoints_spinbox.setValue(100)

        self.num_clusters_spinbox = QSpinBox()
        self.num_clusters_spinbox.setRange(1, 100)
        self.num_clusters_spinbox.setValue(50)

        self.random_state_spinbox = QSpinBox()
        self.random_state_spinbox.setRange(0, 1000)
        self.random_state_spinbox.setValue(0)

        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.accept)

        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("关键点数量："))
        layout.addWidget(self.num_keypoints_spinbox)
        layout.addWidget(QLabel("KMeans 簇的数量："))
        layout.addWidget(self.num_clusters_spinbox)
        layout.addWidget(QLabel("随机种子："))
        layout.addWidget(self.random_state_spinbox)
        layout.addWidget(confirm_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def get_parameters(self):
        num_keypoints = self.num_keypoints_spinbox.value()
        num_clusters = self.num_clusters_spinbox.value()
        random_state = self.random_state_spinbox.value()

        return num_keypoints, num_clusters, random_state

# MLS参数窗口类
class MLSParametersDialog(QDialog):
    def __init__(self, parent=None):
        super(MLSParametersDialog, self).__init__(parent)
        self.setWindowTitle("设置MLS参数")
        self.setFixedSize(450, 170)

        self.search_radius_spinbox = QDoubleSpinBox()
        self.search_radius_spinbox.setRange(0.0001, 1.0)
        self.search_radius_spinbox.setDecimals(3)  # 设置小数点精度为 4
        self.search_radius_spinbox.setValue(0.005)  # 设置为0.0050，四位小数的格式

        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("MLS 查询半径："))
        layout.addWidget(self.search_radius_spinbox)
        layout.addWidget(confirm_button)

        font = QFont("Microsoft YaHei", 12)
        self.setStyleSheet("font-family: Microsoft YaHei; font-size: 12pt")
        self.setFont(font)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setLayout(layout)

    def get_search_radius_value(self):
        return self.search_radius_spinbox.value()

    def reject(self):
        self.done(QDialog.Rejected)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    #清理并释放相关资源
    app.aboutToQuit.connect(window.cleanup)
    sys.exit(app.exec_())