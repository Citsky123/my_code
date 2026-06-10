from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
import io
import glob

app = Flask(__name__)
CORS(app)

# 配置生产排程文件目录
PRODUCTION_SCHEDULE_DIR = r"D:\VScode\production-visualization\生产排程"

class ProductionScheduleAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}
        
    def parse_excel(self):
        """解析Excel文件"""
        try:
            # 读取所有工作表
            xls = pd.ExcelFile(self.file_path)
            sheet_data = {}
            
            for sheet_name in xls.sheet_names:
                try:
                    # 尝试使用 openpyxl 引擎，如果失败则使用默认引擎
                    try:
                        df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None, engine='openpyxl')
                    except:
                        df = pd.read_excel(self.file_path, sheet_name=sheet_name, header=None)
                    
                    parsed_data = self._parse_sheet(df, sheet_name)
                    sheet_data[sheet_name] = parsed_data
                    
                except Exception as e:
                    print(f"解析工作表 {sheet_name} 时出错: {e}")
                    # 即使某个工作表解析失败，继续处理其他工作表
                    sheet_data[sheet_name] = {
                        'sheet_name': sheet_name,
                        'dates': [],
                        'production_data': []
                    }
                    
            self.data = sheet_data
            return True
        except Exception as e:
            print(f"解析错误: {e}")
            return False
    
    def _parse_sheet(self, df, sheet_name):
        """解析单个工作表"""
        sheet_info = {
            'sheet_name': sheet_name,
            'dates': [],
            'production_data': []
        }
        
        # 查找日期行（通常在第2行）
        date_row_idx = None
        for idx in range(min(5, len(df))):
            row_values = df.iloc[idx].dropna().astype(str)
            if any('2025' in str(val) for val in row_values):
                date_row_idx = idx
                break
        
        if date_row_idx is None:
            return sheet_info
        
        # 提取日期
        date_row = df.iloc[date_row_idx].dropna()
        dates = [str(val).split()[0] for val in date_row if '2025' in str(val)]
        sheet_info['dates'] = dates
        
        # 查找数据开始行（包含Model, P/N, W/O, Q'ty的行）
        data_start_idx = None
        for idx in range(date_row_idx + 1, min(date_row_idx + 10, len(df))):
            row_values = df.iloc[idx].dropna().astype(str)
            if any('Model' in val for val in row_values):
                data_start_idx = idx + 1
                break
        
        if data_start_idx is None:
            return sheet_info
        
        # 解析生产数据
        for idx in range(data_start_idx, len(df)):
            row = df.iloc[idx]
            if pd.isna(row.iloc[0]) or 'Input' not in str(row.iloc[1]):
                continue
                
            # 提取模型信息
            model_info = {
                'line': str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else '',
                'type': str(row.iloc[1]).strip(),
                'daily_data': []
            }
            
            # 提取每日数据（每4列为一组：Model, P/N, W/O, Q'ty）
            col_idx = 2
            for i, date in enumerate(dates):
                if col_idx + 3 >= len(row):
                    break
                    
                daily_info = {
                    'date': date,
                    'model': str(row.iloc[col_idx]) if pd.notna(row.iloc[col_idx]) else '',
                    'part_number': str(row.iloc[col_idx+1]) if pd.notna(row.iloc[col_idx+1]) else '',
                    'work_order': str(row.iloc[col_idx+2]) if pd.notna(row.iloc[col_idx+2]) else '',
                    'quantity': self._parse_quantity(row.iloc[col_idx+3])
                }
                
                if daily_info['quantity'] > 0:
                    model_info['daily_data'].append(daily_info)
                
                col_idx += 4
            
            if model_info['daily_data']:
                sheet_info['production_data'].append(model_info)
        
        return sheet_info
    
    def _parse_quantity(self, value):
        """解析数量字段"""
        try:
            if pd.isna(value):
                return 0
            return int(float(str(value)))
        except:
            return 0
    
    def get_summary_stats(self):
        """获取汇总统计"""
        summary = {
            'total_sheets': len(self.data),
            'sheets': [],
            'total_quantity': 0,
            'date_range': {}
        }
        
        all_dates = set()
        total_qty = 0
        
        for sheet_name, sheet_info in self.data.items():
            sheet_summary = {
                'name': sheet_name,
                'total_quantity': 0,
                'models': [],
                'dates': []
            }
            
            for production in sheet_info['production_data']:
                model_qty = sum(daily['quantity'] for daily in production['daily_data'])
                sheet_summary['total_quantity'] += model_qty
                total_qty += model_qty
                
                sheet_summary['models'].append({
                    'line': production['line'],
                    'total_quantity': model_qty
                })
                
                for daily in production['daily_data']:
                    all_dates.add(daily['date'])
                    sheet_summary['dates'].append(daily['date'])
            
            summary['sheets'].append(sheet_summary)
        
        summary['total_quantity'] = total_qty
        summary['date_range'] = {
            'start': min(all_dates) if all_dates else '',
            'end': max(all_dates) if all_dates else '',
            'count': len(all_dates)
        }
        
        return summary
    
    def get_chart_data(self):
        """生成图表数据"""
        chart_data = {
            'daily_production': self._get_daily_production_chart(),
            'sheet_comparison': self._get_sheet_comparison_chart(),
            'model_distribution': self._get_model_distribution_chart(),
            'timeline_data': self._get_timeline_data()
        }
        return chart_data
    
    def _get_daily_production_chart(self):
        """每日生产量图表数据"""
        daily_data = {}
        
        for sheet_name, sheet_info in self.data.items():
            for production in sheet_info['production_data']:
                for daily in production['daily_data']:
                    date = daily['date']
                    if date not in daily_data:
                        daily_data[date] = {}
                    daily_data[date][sheet_name] = daily_data[date].get(sheet_name, 0) + daily['quantity']
        
        # 按日期排序
        sorted_dates = sorted(daily_data.keys())
        
        chart_data = {
            'dates': sorted_dates,
            'series': []
        }
        
        # 为每个工作表创建数据系列
        for sheet_name in self.data.keys():
            series_data = [daily_data.get(date, {}).get(sheet_name, 0) for date in sorted_dates]
            chart_data['series'].append({
                'name': sheet_name,
                'data': series_data
            })
        
        return chart_data
    
    def _get_sheet_comparison_chart(self):
        """工作表比较图表数据"""
        sheet_totals = {}
        
        for sheet_name, sheet_info in self.data.items():
            total = 0
            for production in sheet_info['production_data']:
                total += sum(daily['quantity'] for daily in production['daily_data'])
            sheet_totals[sheet_name] = total
        
        return {
            'sheets': list(sheet_totals.keys()),
            'quantities': list(sheet_totals.values())
        }
    
    def _get_model_distribution_chart(self):
        """型号分布图表数据"""
        model_data = {}
        
        for sheet_name, sheet_info in self.data.items():
            for production in sheet_info['production_data']:
                model_key = f"{production['line']} - {sheet_name}"
                total_qty = sum(daily['quantity'] for daily in production['daily_data'])
                if total_qty > 0:
                    model_data[model_key] = total_qty
        
        # 取前20个型号
        sorted_models = sorted(model_data.items(), key=lambda x: x[1], reverse=True)[:20]
        
        return {
            'models': [item[0] for item in sorted_models],
            'quantities': [item[1] for item in sorted_models]
        }
    
    def _get_timeline_data(self):
        """时间线数据"""
        timeline_data = []
        
        for sheet_name, sheet_info in self.data.items():
            for production in sheet_info['production_data']:
                for daily in production['daily_data']:
                    if daily['quantity'] > 0:
                        timeline_data.append({
                            'sheet': sheet_name,
                            'model': daily['model'],
                            'part_number': daily['part_number'],
                            'work_order': daily['work_order'],
                            'date': daily['date'],
                            'quantity': daily['quantity'],
                            'line': production['line']
                        })
        
        # 按日期排序
        timeline_data.sort(key=lambda x: x['date'])
        return timeline_data

