import open3d as o3d
import numpy as np
def calculate_normals(point_cloud, radius):
    # 估计点云的法线
    point_cloud.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=radius, max_nn=30))
    return point_cloud

def surface_reconstruction(point_cloud):
    # 进行曲面重建
    distances = point_cloud.compute_nearest_neighbor_distance()
    avg_dist = np.mean(distances)
    radius = 3 * avg_dist
    mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(point_cloud, o3d.utility.DoubleVector([radius, radius * 2]))
    return mesh

def poisson_reconstruction(point_cloud):
    poisson_mesh, densities = o3d.geometry.TriangleMesh.\
        create_from_point_cloud_poisson(point_cloud, depth=9, width=0, scale=1.1, linear_fit=False)
    return poisson_mesh

def alpha_shape_reconstruction(point_cloud, alpha):
    alpha_shape = o3d.geometry.TriangleMesh.create_from_point_cloud_alpha_shape(point_cloud, alpha)
    return alpha_shape

# Marching Cubes 曲面重建
def marching_cubes_reconstruction(point_cloud, iso_level=0.5):
    mesh, densities = o3d.geometry.TriangleMesh.\
        create_from_point_cloud_poisson(point_cloud, depth=9, width=0, scale=1.1, linear_fit=False)
    mesh.compute_vertex_normals()
    mesh.filter_smooth_laplacian(1)
    mesh.filter_smooth_taubin(1, 0.8)
    return mesh

 #计算点云的法向量，才能进行下一步的重建
    # cloud = surfaceReconstruction.calculate_normals(cloud, radius=0.01)

    # 进行曲面重建
    #mesh = surface_reconstruction(cloud)

    # 进行 Poisson 曲面重建
    # poisson_mesh = poisson_reconstruction(cloud)

    # 进行 Alpha Shape 曲面重建
    # alpha = 0.007
    # alpha_shape = surfaceReconstruction.alpha_shape_reconstruction(cloud, alpha)

    # 进行 Marching Cubes 曲面重建
    #marching_cubes_mesh = marching_cubes_reconstruction(cloud)