import os
import open3d as o3d
import numpy as np

def process_pointcloud(pcd_path: str) -> str:
    """
    处理 3D 点云，运行 RANSAC 和 DBSCAN，并将带有颜色标签的点云保存为 .ply 文件返回。
    """
   
    pcd = o3d.io.read_point_cloud(pcd_path)
    
    
    voxel_size = 0.06
    downpcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    
   
    plane_model, inliers = downpcd.segment_plane(distance_threshold=0.03,
                                                 ransac_n=3,
                                                 num_iterations=1000)
    inlier_cloud = downpcd.select_by_index(inliers)
    
    inlier_cloud.paint_uniform_color([0.3, 0.3, 0.3]) 
    
    outlier_cloud = downpcd.select_by_index(inliers, invert=True)
    
    
    labels = np.array(outlier_cloud.cluster_dbscan(eps=0.25, min_points=8, print_progress=False))
    
    
    max_label = labels.max()
    if max_label >= 0:
        import matplotlib.pyplot as plt
        colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
        colors[labels < 0] = 0 
        outlier_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])
    
    
    annotated_cloud = inlier_cloud + outlier_cloud
    
    filename = os.path.basename(pcd_path)
    base_name = os.path.splitext(filename)[0]

    pcd_filename = f"annotated_{base_name}.pcd"
    pcd_output_path = os.path.join("outputs", pcd_filename)
    o3d.io.write_point_cloud(pcd_output_path, annotated_cloud)

    # 替换后缀名为 .ply
    output_filename = f"parsed_{os.path.splitext(filename)[0]}.ply"
    output_path = os.path.join("outputs", output_filename)
    
    
    o3d.io.write_point_cloud(output_path, annotated_cloud, write_ascii=False)
    
    
    return output_path