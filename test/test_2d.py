from transformers import pipeline
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# 1. 加载轻量级预训练模型 (第一次运行会自动下载，需要稍等片刻)
# 使用专门针对城市景观/室内场景训练的模型
print("正在加载模型...")
segmenter = pipeline("image-segmentation", model="nvidia/segformer-b0-finetuned-ade-512-512")
print("模型加载完成！")

# 2. 读取一张你们借来的图片 (请替换为实际的图片路径)
# 例如: image_path = "camera/0001.jpg"
image_path = "experimental materials/20260411164655.jpg" 
image = Image.open(image_path)

# 3. 执行推理
print("正在执行图像分割推理...")
result = segmenter(image)

# 4. 简单可视化结果
# 取出模型的预测掩码并叠加上去
plt.figure(figsize=(10, 5))

# 显示原图
plt.subplot(1, 2, 1)
plt.imshow(image)
plt.title("Original Image")
plt.axis('off')

# 显示分割结果
# --- 替换原来的 2D 显示代码 ---
plt.subplot(1, 2, 2)
plt.imshow(image) # 先画底图

import matplotlib.patches as mpatches
import matplotlib.cm as cm

legend_patches = []
# 为每个类别分配不同的颜色
colors = cm.get_cmap('tab20', len(result)) 

for i, r in enumerate(result):
    label = r['label']
    mask_np = np.array(r['mask'])
    
    # 提取颜色的 RGB 值
    color_rgb = colors(i)[:3] 
    
    # 创建一个带有透明度的彩色图层
    colored_mask = np.zeros((*mask_np.shape, 4))
    # 将模型预测为该类别的位置，涂上颜色和 50% 的透明度
    colored_mask[mask_np > 0] = list(color_rgb) + [0.5] 
    
    plt.imshow(colored_mask)
    # 记录图例
    legend_patches.append(mpatches.Patch(color=color_rgb, label=label))

plt.legend(handles=legend_patches, bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.title("Semantic Segmentation")
plt.axis('off')
plt.tight_layout()
plt.show()
print("2D 测试完成！")