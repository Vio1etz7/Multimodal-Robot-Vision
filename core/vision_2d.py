import os
from transformers import pipeline
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.cm as cm
import numpy as np

# 1. 初始化模型（放在函数外部，这样启动服务器时只加载一次，不用每次请求都加载）
print("Loading SegFormer model...")
segmenter = pipeline("image-segmentation", model="nvidia/segformer-b0-finetuned-ade-512-512")
print("Model loaded successfully!")

def process_image(image_path: str) -> str:
    """
    接收原始图片路径，执行语义分割，并将结果图保存，返回结果图的相对路径。
    """
    # 读取图片
    image = Image.open(image_path)
    
    # 执行推理
    result = segmenter(image)
    
    # 准备画图：创建画布
    plt.figure(figsize=(10, 5))
    
    # 画底图
    plt.imshow(image)
    
    legend_patches = []
    colors = cm.get_cmap('tab20', len(result)) 
    
    # 叠加掩码
    for i, r in enumerate(result):
        label = r['label']
        mask_np = np.array(r['mask'])
        color_rgb = colors(i)[:3] 
        colored_mask = np.zeros((*mask_np.shape, 4))
        colored_mask[mask_np > 0] = list(color_rgb) + [0.5] 
        plt.imshow(colored_mask)
        legend_patches.append(mpatches.Patch(color=color_rgb, label=label))

    plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
    plt.axis('off')
    plt.tight_layout()
    
    # 生成输出路径 (存在 outputs 文件夹下)
    filename = os.path.basename(image_path)
    output_filename = f"result_{filename}"
    output_path = os.path.join("outputs", output_filename)
    
    # 保存成文件
    os.makedirs("outputs", exist_ok=True)  # 确保输出目录存在
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.close() # 释放内存
    
    return output_path