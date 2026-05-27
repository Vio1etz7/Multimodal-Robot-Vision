import os
import gc  
from transformers import pipeline
from PIL import Image
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

print("Loading SegFormer model...")
segmenter = pipeline("image-segmentation", model="nvidia/segformer-b0-finetuned-ade-512-512")
print("Model loaded successfully!")

def process_image(image_path: str):
    """
    处理 2D 图像，返回 (原始图保存路径, 结果图保存路径, 带有颜色信息的标签列表)
    """
    image = Image.open(image_path)
    result = segmenter(image)

    # 保存原始图像
    filename = os.path.basename(image_path)
    original_filename = f"original_{filename}"
    original_path = os.path.join("outputs", original_filename)
    image.save(original_path)

    img_w, img_h = image.size
    dpi = 100
    fig, ax = plt.subplots(figsize=(img_w / dpi, img_h / dpi), dpi=dpi)

    ax.imshow(image)
    ax.axis('off')
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    detected_targets = []
    seen_labels = set()

    colors = cm.get_cmap('tab20', len(result))

    for i, r in enumerate(result):
        label = r['label']
        mask_np = np.array(r['mask'])
        color_rgb = colors(i)[:3]

        hex_color = '#%02x%02x%02x' % (int(color_rgb[0]*255), int(color_rgb[1]*255), int(color_rgb[2]*255))

        if label not in seen_labels:
            seen_labels.add(label)
            detected_targets.append({
                "name": label,
                "color": hex_color
            })

        # 🌟 关键优化：指定 dtype=np.float32。1080p大图的内存占用直接砍掉 50%
        colored_mask = np.zeros((*mask_np.shape, 4), dtype=np.float32)
        colored_mask[mask_np > 0] = list(color_rgb) + [0.4]
        ax.imshow(colored_mask)

    output_filename = f"parsed_{filename}"
    output_path = os.path.join("outputs", output_filename)

    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)


    fig.clf()
    plt.close(fig)
    plt.close('all')


    del image, result, fig, ax, colored_mask, mask_np
    gc.collect()

    return original_path, output_path, detected_targets