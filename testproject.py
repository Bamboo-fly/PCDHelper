import open3d as o3d
import numpy as np

# 读取PCD文件
pcd_path = r"C:\Users\Bamboo\Desktop\rabbit.pcd"
point_cloud = o3d.io.read_point_cloud(pcd_path)
points = np.asarray(point_cloud.points)  # 提取点云数据

# 处理点云数据，确保每行有六列数据
if points.shape[1] < 6:
    num_points_to_add = 6 - points.shape[1]
    points = np.hstack((points, np.zeros((points.shape[0], num_points_to_add))))

# 创建ModelNet40 Normal Resampled数据集格式
output_path = r"C:\Users\Bamboo\Desktop\rabbit_M.pcd"
num_points = points.shape[0]
with open(output_path, 'w') as f:
    # 写入点云数据
    for i in range(num_points):
        f.write(f"{points[i][0]:.6f},{points[i][1]:.6f},{points[i][2]:.6f},{points[i][3]:.6f},{points[i][4]:.6f},{points[i][5]:.6f}\n")
    # 添加类别标签，这里假设类别为0
    f.write("0\n")

print("Conversion completed. Data saved to", output_path)