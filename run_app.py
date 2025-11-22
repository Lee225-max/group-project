#!/usr/bin/env python3
"""
应用程序启动脚本 - 在项目根目录运行
"""
import sys
import os
import logging

# 添加项目根目录和src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 添加src目录到Python路径
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数 - 启动图形界面"""
    try:
        logger.info("🚀 启动智能复习闹钟...")
        
        # 调试信息：显示Python路径
        logger.debug("Python路径:")
        for path in sys.path:
            logger.debug(f"  {path}")
        
        # 检查关键模块是否存在
        required_modules = [
            'src.database.manager',
            'src.auth.ui', 
            'src.knowledge.ui'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
                logger.debug(f"✅ 模块 {module} 可正常导入")
            except ImportError as e:
                logger.warning(f"⚠️ 模块 {module} 导入失败: {e}")
        
        # 直接启动图形界面应用
        from src.app import ReviewAlarmApp
        
        logger.info("正在初始化图形界面...")
        app = ReviewAlarmApp()
        logger.info("图形界面初始化完成，启动主循环...")
        app.run()
        
        logger.info("✅ 程序执行完成")
        return 0
        
    except ImportError as e:
        logger.error(f"❌ 导入模块失败: {str(e)}")
        
        # 详细的错误诊断
        print("\n错误: 无法导入必要的模块 - run_app.py:64")
        print(f"详情: {e} - run_app.py:65")
        print(f"\n当前工作目录: {os.getcwd()} - run_app.py:66")
        print(f"脚本所在目录: {current_dir} - run_app.py:67")
        print("Python路径: - run_app.py:68")
        for i, path in enumerate(sys.path[:5]):  # 只显示前5个路径
            print(f"{i+1}. {path} - run_app.py:70")
        
        print("\n请检查以下文件和目录是否存在: - run_app.py:72")
        print("1. 数据库模块: src/database/manager.py - run_app.py:73")
        print("2. 认证模块: src/auth/ui.py - run_app.py:74") 
        print("3. 知识管理模块: src/knowledge/ui.py - run_app.py:75")
        print("4. 主应用模块: src/app.py - run_app.py:76")
        
        # 检查文件是否存在
        files_to_check = [
            'src/database/manager.py',
            'src/auth/ui.py',
            'src/knowledge/ui.py', 
            'src/app.py'
        ]
        
        print("\n文件状态检查: - run_app.py:86")
        for file_path in files_to_check:
            full_path = os.path.join(current_dir, file_path)
            if os.path.exists(full_path):
                print(f"✅ {file_path}  存在 - run_app.py:90")
            else:
                print(f"❌ {file_path}  缺失 - run_app.py:92")
                
        return 1
        
    except Exception as e:
        logger.error(f"❌ 程序启动失败: {str(e)}", exc_info=True)
        
        # 尝试显示图形错误对话框
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror(
                "启动错误", 
                f"无法启动智能复习闹钟:\n\n{str(e)}\n\n请查看控制台输出获取详细信息。"
            )
            root.destroy()
        except Exception as dialog_error:
            # 如果图形界面也失败，回退到控制台输出
            print(f"启动错误: {e} - run_app.py:113")
            print(f"错误对话框也失败: {dialog_error} - run_app.py:114")
            
        return 1


if __name__ == "__main__":
    sys.exit(main())
