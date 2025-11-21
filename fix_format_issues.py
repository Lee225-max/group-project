#!/usr/bin/env python3
"""
全面修复flake8格式问题的脚本
"""

import os
import re


def fix_format_issues():
    """修复所有格式相关问题"""
    
    # 要修复的文件列表（基于flake8输出）
    files_to_fix = [
        "src/analytics/stats.py",
        "src/app.py", 
        "src/auth/service.py",
        "src/auth/ui.py",
        "src/database/manager.py",
        "src/database/models.py",
        "src/knowledge/__init__.py",
        "src/knowledge/service.py", 
        "src/knowledge/ui.py",
        "src/scheduler/__init__.py",
        "src/scheduler/ebbinghaus_config.py",
        "src/scheduler/reminder.py",
        "src/scheduler/service.py",
        "src/scheduler/ui.py",
        "src/settings/ui.py",
        "tests/test_auth.py"
    ]
    
    for file_path in files_to_fix:
        if not os.path.exists(file_path):
            continue
            
        print(f"🔧 修复 {file_path}... - fix_format_issues.py:37")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复1: 文件末尾添加换行符
        if not content.endswith('\n'):
            content += '\n'
            print("✅ 添加文件末尾换行符 - fix_format_issues.py:45")
        
        # 修复2: 删除行尾空白字符
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            # 删除行尾空白
            cleaned_line = line.rstrip()
            new_lines.append(cleaned_line)
        
        content = '\n'.join(new_lines)
        
        # 修复3: 删除包含空白字符的空行
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.strip() == '':
                new_lines.append('')  # 真正的空行
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # 修复4: 修复注释格式 (E265)
        if file_path == "src/scheduler/ebbinghaus_config.py":
            content = content.replace(
                "#艾宾浩斯遗忘曲线复习间隔配置",
                "# 艾宾浩斯遗忘曲线复习间隔配置"
            )
        
        # 修复5: 修复缩进问题 (E128)
        if file_path == "src/scheduler/ui.py":
            content = re.sub(
                r'(\s+)stage_label = ctk\.CTkLabel\(',
                r'            stage_label = ctk.CTkLabel(',
                content
            )
        
        # 修复6: 删除多余空行 (E303)
        if file_path == "src/scheduler/service.py":
            # 将连续3个以上空行替换为2个空行
            content = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n\n', content)
        
        # 写入修复后的内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 完成格式修复 - fix_format_issues.py:92")


def fix_specific_issues():
    """修复特定的代码问题"""
    
    # 修复 database/manager.py 中的 today_end 问题
    manager_file = "src/database/manager.py"
    if os.path.exists(manager_file):
        with open(manager_file, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        today_end_used = False
        
        for i, line in enumerate(lines):
            # 检查 today_end 是否被使用
            if "today_end = today + timedelta(days=1)" in line:
                # 检查后续代码是否使用了 today_end
                for j in range(i+1, min(i+20, len(lines))):
                    if "today_end" in lines[j]:
                        today_end_used = True
                        break
                
                if today_end_used:
                    new_lines.append(line)
                else:
                    print("⚠️  删除未使用的变量: today_end - fix_format_issues.py:119")
                    continue
            else:
                new_lines.append(line)
        
        with open(manager_file, 'w') as f:
            f.writelines(new_lines)
        print("✅ 修复 database/manager.py 的 today_end 问题 - fix_format_issues.py:126")


def main():
    """主函数"""
    print("🎯 开始全面修复代码格式问题... - fix_format_issues.py:131")
    
    fix_format_issues()
    fix_specific_issues()
    
    print("🎉 所有格式问题修复完成！ - fix_format_issues.py:136")
    print("\n📋 建议后续步骤: - fix_format_issues.py:137")
    print("1. 运行: flake8 src/ tests/ - fix_format_issues.py:138")
    print("2. 提交修复: git add . && git commit m 'style: 修复代码格式问题' - fix_format_issues.py:139")
    print("3. 推送到GitHub: git push origin main - fix_format_issues.py:140")


if __name__ == "__main__":
    main()