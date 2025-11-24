import re

# 修复 analytics/service.py
with open('src/analytics/service.py', 'r') as f:
    lines = f.readlines()

# 修复第2行
if lines[1].startswith('from typing import Dict, List, Any#'):
    lines[1] = 'from typing import Dict, List, Any  \n'

# 修复函数定义，添加 user_id 参数
for i in range(len(lines)):
    if 'def get_review_stats():' in lines[i]:
        lines[i] = 'def get_review_stats(user_id: int):\n'
    elif 'def get_memory_retention_rate():' in lines[i]:
        lines[i] = 'def get_memory_retention_rate(user_id: int):\n'
    elif 'def get_today_review_count():' in lines[i]:
        lines[i] = 'def get_today_review_count(user_id: int):\n'
    elif 'def get_streak_days():' in lines[i]:
        lines[i] = 'def get_streak_days(user_id: int):\n'
    elif 'def get_review_efficiency():' in lines[i]:
        lines[i] = 'def get_review_efficiency(user_id: int):\n'
    elif 'def get_completed_review_count():' in lines[i]:
        lines[i] = 'def get_completed_review_count(user_id: int):\n'

# 修复缩进
for i in range(len(lines)):
    if lines[i].startswith('   #'):
        lines[i] = '    #' + lines[i][4:]
    elif lines[i].startswith('  #'):
        lines[i] = '    #' + lines[i][3:]

with open('src/analytics/service.py', 'w') as f:
    f.writelines(lines)

print("✅ analytics/service.py 修复完成")
