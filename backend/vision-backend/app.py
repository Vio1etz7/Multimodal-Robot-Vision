from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil
from core.vision_2d import process_image
from core.vision_3d import process_pointcloud

# 确保文件夹存在
os.makedirs("data", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

app = FastAPI()

# 只挂载输出文件夹（用来在网页上显示图片）
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.post("/api/analyze/2d")
async def analyze_2d(file: UploadFile = File(...)):
    print(f"[2D Pipeline] 接收到图像: {file.filename}")
    file_location = f"data/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 接收路径和目标对象
    result_path, targets = process_image(file_location)
    
    return {
        "status": "success", 
        "result_url": f"/{result_path}",
        "targets": targets  # 🌟 结构为: [{"name": "wall", "color": "#1f77b4"}, ...]
    }

@app.post("/api/analyze/3d")
async def analyze_3d(file: UploadFile = File(...)):
    print(f"[3D Pipeline]接收到点云: {file.filename}")
    
    file_location = f"data/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    
    result_path = process_pointcloud(file_location)
    
    return {
        "status": "success", 
        "result_url": f"/{result_path}"
    }

if __name__ == "__main__":
    print("服务器启动中: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)