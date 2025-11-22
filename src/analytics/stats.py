"""艾宾浩斯统计分析+可视化模块"""
'''from src.database.manager import DatabaseManager
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np


class EbbinghausStatsService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        # 设置中文字体（避免中文乱码）
        plt.rcParams['font.sans-serif'] = ['SimHei']  # Windows：黑体；Mac：Arial Unicode MS
        plt.rcParams['axes.unicode_minus'] = False

    def generate_full_report(self, user_id):
        """生成完整统计报告（文字+图表）"""
        print("= - stats.py:18" * 50)
        print(f"📊 艾宾浩斯复习统计报告（用户ID：{user_id}） - stats.py:19")
        print(f"生成时间：{datetime.now().strftime('%Y%m%d %H:%M:%S')} - stats.py:20")
        print("= - stats.py:21" * 50)

        # 1. 整体概览
        overall = self.db_manager.get_overall_stats(user_id)
        print("\n【整体概览】 - stats.py:25")
        print(f"总知识点数：{overall['total_knowledge']} 个 - stats.py:26")
        print(f"已掌握知识点：{overall['mastered_knowledge']} 个 - stats.py:27")
        print(f"30天复习完成率：{overall['completion_rate_30d']}% - stats.py:28")
        print(f"连续复习天数：{overall['streak_days']} 天 - stats.py:29")
        print(f"上次复习时间：{overall['last_review_date']} - stats.py:30")

        # 2. 各阶段知识点分布（饼图）
        stage_stats = self.db_manager.get_ebbinghaus_stats(user_id)
        print("\n【各艾宾浩斯阶段未完成知识点】 - stats.py:34")
        stage_names = [
            "第1阶段（20分钟）", "第2阶段（1小时）", "第3阶段（12小时）",
            "第4阶段（1天）", "第5阶段（4天）", "第6阶段（7天）", "第7阶段（15天）"
        ]
        for stage, count in stage_stats.items():
            print(f"{stage_names[stage]}：{count} 个 - stats.py:40")
        self._plot_stage_pie(stage_stats)

        # 3. 近7天复习效果趋势（折线图）
        daily_stats = self.db_manager.get_daily_review_stats(user_id, days=7)
        print("\n【近7天复习效果】 - stats.py:45")
        for day in daily_stats:
            print(
                f"{day['date']}：平均回忆分 {day['avg_recall_score']}，复习 {day['review_count']} 次 - stats.py:47")
        self._plot_daily_trend(daily_stats)

        print("\n - stats.py:50" + "=" * 50)

    def _plot_stage_pie(self, stage_stats):
        """绘制各阶段知识点分布饼图"""
        if not stage_stats:
            print("⚠️  暂无未完成的复习计划，无法生成阶段分布图表 - stats.py:55")
            return

        labels = [f"第{stage + 1}阶段" for stage in stage_stats.keys()]
        sizes = list(stage_stats.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))

        plt.figure(figsize=(8, 6))
        wedges, texts, autotexts = plt.pie(
            sizes, labels=labels, colors=colors, autopct="%1.1f%%",
            startangle=90, textprops={"fontsize": 10}
        )
        plt.title("各艾宾浩斯阶段未完成知识点占比", fontsize=14, pad=20)
        plt.axis("equal")  # 保证饼图为正圆形
        plt.tight_layout()
        plt.show()

    def _plot_daily_trend(self, daily_stats):
        """绘制近7天复习效果趋势图"""
        if not daily_stats:
            print("⚠️  近7天无复习记录，无法生成趋势图表 - stats.py:75")
            return

        dates = [datetime.strptime(day["date"], "%Y-%m-%d").date()
                 for day in daily_stats]
        avg_scores = [day["avg_recall_score"] for day in daily_stats]
        review_counts = [day["review_count"] for day in daily_stats]

        # 创建双轴图
        fig, ax1 = plt.subplots(figsize=(10, 5))
        # 回忆分数（左轴）
        ax1.plot(
            dates,
            avg_scores,
            marker="o",
            color="#2E86AB",
            linewidth=2,
            label="平均回忆分数")
        ax1.set_xlabel("日期", fontsize=12)
        ax1.set_ylabel("平均回忆分数（0-100）", fontsize=12, color="#2E86AB")
        ax1.tick_params(axis="y", labelcolor="#2E86AB")
        ax1.set_ylim(0, 100)  # 回忆分数范围固定0-100

        # 复习次数（右轴）
        ax2 = ax1.twinx()
        ax2.bar(dates, review_counts, alpha=0.5, color="#A23B72", label="复习次数")
        ax2.set_ylabel("复习次数", fontsize=12, color="#A23B72")
        ax2.tick_params(axis="y", labelcolor="#A23B72")
        ax2.set_ylim(0, max(review_counts) + 1)

        # 格式化x轴日期
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)

        # 添加图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

        plt.title("近7天复习效果趋势", fontsize=14, pad=20)
        plt.tight_layout()
        plt.show()
'''
from datetime import datetime, timedelta


class ReviewStatsAnalyzer:
    """复习数据统计分析器（核心类，供UI调用）"""

    def __init__(self, db_manager):
        """接收数据库管理器实例（避免重复创建数据库连接）"""
        self.db_manager = db_manager

    def get_overall_review_stats(self, user_id):
        """统计用户整体复习情况（核心统计维度）"""
        # 1. 总复习计划数、已完成数
        total_schedules = self.db_manager.get_total_review_schedules(user_id)
        completed_schedules = self.db_manager.get_completed_review_schedules(user_id)

        # 2. 复习完成率（避免除零错误）
        completion_rate = (completed_schedules / total_schedules * 100) if total_schedules > 0 else 0.0

        # 3. 最近7天复习量
        recent_7d_reviews = self.db_manager.get_reviews_in_date_range(
            user_id,
            start_date=datetime.now() - timedelta(days=7),
            end_date=datetime.now()
        )

        # 4. 平均复习效果分
        avg_effectiveness = self.db_manager.get_avg_review_effectiveness(user_id)

        # 返回格式化结果（供UI展示）
        return {
            "total_schedules": total_schedules,
            "completed_schedules": completed_schedules,
            "completion_rate": round(completion_rate, 1),  # 保留1位小数
            "recent_7d_reviews": recent_7d_reviews,
            "avg_effectiveness": round(avg_effectiveness, 1) if avg_effectiveness else 0.0
        }

    def get_knowledge_mastery(self, user_id):
        """统计各知识点掌握情况（可选扩展维度）"""
        return self.db_manager.get_knowledge_review_stats(user_id)