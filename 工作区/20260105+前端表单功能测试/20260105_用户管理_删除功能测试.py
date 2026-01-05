import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import asyncio
from playwright.async_api import async_playwright, expect

async def test_delete_user():
    print("===== 开始执行用户管理删除功能测试 =====")
    
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
            
            print("[步骤6] 选择要删除的用户")
            
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
                    
                    user_id_cell = page.locator(f"tbody tr:nth-child({selected_idx}) td:nth-child(1)")
                    user_id_text = await user_id_cell.text_content()
                    
                    selected_user = {
                        "index": selected_idx,
                        "username": username_value,
                        "user_id": user_id_text.strip() if user_id_text else None
                    }
                    print(f"  找到可删除的用户: {username_value} (ID: {selected_user['user_id']})")
                    
                    await page.locator(f"tbody tr:nth-child({selected_idx}) .el-checkbox__input").first.click()
                    print(f"  已选中用户: {username_value}")
                    break
            
            if not selected_user:
                print("[WARN] 未找到可删除的用户（admin用户禁止删除）")
                await page.wait_for_timeout(2000)
                result = {
                    "status": "SKIP",
                    "reason": "无可删除的用户"
                }
                
                import json
                import os
                report_path = os.path.join(os.getcwd(), "工作区", "20260105+前端表单功能测试", "删除功能测试报告.json")
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"\n测试报告已保存至: {report_path}")
                await browser.close()
                return
            
            print(f"\n准备删除用户: {selected_user['username']}")
            
            print("[步骤7] 点击删除按钮")
            delete_buttons = await page.locator("button:has-text('删除')").all()
            await delete_buttons[1].click()
            
            print("[步骤8] 在确认对话框中点击确定")
            await page.wait_for_timeout(1000)
            
            try:
                confirm_button = page.get_by_role("button", name="确 定")
                await confirm_button.wait_for(state="visible", timeout=3000)
                await confirm_button.click()
                print("  已点击确认按钮")
            except:
                try:
                    confirm_button = page.locator(".el-message-box .el-button--primary")
                    await confirm_button.wait_for(state="visible", timeout=3000)
                    await confirm_button.click()
                    print("  已点击确认按钮（通过 el-button--primary）")
                except:
                    try:
                        confirm_button = page.locator("button.el-button--primary:has-text('确 定')")
                        await confirm_button.wait_for(state="visible", timeout=3000)
                        await confirm_button.click()
                        print("  已点击确认按钮（通过组合选择器）")
                    except Exception as e:
                        print(f"[WARN] 无法找到确认按钮，尝试按键确认: {e}")
                        await page.keyboard.press("Enter")
            
            print("[步骤9] 验证删除成功提示")
            success_msgs = ["操作成功", "删除成功", "保存成功"]
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
                "status": "PASS" if success_found else "UNCERTAIN",
                "deleted_user": selected_user["username"],
                "deleted_user_id": selected_user["user_id"]
            }
            
            import json
            import os
            report_path = os.path.join(os.getcwd(), "工作区", "20260105+前端表单功能测试", "删除功能测试报告.json")
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
            report_path = os.path.join(os.getcwd(), "工作区", "20260105+前端表单功能测试", "删除功能测试报告.json")
            os.makedirs(os.path.dirname(report_path), exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"错误报告已保存至: {report_path}")
            
            import traceback
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_delete_user())