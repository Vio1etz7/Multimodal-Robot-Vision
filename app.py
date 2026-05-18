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

# 挂载静态文件夹（前端页面）和输出文件夹（用来在网页上显示图片）
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.post("/api/analyze/2d")
async def analyze_2d(file: UploadFile = File(...)):
    print(f"接收到文件: {file.filename}")
    
    # 1. 把上传的图片存到 data 目录下
    file_location = f"data/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. 调用刚才写好的算法进行处理
    print("开始执行 2D 语义分割...")
    result_path = process_image(file_location)
    
    # 3. 把生成的图片 URL 返回给前端
    # 如果 result_path 是 "outputs/result_001.jpg"
    # 我们加上 "/" 变成 "/outputs/result_001.jpg" 方便前端直接使用 <img src="...">
    return {
        "status": "success", 
        "message": "处理完成", 
        "result_url": f"/{result_path}"
    }

@app.post("/api/analyze/3d")
async def analyze_3d(file: UploadFile = File(...)):
    print(f"接收到 3D 文件: {file.filename}")
    
    file_location = f"data/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    print("开始执行 3D 语义分割...")
    result_path = process_pointcloud(file_location)
    
    return {
        "status": "success", 
        "result_url": f"/{result_path}"
    }

if __name__ == "__main__":
    print("服务器启动中: http://localhost:8000/static/index.html")
    uvicorn.run(app, host="0.0.0.0", port=8000)