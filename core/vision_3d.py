import os
import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

def process_pointcloud(pcd_path: str) -> str:
    """
    处理 3D 点云，并将其渲染结果截图保存。
    """
    pcd = o3d.io.read_point_cloud(pcd_path)
    
    # 1. 降采样与地面分割
    voxel_size = 0.05
    downpcd = pcd.voxel_down_sample(voxel_size=voxel_size)
    plane_model, inliers = downpcd.segment_plane(distance_threshold=0.02,
                                                 ransac_n=3,
                                                 num_iterations=1000)
    inlier_cloud = downpcd.select_by_index(inliers)
    inlier_cloud.paint_uniform_color([0.5, 0.5, 0.5]) # 地面灰色
    
    outlier_cloud = downpcd.select_by_index(inliers, invert=True)
    
    # 2. DBSCAN 聚类
    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Error) as cm:
        labels = np.array(outlier_cloud.cluster_dbscan(eps=0.2, min_points=10, print_progress=False))
    
    max_label = labels.max()
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0 # 噪点黑色
    outlier_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])
    
    # 3. 离线渲染截图 (不弹窗)
    # 生成输出路径
    filename = os.path.basename(pcd_path)
    output_filename = f"result_{filename}.png" # 强制存为 png 截图
    output_path = os.path.join("outputs", output_filename)
    
    vis = o3d.visualization.Visualizer()
    vis.create_window(visible=False, width=800, height=600) # 关键：隐藏窗口
    vis.add_geometry(inlier_cloud)
    vis.add_geometry(outlier_cloud)
    
    # 获取视角控制并稍微调整一下角度让截图更好看
    ctr = vis.get_view_control()
    ctr.set_front([0.5, 0.5, 0.5])
    ctr.set_lookat([0, 0, 0])
    ctr.set_up([0, 0, 1])
    
    vis.poll_events()
    vis.update_renderer()
    vis.capture_screen_image(output_path) # 截图保存
    vis.destroy_window()
    
    return output_path