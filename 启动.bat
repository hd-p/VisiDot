@echo off
chcp 65001 >nul
REM 色卡识别工具 - 一键启动
REM 双击本文件即可启动本地服务并自动打开浏览器；关闭本窗口即停止服务并回收资源。

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    py serve.py
    goto :done
)

where python >nul 2>nul
if %errorlevel%==0 (
    python serve.py
    goto :done
)

echo [错误] 未找到 Python，请先安装 Python 3。
pause
exit /b 1

:done
echo.
echo 服务已停止。
