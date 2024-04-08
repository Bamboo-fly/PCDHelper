import open3d as o3d

#这里放置进行点云滤波的函数
def voxel_filter(point_cloud, voxel_size):
    # 使用Voxel滤波对点云数据进行降采样
    downsampled_cloud = point_cloud.voxel_down_sample(voxel_size=voxel_size)
    return downsampled_cloud

def remove_statistical_outliers(point_cloud, nb_points=20, std_ratio=2.0):
    #Statistical Outlier Removal（统计异常值去除）
    cl, ind = point_cloud.remove_statistical_outlier(nb_neighbors=nb_points, std_ratio=std_ratio)
    return cl

def remove_radius_outliers(point_cloud, radius, nb_points):
    #半径异常值去除
    cl, ind = point_cloud.remove_radius_outlier(nb_points=nb_points, radius=radius)
    return cl

def pass_through_filter(point_cloud, axis, min_bound, max_bound):
    #通道滤波
    cl = point_cloud.crop(
        o3d.geometry.AxisAlignedBoundingBox(min_bound=[-100, -100, min_bound],
                                            max_bound=[100, 100, max_bound]))
    return cl

    # #添加voxel滤波并进行降采样处理
    # voxel_size = 0.005    #Voxel 滤波器的滤波尺寸,代表了每个体素的边长
    # cloud = voxel_filter(cloud, voxel_size)
    # print("Voxel滤波后点云中的点数：", len(cloud.points))
    #
    # # 添加 Statistical Outlier Removal 操作
    # cloud = remove_statistical_outliers(cloud)
    # print("Statistical Outlier Removal后点云中的点数：", len(cloud.points))
    #
    # # 添加 Radius Outlier Removal 操作
    # radius = 0.005
    # #radius: 这是用于确定半径范围的参数
    # nb_points = 3
    # #nb_points: 这是指定在给定半径范围内用于判断点是否为异常值的邻近点的最小数量
    # cloud = remove_radius_outliers(cloud, radius, nb_points)
    # print("Radius Outlier Removal后点云中的点数：", len(cloud.points))
    #
    # # 添加 PassThrough Filter 操作
    # axis = 2
    # #操作沿着的轴 0：表示沿x轴进行过滤操作。 1：表示沿y轴进行过滤操作。 2：表示沿z轴进行过滤操作。
    # min_bound = -0.03
    # max_bound = 0.03
    # #cloud = pass_through_filter(cloud, axis, min_bound, max_bound)
    # print("PassThrough Filter后点云中的点数：", len(cloud.points))