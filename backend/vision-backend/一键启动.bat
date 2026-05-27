@echo off
chcp 65001
cls
echo ====================================================
echo  宇树机器狗视觉认知系统 - 一键启动程序 
echo ====================================================
echo.
echo 正在检查并补全运行环境，请稍候...
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

echo.
echo 环境就绪！正在拉起核心引擎...
echo.
echo ====================================================
echo  [成功] 系统已启动！
echo  请保持此终端打开，并在浏览器中访问以下地址：
echo  http://127.0.0.1:8000
echo ====================================================
echo.
python app.py
pause