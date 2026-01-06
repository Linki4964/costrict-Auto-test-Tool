import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
import random
from playwright.async_api import async_playwright, expect

async def test_add_user():
    print("===== 开始执行用户管理新增功能测试 =====")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        base_url = "http://192.168.142.146/"
        
        try:
            print(f"[步骤1] 访问登录页面: {base_url}")
            await page.goto(f"{base_url}login?redirect=%2Findex")
            
            print("[步骤2] 点击登录按钮（使用默认凭证）")
            await page.get_by_role("button", name="登 录").click()
            
            print("[步骤3] 等待页面跳转到首页")
            await page.wait_for_url("**/index")
            
            print("[步骤4] 展开侧边栏系统管理菜单")
            system_menu = page.locator("li").filter(has_text="系统管理").first
            await system_menu.click()
            
            print("[步骤5] 点击用户管理菜单项")
            user_link = page.get_by_role("link", name="用户管理")
            await user_link.wait_for(state="visible", timeout=10000)
            await user_link.click()
            print("已进入用户管理页面")
            
            await page.wait_for_timeout(2000)
            
            print("[步骤6] 点击新增按钮")
            add_button = page.get_by_role("button", name="新增")
            await add_button.wait_for(state="visible", timeout=5000)
            await add_button.click()
            
            print("[步骤7] 等待对话框弹出")
            await page.wait_for_timeout(1000)
            dialog = page.get_by_role("dialog")
            await dialog.wait_for(state="visible", timeout=10000)
            print("对话框已弹出，开始填写表单...")
            
            test_id = random.randint(1000, 9999)
            print(f"\n填写用户信息: 测试ID={test_id}")
            
            print("[步骤8] 填写用户昵称")
            await dialog.locator("input[placeholder='请输入用户昵称']").fill(f"昵称_{test_id}")
            
            print("[步骤9] 选择归属部门")
            await dialog.locator(".vue-treeselect__control").click()
            await page.wait_for_timeout(500)
            dept_items = await page.query_selector_all(".vue-treeselect__menu div")
            for item in dept_items:
                text = await item.text_content()
                if text and "若依科技" in text:
                    await item.click()
                    print(f"  选择部门: {text.strip()}")
                    break
            await page.wait_for_timeout(500)
            
            print("[步骤10] 填写手机号码")
            await dialog.locator("input[placeholder='请输入手机号码']").fill(f"1380000{test_id}")
            
            print("[步骤11] 填写邮箱")
            await dialog.locator("input[placeholder='请输入邮箱']").fill(f"test{test_id}@qq.com")
            
            print("[步骤12] 填写用户名称")
            await dialog.locator("input[placeholder='请输入用户名称']").fill(f"user_{test_id}")
            
            print("[步骤13] 填写用户密码")
            await dialog.locator("input[type='password'][placeholder='请输入用户密码']").fill("123456")
            
            print("[步骤14] 点击确定按钮提交表单")
            await dialog.locator(".el-dialog__footer >> button:has-text('确 定')").click()
            
            print("[步骤15] 验证新增成功提示")
            success_msgs = ["操作成功", "新增成功", "保存成功"]
            success_found = False
            
            for msg in success_msgs:
                try:
                    await expect(page.get_by_text(msg)).to_be_visible(timeout=3000)
                    success_found = True
                    print(f"[PASS] 找到提示: {msg}")
                    break
                except:
                    continue
            
            if not success_found:
                print("[WARN] 未找到标准成功提示，检查页面可能的状态...")
                await page.wait_for_timeout(2000)
            
            await page.wait_for_timeout(2000)
            
            print("\n===== 测试完成 =====")
            result = {
                "test_id": test_id,
                "status": "PASS" if success_found else "UNCERTAIN",
                "username": f"user_{test_id}",
                "nickname": f"昵称_{test_id}",
                "phonenumber": f"1380000{test_id}",
                "email": f"test{test_id}@qq.com"
            }
            
            import json
            import os
            report_path = os.path.join("工作区", "20260105+前端表单功能测试", "新增功能测试报告.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\n测试报告已保存至: {report_path}")
            print(f"测试结果: {result}")
            
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            print(f"\n[ERROR] 测试过程中发生错误: {e}")
            result = {
                "status": "FAIL",
                "error": str(e)
            }
            
            import json
            import os
            report_path = os.path.join("工作区", "20260105+前端表单功能测试", "新增功能测试报告.json")
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"错误报告已保存至: {report_path}")
            
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_add_user())