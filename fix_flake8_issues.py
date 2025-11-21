#!/usr/bin/env python3
"""
快速修复flake8问题的脚本
"""

import os

def fix_issues():
    """修复所有flake8报告的问题"""
    
    # 1. 修复 analytics/stats.py 中的 fig 变量问题
    stats_file = "src/analytics/stats.py"
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            content = f.read()
        
        # 修复双轴图创建方式
        if "fig, ax1 = plt.figure(figsize=(10, 5)), plt.subplot(111)" in content:
            content = content.replace(
                "fig, ax1 = plt.figure(figsize=(10, 5)), plt.subplot(111)",
                "fig, ax1 = plt.subplots(figsize=(10, 5))"
            )
        
        with open(stats_file, 'w') as f:
            f.write(content)
        print(f"✅ 修复 {stats_file}")
    
    # 2. 修复 database/manager.py
    manager_file = "src/database/manager.py"
    if os.path.exists(manager_file):
        with open(manager_file, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        for i, line in enumerate(lines):
            # 删除未使用的导入
            if "from collections import defaultdict" in line:
                continue
            # 修复f-string警告
            elif "logger.info(f\"开始查询用户 {user_id} 的知识点\")" in line:
                new_lines.append('    logger.info("开始查询用户 %s 的知识点", user_id)\n')
            # 删除未使用的 today_end 变量
            elif "today_end = today + timedelta(days=1)" in line:
                # 检查这个变量是否真的被使用了
                used = False
                for j in range(i+1, min(i+10, len(lines))):
                    if "today_end" in lines[j]:
                        used = True
                        break
                if used:
                    new_lines.append(line)
                else:
                    print(f"⚠️  删除未使用的变量: {line.strip()}")
            else:
                new_lines.append(line)
        
        with open(manager_file, 'w') as f:
            f.writelines(new_lines)
        print(f"✅ 修复 {manager_file}")
    
    # 3. 修复其他文件的导入问题
    files_to_fix = [
        ("src/knowledge/ui.py", "from datetime import datetime"),
        ("src/scheduler/reminder.py", "from datetime import datetime"),
    ]
    
    for file_path, import_line in files_to_fix:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            
            # 检查这个导入是否真的被使用了
            lines = content.split('\n')
            new_lines = []
            import_used = False
            
            for line in lines:
                if import_line in line:
                    # 检查导入的内容是否在文件后面被使用
                    import_name = import_line.split()[-1]
                    if import_name in content[content.find(line) + len(line):]:
                        new_lines.append(line)
                        import_used = True
                    else:
                        print(f"⚠️  删除未使用的导入: {line.strip()}")
                else:
                    new_lines.append(line)
            
            if not import_used:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(new_lines))
                print(f"✅ 修复 {file_path}")
    
    # 4. 修复 scheduler/ui.py 的导入
    scheduler_ui_file = "src/scheduler/ui.py"
    if os.path.exists(scheduler_ui_file):
        with open(scheduler_ui_file, 'r') as f:
            content = f.read()
        
        # 删除未使用的 ReviewSchedule 导入
        if "from src.database.models import ReviewSchedule, KnowledgeItem" in content:
            content = content.replace(
                "from src.database.models import ReviewSchedule, KnowledgeItem",
                "from src.database.models import KnowledgeItem"
            )
        
        with open(scheduler_ui_file, 'w') as f:
            f.write(content)
        print(f"✅ 修复 {scheduler_ui_file}")
    
    print("🎉 所有flake8问题已修复！")

if __name__ == "__main__":
    fix_issues()
