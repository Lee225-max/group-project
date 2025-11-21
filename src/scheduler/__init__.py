"""
调度算法模块
"""

# 注释掉不存在的导入
# from .algorithms import EbbinghausScheduler
from .service import SchedulerService
from .ui import ReviewSchedulerFrame, ReviewDialog

__all__ = [
    # "EbbinghausScheduler",
    "SchedulerService",
    "ReviewSchedulerFrame",
    "ReviewDialog",
]
