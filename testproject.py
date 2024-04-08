import open3d as o3d
import numpy as np

def process_and_visualize_point_cloud(pcd_path, radius=0.01, non_max_radius=0.005, gamma_21=0.975, gamma_32=0.975):
    # 加载点云文件
    point_cloud_o3d = o3d.io.read_point_cloud(pcd_path)

    def extract_iss_keypoints(point_cloud, radius, non_max_radius, gamma_21, gamma_32):
        keypoints = o3d.geometry.keypoint.compute_iss_keypoints(point_cloud,
                                                                salient_radius=radius,
                                                                non_max_radius=non_max_radius,
                                                                gamma_21=gamma_21,
                                                                gamma_32=gamma_32,
                                                                min_neighbors=5)
        return keypoints

    # 提取关键点
    keypoints = extract_iss_keypoints(point_cloud_o3d, radius, non_max_radius, gamma_21, gamma_32)

    # 输出关键点的数量
    num_keypoints = len(keypoints.points)
    print("关键点的数量：", num_keypoints)

    # 设置点云颜色
    point_cloud_o3d.paint_uniform_color([1, 1, 0])  # 设置点云颜色为黄色
    all_points_colors = np.full((len(point_cloud_o3d.points), 3), [1, 0, 0])  # 红色
    keypoints_array = np.asarray(keypoints.points)
    keypoints_indices = [np.where((np.asarray(point_cloud_o3d.points) == kp).all(axis=1))[0][0] for kp in keypoints_array]
    all_points_colors[keypoints_indices] = [0, 0, 0]  # 黑色
    point_cloud_o3d.colors = o3d.utility.Vector3dVector(all_points_colors)

    # 可视化结果
    o3d.visualization.draw_geometries([point_cloud_o3d])

# 调用函数以处理和可视化点云数据
pcd_path = "C:/Users/Bamboo/Desktop/rabbit.pcd"  # 替换为您自己的PCD文件路径
process_and_visualize_point_cloud(pcd_path)