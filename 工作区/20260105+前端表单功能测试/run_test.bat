@echo off
chcp 65001 >nul
echo ===== 前端表单功能测试 =====
echo.
echo [1] 用户管理新增功能测试
python 工作区\20260105+前端表单功能测试\20260105_用户管理_新增功能测试.py
if %errorlevel% neq 0 (
    echo [ERROR] 新增功能测试失败
) else (
    echo [SUCCESS] 新增功能测试通过
)
echo.

echo [2] 用户管理修改功能测试
python 工作区\20260105+前端表单功能测试\20260105_用户管理_修改功能测试.py
if %errorlevel% neq 0 (
    echo [ERROR] 修改功能测试失败
) else (
    echo [SUCCESS] 修改功能测试通过
)
echo.

echo [3] 用户管理删除功能测试
python 工作区\20260105+前端表单功能测试\20260105_用户管理_删除功能测试.py
if %errorlevel% neq 0 (
    echo [ERROR] 删除功能测试失败
) else (
    echo [SUCCESS] 删除功能测试通过
)
echo.

echo ===== 所有测试已完成 =====
echo 请查看测试报告：工作区\20260105+前端表单功能测试\
pause