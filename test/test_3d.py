import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt

# 1. 加载借来的点云文件 (请替换为实际路径)
# 支持 .pcd 或 .ply 格式。如果是 .bin 需要转换，请告诉我。
pcd_path = "experimental materials/pointcloud_1.pcd"
print(f"正在读取点云: {pcd_path}")
pcd = o3d.io.read_point_cloud(pcd_path)
print(f"原始点云共有 {len(pcd.points)} 个点")

# 2. 体素下采样 (加快处理速度)
print("正在下采样...")
voxel_size = 0.05  # 体素大小，可根据你的场景调节
downpcd = pcd.voxel_down_sample(voxel_size=voxel_size)

# 3. 提取地面 (平面拟合)
print("正在识别并剔除地面...")
# distance_threshold: 点到平面的最大距离，用来判断点是否属于该平面
plane_model, inliers = downpcd.segment_plane(distance_threshold=0.02,
                                             ransac_n=3,
                                             num_iterations=1000)
# inlier_cloud 就是地面
inlier_cloud = downpcd.select_by_index(inliers)
inlier_cloud.paint_uniform_color([0.5, 0.5, 0.5]) # 地面涂成灰色

# outlier_cloud 就是去除了地面后的非地面障碍物
outlier_cloud = downpcd.select_by_index(inliers, invert=True)

# 4. 对非地面障碍物进行聚类分割 (区分不同的物体)
print("正在对障碍物聚类...")
# eps: 同一聚类中相邻点之间的最大距离
# min_points: 形成聚类的最少点数
with o3d.utility.VerbosityContextManager(
        o3d.utility.VerbosityLevel.Debug) as cm:
    labels = np.array(
        outlier_cloud.cluster_dbscan(eps=0.2, min_points=10, print_progress=True))

max_label = labels.max()
print(f"点云聚类完成，共发现 {max_label + 1} 个障碍物簇")

# 给不同的障碍物上不同的颜色
colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
colors[labels < 0] = 0 # 噪点涂黑
outlier_cloud.colors = o3d.utility.Vector3dVector(colors[:, :3])

# 5. 可视化结果
print("正在渲染三维结果...")
o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud],
                                  window_name="3D Scene Understanding",
                                  width=800, height=600)