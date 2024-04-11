import open3d as o3d

def find_keypoints_using_mls(pcd_path, search_radius=0.1):
    # 读取点云文件
    point_cloud = o3d.io.read_point_cloud(pcd_path)

    # 进行 MLS 曲面重建
    mls_pcd = point_cloud.voxel_down_sample(voxel_size=0.005)
    search_param = o3d.geometry.KDTreeSearchParamHybrid(radius=search_radius, max_nn=30)  # 添加 max_nn 参数
    mls_pcd.estimate_normals(search_param)

    # 找出关键点
    keypoints = mls_pcd.detect_keypoints(o3d.geometry.Feature.Normal, search_param)

    # 将关键点设置为蓝色，非关键点设置为红色
    colors = [[1, 0, 0] for _ in range(len(mls_pcd.points))]  # 非关键点设置为红色
    for key_index in keypoints:
        colors[key_index] = [0, 0, 1]  # 关键点设置为蓝色
    mls_pcd.colors = o3d.utility.Vector3dVector(colors)

    return mls_pcd

# 示例用法
pcd_path = "C:\\Users\\Bamboo\\Desktop\\rabbit.pcd"  # 替换为您的 PCD 文件路径
search_radius = 0.1  # MLS 查询半径
processed_pcd = find_keypoints_using_mls(pcd_path, search_radius)

# 展示处理后的点云文件
o3d.visualization.draw_geometries([processed_pcd], window_name='MLS Key Points')