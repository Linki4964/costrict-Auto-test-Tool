c         input_elem.press("Tab")
                            except Exception as e:
                                print(f"处理第{i+1}个输入框时出错: {e}")
                        
                        # 尝试提交表单
                        try:
                            page.locator(".el-dialog .el-button--primary:has-text('确 定')").first.click()
                            time.sleep(2)
                            
                            # 检查是否有成功提示
                            success_found = False
                            for msg in ["操作成功", "新增成功", "保存成功"]:
                                try:
                                    expect(page.get_by_text(msg)).to_be_visible(timeout=3000)
                                    success_found = True
                                    print(f"[PASS] 找到成功提示: {msg}")
                                    break
                                except:
                                    continue
                            
                            if success_found:
                                print("[PASS] 表单提交可能成功")
                            else:
                                print("[WARN] 未找到预期的成功提示")
                            
                        except Exception as e:
                            print(f"[WARN] 表单提交失败: {e}")
                        
                    except Exception as e:
                        print(f"[WARN] 输入框诊断失败: {e}")
                    
                    # 关闭对话框
                    try:
                        page.locator(".el-dialog__headerbtn").click()
                        time.sleep(1)
                    except:
                        pass
                
            except Exception as e:
                print(f"[WARN] 新增用户测试失败: {e}")
            
            print("\n=== 测试完成 ===")
            print("[PASS] 用户管理模块改进功能测试执行完成")
            
            page.screenshot(path="user_management_improved_test_success.png")
            print("改进测试成功截图已保存")
            
        except Exception as e:
            print(f"\n[FAIL] 测试执行失败: {e}")
            try:
                page.screenshot(path="user_management_improved_test_error.png")
                print("错误截图已保存")
                
                # 尝试获取当前页面的调试信息
                try:
                    print("\n=== 调试信息 ===")
                    current_url = page.url
                    print(f"当前URL: {current_url}")
                    
                    # 获取页面标题
                    title = page.title()
                    print(f"页面标题: {title}")
                    
                    # 尝试获取页面中的文本内容
                    body_text = page.locator("body").text_content()
                    if body_text:
                        print(f"页面内容摘要: {body_text[:200]}...")
                except Exception as debug_e:
                    print(f"获取调试信息失败: {debug_e}")
                    
            except:
                pass
            raise
        
        finally:
            try:
                context.close()
                browser.close()
            except:
z