# API路由
@app.route('/api/files', methods=['GET'])
def get_excel_files():
    """获取生产排程目录下的Excel文件列表"""
    try:
        # 确保目录存在
        if not os.path.exists(PRODUCTION_SCHEDULE_DIR):
            os.makedirs(PRODUCTION_SCHEDULE_DIR)
            return jsonify({'files': [], 'message': '目录已创建，请添加Excel文件'})
        
        # 查找所有Excel文件
        excel_files = []
        for ext in ['*.xlsx', '*.xls']:
            excel_files.extend(glob.glob(os.path.join(PRODUCTION_SCHEDULE_DIR, ext)))
        
        # 提取文件名
        file_list = [os.path.basename(f) for f in excel_files]
        
        return jsonify({
            'success': True,
            'files': file_list,
            'directory': PRODUCTION_SCHEDULE_DIR
        })
    except Exception as e:
        return jsonify({'error': f'读取文件列表失败: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    """分析选定的Excel文件"""
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'error': '未指定文件名'}), 400
        
        # 构建完整文件路径
        file_path = os.path.join(PRODUCTION_SCHEDULE_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'文件不存在: {file_path}'}), 400
        
        # 解析文件
        analyzer = ProductionScheduleAnalyzer(file_path)
        if analyzer.parse_excel():
            # 获取分析结果
            summary = analyzer.get_summary_stats()
            chart_data = analyzer.get_chart_data()
            
            return jsonify({
                'success': True,
                'summary': summary,
                'chart_data': chart_data,
                'filename': filename
            })
        else:
            return jsonify({'error': '文件解析失败'}), 500
            
    except Exception as e:
        return jsonify({'error': f'分析失败: {str(e)}'}), 500

@app.route('/api/sample', methods=['GET'])
def get_sample_data():
    """获取示例数据（用于测试）"""
    return jsonify({
        'message': 'API服务运行正常',
        'endpoints': [
            '/api/files - GET - 获取Excel文件列表',
            '/api/analyze - POST - 分析选定文件',
            '/api/sample - GET - 测试接口',
            '/ - GET - 前端页面'
        ]
    })

@app.route('/')
def index():
    """返回前端页面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>生产排程可视化系统</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        <div id="app">
            <h1>生产排程可视化系统</h1>
            <p>请上传Excel文件查看可视化图表</p>
        </div>
        <script>
            window.location.href = '/static/index.html';
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    # 创建静态文件目录
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # 确保生产排程目录存在
    if not os.path.exists(PRODUCTION_SCHEDULE_DIR):
        os.makedirs(PRODUCTION_SCHEDULE_DIR)
        print(f"已创建目录: {PRODUCTION_SCHEDULE_DIR}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)