@echo off
chcp 65001
cd /d "%~dp0"
echo ========================================
echo 岗位管理表单功能测试
echo ========================================
echo.
echo [1] 运行新增功能测试
echo.
python 20260105_岗位管理_新增功能测试.py -v -s --tb=short
echo.
echo [2] 运行修改功能测试
echo.
python 20260105_岗位管理_修改功能测试.py -v -s --tb=short
echo.
echo [3] 运行删除功能测试
echo.
python 20260105_岗位管理_删除功能测试.py -v -s --tb=short
echo.
echo ========================================
echo 测试执行完成！
echo ========================================
echo.
echo 生成测试报告...
echo.
echo 查看汇总报告请打开：20260105_岗位管理_表单功能测试_汇总报告.md
echo.
pause