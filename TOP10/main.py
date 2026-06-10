# main.py
# -*- coding: utf-8 -*-
"""
电池数据分析系统 - 主入口脚本
使用方式：
1. 数据分析模式：python main.py --analyze --start 2024-01-01 --end 2024-12-31 --model ModelX
2. Web服务模式：python main.py --web
3. 完整模式：python main.py --all
"""

import argparse
import sys
import os
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='电池数据分析系统')
    parser.add_argument('--analyze', action='store_true', help='执行数据分析')
    parser.add_argument('--web', action='store_true', help='启动Web服务器')
    parser.add_argument('--all', action='store_true', help='执行分析并启动Web服务器')
    parser.add_argument('--start', type=str, help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--model', type=str, help='机种类型')
    parser.add_argument('--config', type=str, default='development', help='配置环境')
    
    args = parser.parse_args()
    
    # 如果没有指定任何模式，显示帮助
    if not any([args.analyze, args.web, args.all]):
        parser.print_help()
        sys.exit(1)
    
    # 导入配置
    try:
        from config import DATABASE_CONFIG, DEFAULT_PARAMS
        db_config = DATABASE_CONFIG.get(args.config, DATABASE_CONFIG['development'])
    except ImportError:
        print("错误：找不到配置文件")
        sys.exit(1)
    
    # 设置默认参数
    start_date = args.start or DEFAULT_PARAMS['start_date']
    end_date = args.end or DEFAULT_PARAMS['end_date']
    model_type = args.model or DEFAULT_PARAMS['model_type']
    
    # 执行数据分析
    if args.analyze or args.all:
        print(f"开始数据分析...")
        print(f"时间范围: {start_date} 到 {end_date}")
        print(f"机种: {model_type}")
        
        try:
            from data_analysis import BatteryDataAnalyzer
            
            analyzer = BatteryDataAnalyzer(db_config)
            
            if analyzer.connect_database():
                data = analyzer.fetch_battery_data(start_date, end_date, model_type)
                
                if data is not None:
                    analyzer.calculate_yield_statistics()
                    analyzer.analyze_top10_first_pass_failures()
                    analyzer.analyze_top3_final_failures()
                    analyzer.save_results()
                    
                    print("\n数据分析完成！")
                else:
                    print("无法获取数据，请检查查询参数。")
            else:
                print("数据库连接失败。")
                
        except Exception as e:
            print(f"数据分析过程中出错: {str(e)}")
    
    # 启动Web服务器
    if args.web or args.all:
        print("\n启动Web服务器...")
        print("请访问 http://localhost:5000")
        
        try:
            # 确保有分析结果
            results_dir = './results'
            if not os.path.exists(results_dir) or not os.listdir(results_dir):
                print("警告：没有找到分析结果，将显示示例数据。")
            
            # 导入并运行Web应用
            from web_dashboard import app
            app.run(host='localhost', port=5000, debug=False)
            
        except Exception as e:
            print(f"Web服务器启动失败: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main()