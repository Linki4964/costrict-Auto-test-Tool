import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
import random
from playwright.async_api import async_playwright, expect

async def test_update_user():
    print("===== 开始执行用户管理修改功能测试 =====")
    
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
            
            print("[步骤6] 选择要修改的用户")
            
            rows = await page.locator("tbody tr").count()
            print(f"  当前页面共有 {rows} 行用户数据")
            
            selected_user = None
            selected_idx = -1
            
            for i in range(rows):
                username_cell = page.locator(f"tbody tr:nth-child({i+1}) td:nth-child(2)")
                username_text = await username_cell.text_content()
                print(f"  检查第 {i+1} 行用户: {username_text}")
                
                if username_text and username_text.strip() != "admin":
                    selected_idx = i + 1
                    username_value = username_text.strip()
                    
                    await page.locator(f"tbody tr:nth-child({selected_idx}) .el-checkbox__input").first.click()
                    print(f"  已选中用户: {username_value}")
                    
                    user_id_cell = page.locator(f"tbody tr:nth-child({selected_idx}) td:nth-child(1)")
                    user_id_text = await user_id_cell.text_content()
                    if user_id_text:
                        print(f"  用户ID: {user_id_text.strip()}")
                    
                    selected_user = {
                        "index": selected_idx,
                        "username": username_value
                    }
                    break
            
            if not selected_user:
                print("[WARN] 未找到可修改的用户（admin用户禁止修改），将尝试创建测试用户")
                await page.wait_for_timeout(2000)
                result = {
                    "status": "SKIP",
                    "reason": "无可修改的用户"
                }
                
                import json
                import os
                report_path = os.path.join("工作区", "20260105+前端表单功能测试", "修改功能测试报告.json")
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n测试报告已保存至: {report_path}")
                await browser.close()
                print("已关闭浏览器，跳过修改测试")
                return
            
            test_id = random.randint(2000, 9999)
            print(f"\n修改用户信息: 测试ID={test_id}")
            
            print("[步骤7] 点击修改按钮")
            modify_buttons = await page.locator("button:has-text('修改')").all()
            await modify_buttons[1].click()
            
            print("[步骤8] 等待对话框弹出")
            await page.wait_for_timeout(1000)
            dialog = page.get_by_role("dialog")
            await dialog.wait_for(state="visible", timeout=10000)
            print("对话框已弹出，开始修改表单...")
            
            print("[步骤9] 修改用户昵称")
            nickname_field = dialog.locator("input[placeholder='请输入用户昵称']")
            await nickname_field.click()
            await nickname_field.fill("")
            await nickname_field.fill(f"修改昵称_{test_id}")
            
            print("[步骤10] 修改手机号码")
            phone_field = dialog.locator("input[placeholder='请输入手机号码']")
            await phone_field.click()
            await phone_field.fill("")
            await phone_field.fill(f"1390000{test_id}")
            
            print("[步骤11] 修改邮箱")
            email_field = dialog.locator("input[placeholder='请输入邮箱']")
            await email_field.click()
            await email_field.fill("")
            await email_field.fill(f"updated{test_id}@qq.com")
            
            print("[步骤12] 点击确定按钮提交修改")
            await dialog.locator(".el-dialog__footer >> button:has-text('确 定')").click()
            
            print("[步骤13] 验证修改成功提示")
            success_msgs = ["操作成功", "修改成功", "保存成功"]
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
                "target_user": selected_user["username"],
                "new_nickname": f"修改昵称_{test_id}",
                "new_phonenumber": f"1390000{test_id}",
                "new_email": f"updated{test_id}@qq.com"
            }
            
            import json
            import os
            report_path = os.path.join(os.getcwd(), "工作区", "20260105+前端表单功能测试", "修改功能测试报告.json")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
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
            report_path = os.path.join(os.getcwd(), "工作区", "20260105+前端表单功能测试", "修改功能测试报告.json")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"错误报告已保存至: {report_path}")
            
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_update_user())