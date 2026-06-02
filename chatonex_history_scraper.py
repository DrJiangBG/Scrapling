#!/usr/bin/env python3
"""
ChatOneX 历史记录爬虫脚本
自动登录并导出所有历史记录为 HTML 文件

使用方法:
    python chatonex_history_scraper.py
"""

import asyncio
import os
import re
from pathlib import Path
from datetime import datetime
from scrapling.fetchers import DynamicSession


class ChatOneXHistoryScraper:
    """ChatOneX 历史记录爬虫"""
    
    def __init__(self, output_dir: str = "./history_exports"):
        self.url = "https://ai.chatonex.com/home"
        self.phone = "15800473016"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        print(f"[✓] 输出目录: {self.output_dir.absolute()}")
    
    def _sanitize_filename(self, name: str) -> str:
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # 移除末尾的点和空格
        name = name.rstrip('. ')
        # 限制长度
        if len(name) > 200:
            name = name[:200]
        return name if name else "untitled"
    
    async def login(self, session: DynamicSession) -> bool:
        """
        执行登录流程
        
        步骤:
        1. 访问网站
        2. 点击手机登录
        3. 填写手机号
        4. 点击获取验证码
        5. 等待用户输入验证码
        6. 验证登录成功
        """
        print("\n" + "="*60)
        print("开始登录流程")
        print("="*60)
        
        try:
            # 第1步: 访问网站
            print(f"\n[1/6] 访问网站: {self.url}")
            page = await session.fetch(self.url, headless=False)
            print(f"[✓] 页面加载完成，状态码: {page.status}")
            
            # 等待页面加载稳定
            await asyncio.sleep(2)
            
            # 第2步: 点击手机登录按钮
            print("\n[2/6] 查找并点击'手机号登录'按钮")
            # 尝试多个可能的选择器
            selectors = [
                'button:has-text("手机号登录")',
                'button:has-text("手机登录")',
                '[class*="phone"][class*="login"]',
                'text=手机号登录',
            ]
            
            phone_login_found = False
            for selector in selectors:
                try:
                    # 使用 page_action 来执行 JavaScript 点击
                    print(f"  尝试选择器: {selector}")
                    # 这里需要使用浏览器自动化来点击
                    # 由于 Scrapling 的 DynamicSession 基于 Playwright
                    await session._browser_tab.click(selector, timeout=3000)
                    phone_login_found = True
                    print("[✓] 成功点击手机登录按钮")
                    break
                except:
                    continue
            
            if not phone_login_found:
                print("[⚠] 未找到手机登录按钮，假设页面已在登录界面")
            
            await asyncio.sleep(1)
            
            # 第3步: 填写手机号
            print(f"\n[3/6] 填写手机号: {self.phone}")
            phone_input_selectors = [
                'input[type="tel"]',
                'input[placeholder*="手机"]',
                'input[placeholder*="电话"]',
                'input[pattern*="\\d"]',
            ]
            
            phone_filled = False
            for selector in phone_input_selectors:
                try:
                    await session._browser_tab.fill(selector, self.phone, timeout=3000)
                    phone_filled = True
                    print(f"[✓] 成功填写手机号到选择器: {selector}")
                    break
                except:
                    continue
            
            if not phone_filled:
                print("[⚠] 自动填写失败，请手动填写手机号后继续")
                input("请手动填写手机号后，按 Enter 继续...")
            
            await asyncio.sleep(1)
            
            # 第4步: 点击获取验证码按钮
            print("\n[4/6] 点击'获取验证码'按钮")
            code_button_selectors = [
                'button:has-text("获取验证码")',
                'button:has-text("发送验证码")',
                '[class*="code"][class*="button"]',
                'text=获取验证码',
            ]
            
            code_button_found = False
            for selector in code_button_selectors:
                try:
                    await session._browser_tab.click(selector, timeout=3000)
                    code_button_found = True
                    print("[✓] 成功点击获取验证码按钮")
                    break
                except:
                    continue
            
            if not code_button_found:
                print("[⚠] 未找到获取验证码按钮，请手动点击")
                input("请手动点击'获取验证码'按钮后，按 Enter 继续...")
            
            await asyncio.sleep(2)
            
            # 第5步: 等待用户输入验证码
            print("\n[5/6] 等待验证码...")
            print("="*60)
            print("[!] 请查看你的手机，你应该收到来自 ChatOneX 的验证码短信")
            print("="*60)
            
            verification_code = input("\n请输入你收到的验证码: ").strip()
            
            if not verification_code or len(verification_code) < 4:
                print("[✗] 验证码无效，请重新运行脚本")
                return False
            
            print(f"[✓] 你输入的验证码: {verification_code}")
            
            # 第5.5步: 填写验证码
            print("\n[5.5/6] 填写验证码到输入框")
            code_input_selectors = [
                'input[placeholder*="验证码"]',
                'input[placeholder*="码"]',
                'input[type="text"][maxlength="6"]',
                'input[inputmode="numeric"]',
            ]
            
            code_filled = False
            for selector in code_input_selectors:
                try:
                    await session._browser_tab.fill(selector, verification_code, timeout=3000)
                    code_filled = True
                    print(f"[✓] 成功填写验证码")
                    break
                except:
                    continue
            
            if not code_filled:
                print("[⚠] 自动填写验证码失败，请手动填写")
                input("请手动填写验证码后，按 Enter 继续...")
            
            await asyncio.sleep(1)
            
            # 第6步: 点击登录按钮并等待页面跳转
            print("\n[6/6] 点击登录按钮")
            login_button_selectors = [
                'button:has-text("登录")',
                'button:has-text("确认")',
                '[class*="login"][class*="button"]',
                'text=登录',
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    await session._browser_tab.click(selector, timeout=3000)
                    login_clicked = True
                    print("[✓] 成功点击登录按钮")
                    break
                except:
                    continue
            
            if not login_clicked:
                print("[⚠] 未找到登录按钮，请手动点击")
                input("请手动点击登录按钮后，按 Enter 继续...")
            
            # 等待页面跳转和加载
            print("\n[⏳] 等待页面加载...")
            await asyncio.sleep(3)
            
            # 验证登录成功
            print("[✓] 登录流程完成！")
            print("="*60 + "\n")
            return True
            
        except Exception as e:
            print(f"[✗] 登录出错: {str(e)}")
            print("请手动完成登录后，按 Enter 继续...")
            input()
            return True  # 继续处理，假设手动登录成功


    async def extract_history_records(self, session: DynamicSession) -> list:
        """
        提取历史记录列表
        
        返回: [(记录名称, HTML内容), ...]
        """
        print("\n" + "="*60)
        print("提取历史记录")
        print("="*60)
        
        try:
            # 刷新页面确保获取最新内容
            print("\n[1/3] 刷新页面...")
            page = await session.fetch(self.url, headless=False)
            await asyncio.sleep(2)
            
            # 获取当前页面的 HTML
            print("[2/3] 获取页面内容...")
            
            # 查找历史记录容器的选择器
            # 这些是常见的选择器，可能需要根据实际网站结构调整
            history_selectors = [
                '[class*="history"]',
                '[class*="record"]',
                '[data-test="history"]',
                '.sidebar-history',
                '.history-list',
                'div[class*="history"] > div',
            ]
            
            records = []
            
            for selector in history_selectors:
                try:
                    items = page.css(selector)
                    if items and len(items) > 0:
                        print(f"[✓] 找到历史记录容器: {selector}")
                        print(f"[✓] 共找到 {len(items)} 条记录\n")
                        
                        for i, item in enumerate(items, 1):
                            try:
                                # 提取记录名称
                                name_selectors = [
                                    'span:nth-child(1)::text',
                                    '.name::text',
                                    '[class*="title"]::text',
                                    '::text',  # 所有文本
                                ]
                                
                                record_name = None
                                for name_selector in name_selectors:
                                    name_text = item.css(name_selector).get()
                                    if name_text and name_text.strip():
                                        record_name = name_text.strip()
                                        break
                                
                                if not record_name:
                                    record_name = f"记录_{i}"
                                
                                # 获取完整 HTML
                                html_content = item.get()
                                
                                records.append((record_name, html_content))
                                print(f"  [{i}] {record_name[:50]}... ✓")
                            
                            except Exception as e:
                                print(f"  [{i}] 提取失败: {str(e)}")
                                continue
                        
                        if records:
                            return records
                
                except:
                    continue
            
            if not records:
                print("[⚠] 未找到历史记录，请确保已成功登录")
            
            return records
        
        except Exception as e:
            print(f"[✗] 提取记录出错: {str(e)}")
            return []
    
    async def export_records(self, records: list) -> int:
        """
        导出历史记录为 HTML 文件
        
        返回: 成功导出的文件数
        """
        print("\n" + "="*60)
        print("导出历史记录为 HTML 文件")
        print("="*60 + "\n")
        
        if not records:
            print("[⚠] 没有记录需要导出")
            return 0
        
        success_count = 0
        
        for record_name, html_content in records:
            try:
                # 清理文件名
                clean_name = self._sanitize_filename(record_name)
                filename = f"{clean_name}.html"
                filepath = self.output_dir / filename
                
                # 创建完整的 HTML 文档
                full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{record_name}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 2px solid #007bff;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .title {{
            font-size: 24px;
            font-weight: bold;
            margin: 0 0 5px 0;
        }}
        .meta {{
            font-size: 12px;
            color: #999;
            margin: 5px 0 0 0;
        }}
        .content {{
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{record_name}</h1>
            <p class="meta">导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p class="meta">来源: ChatOneX (https://ai.chatonex.com)</p>
        </div>
        <div class="content">
            {html_content}
        </div>
    </div>
</body>
</html>"""
                
                # 保存文件
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                
                success_count += 1
                print(f"[✓] {filename}")
                print(f"    路径: {filepath.absolute()}\n")
            
            except Exception as e:
                print(f"[✗] 导出失败: {record_name}")
                print(f"    错误: {str(e)}\n")
                continue
        
        return success_count
    
    async def run(self):
        """运行完整的爬虫流程"""
        print("\n")
        print("╔" + "="*58 + "╗")
        print("║" + " ChatOneX 历史记录爬虫 - 自动化脚本 ".center(58) + "║")
        print("╚" + "="*58 + "╝")
        print(f"\n目标网址: {self.url}")
        print(f"手机号: {self.phone}")
        print(f"输出目录: {self.output_dir.absolute()}\n")
        
        try:
            # 使用 DynamicSession (浏览器自动化)
            async with DynamicSession(headless=False) as session:
                # 步骤 1: 登录
                login_success = await self.login(session)
                if not login_success:
                    print("[✗] 登录失败，程序终止")
                    return
                
                # 步骤 2: 提取历史记录
                records = await self.extract_history_records(session)
                
                # 步骤 3: 导出为 HTML
                if records:
                    exported_count = await self.export_records(records)
                    
                    print("\n" + "="*60)
                    print("完成!")
                    print("="*60)
                    print(f"\n[✓] 成功导出 {exported_count}/{len(records)} 条记录")
                    print(f"[✓] 所有文件已保存到: {self.output_dir.absolute()}\n")
                    
                    # 列出所有导出的文件
                    print("导出的文件列表:")
                    for html_file in sorted(self.output_dir.glob("*.html")):
                        print(f"  - {html_file.name}")
                else:
                    print("\n[⚠] 未找到任何记录")
        
        except Exception as e:
            print(f"\n[✗] 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    scraper = ChatOneXHistoryScraper(output_dir="./chatonex_history")
    await scraper.run()


if __name__ == "__main__":
    # 检查依赖
    try:
        from scrapling.fetchers import DynamicSession
    except ImportError:
        print("错误: 未找到 Scrapling 库")
        print("\n请先安装 Scrapling:")
        print("  pip install scrapling[all]")
        print("  scrapling install")
        exit(1)
    
    # 运行爬虫
    asyncio.run(main())
