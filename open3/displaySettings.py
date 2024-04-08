import open3d as o3d
import numpy as np



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