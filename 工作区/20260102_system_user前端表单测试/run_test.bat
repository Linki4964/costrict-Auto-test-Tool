@echo off
chcp 65001
echo ========================================
echo 用户管理-新增功能测试脚本
echo ========================================
echo.
echo 测试开始时间: %date% %time%
echo.

cd %~dp0
pytest 20260102_用户管理_新增功能测试脚本_v1.py -v --tb=short --html=report.html --self-contained-html

echo.
echo 测试结束时间: %date% %time%
echo ========================================
echo.
pause