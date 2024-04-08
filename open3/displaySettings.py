import open3d as o3d
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtCore import QMetaObject

def load_point_cloud_from_file(file_path):
    # 使用open3d加载.pcd文件
    cloud = o3d.io.read_point_cloud(file_path)
    return cloud

def centerize_point_cloud(point_cloud):
    # 将点云数据转换为numpy数组
    points = np.asarray(point_cloud.points)
    # 计算点云数据的中心坐标
    center = np.mean(points, axis=0)
    # 点云中心化处理
    centered_points = points - center
    return centered_points, center

def visualize_point_cloud(point_cloud):
    # 创建 Visualizer
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    # 获取默认相机参数
    params = vis.get_view_control().convert_to_pinhole_camera_parameters()
    # 将点云添加到Visualizer
    vis.add_geometry(point_cloud)
    # 运行Visualizer
    vis.run()
    # 关闭Visualizer
    vis.destroy_window()

def modify_background_color(window):
    color_dialog = QColorDialog(window)
    color = color_dialog.getColor()

    if color.isValid():
        QTimer.singleShot(0, lambda: _apply_color(window, color))

def _apply_color(window, color):
    try:
        rgb_color = np.array([color.redF(), color.greenF(), color.blueF()]) # 仅保留RGB颜色值，不包含透明度
        rgb_color = rgb_color.astype(np.float64).reshape(3, 1) # 转换为float64类型的2D数组
        window.vis.get_render_option().background_color = rgb_color
        window.vis.update_renderer()
    except Exception as e:
        print(f"Error in _apply_color: {e}")

