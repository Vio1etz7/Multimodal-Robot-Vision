import os
import sys
import shutil
import glob

# 确保脚本能正确导入同级目录下的算法
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.vision_2d import process_image
from core.vision_3d import process_pointcloud

# ==================== 1. 路径定义 ====================
# 输入的原始数据路径
RAW_CAMERA_DIR = os.path.join("..", "..","raw_data", "camera")
RAW_LIDAR_DIR = os.path.join("..", "..","raw_data", "lidar")

# 输出的提交归档路径
SUBMIT_2D_DIR = os.path.join("..", "..", "标注文件", "视频_图像标注")
SUBMIT_3D_DIR = os.path.join("..", "..", "标注文件", "点云标注")

# ==================== 2. 初始化环境 ====================
os.makedirs(SUBMIT_2D_DIR, exist_ok=True)
os.makedirs(SUBMIT_3D_DIR, exist_ok=True)

def batch_process_2d():
    print("\n==============================================")
    print("▶ 阶段一：开始批量生成 2D 图像语义分割标注...")
    print("==============================================")
    
    # 查找所有图片格式
    extensions = ("*.jpg", "*.jpeg", "*.png")
    image_paths = []
    for ext in extensions:
        image_paths.extend(glob.glob(os.path.join(RAW_CAMERA_DIR, ext)))
    
    total = len(image_paths)
    if total == 0:
        print("❌ 未在 raw_data/camera/ 中检测到任何图像文件，跳过 2D 处理。")
        return
        
    print(f"检测到 {total} 张原始图像，开始神经网络推理...")
    
    for idx, img_path in enumerate(image_paths, 1):
        filename = os.path.basename(img_path)
        print(f"[{idx}/{total}] 正在处理: {filename} ... ", end="", flush=True)
        
        try:
            
            output_path, _ = process_image(img_path)
            
            
            final_dest = os.path.join(SUBMIT_2D_DIR, os.path.basename(output_path))
            shutil.copyfile(output_path, final_dest)
            print("✅ 成功并成功归档")
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

def batch_process_3d():
    print("\n==============================================")
    print("▶ 阶段二：开始批量生成 3D 点云空间解析标注...")
    print("==============================================")
    
    pcd_paths = sorted(glob.glob(os.path.join(RAW_LIDAR_DIR, "*.pcd")))
    total_raw = len(pcd_paths)
    
    if total_raw == 0:
        print("❌ 未在 raw_data/lidar/ 中检测到任何 .pcd 点云文件，跳过 3D 处理。")
        return
    
   
    sampled_pcd_paths = pcd_paths[::10]
    total_sampled = len(sampled_pcd_paths)
    
    print(f"原始点云共 {total_raw} 帧。已启用 10:1 时序抽帧，实际需处理 {total_sampled} 帧。")
    print("开始执行 RANSAC 地面分割与 DBSCAN 聚类...")
    
    for idx, pcd_path in enumerate(sampled_pcd_paths, 1):
        filename = os.path.basename(pcd_path)
        print(f"[{idx}/{total_sampled}] 正在解析点云: {filename} ... ", end="", flush=True)
        
        try:
            
            output_ply_path = process_pointcloud(pcd_path)
            
           
            pcd_filename = f"annotated_{os.path.splitext(filename)[0]}.pcd"
            real_pcd_output = os.path.join("outputs", pcd_filename)
            
            if os.path.exists(real_pcd_output):
                final_dest = os.path.join(SUBMIT_3D_DIR, pcd_filename)
                shutil.copyfile(real_pcd_output, final_dest)
                print("✅ 成功生成 3D .pcd 标注文件")
            else:
                print("⚠️ 输出了 PLY，但未找到对应的归档 PCD 文件")
                
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

if __name__ == "__main__":
    print(" 机器狗多模态数据批量 Auto-Labeling 引擎启动...")
    batch_process_2d()
    batch_process_3d()
    print("\n 所有数据批量跑图结束！")