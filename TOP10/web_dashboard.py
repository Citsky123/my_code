# web_dashboard.py
# -*- coding: utf-8 -*-
"""
电池数据可视化Web仪表板
功能：创建本地Web服务器，展示分析结果
运行后访问：http://localhost:5000
"""

from flask import Flask, render_template, jsonify
import json
import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

app = Flask(__name__)

class BatteryDashboard:
    def __init__(self, results_path='./results'):
        self.results_path = results_path
        
    def load_analysis_results(self):
        """加载分析结果"""
        try:
            with open(f'{self.results_path}/analysis_results.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 返回示例数据（如果没有分析结果文件）
            return self.get_sample_data()
    
    def get_sample_data(self):
        """获取示例数据（在没有真实数据时使用）"""
        return {
            'yield_statistics': {
                '总数量': 1000,
                '一次通过数量': 850,
                '一次通过率': 85.0,
                '最终通过数量': 920,
                '最终通过率': 92.0,
                '返工数量': 70,
                '返工率': 7.0,
                '不良数量': 80,
                '不良率': 8.0
            },
            'top10_first_pass': {
                '电压异常': 45,
                '容量不足': 38,
                '内阻过高': 32,
                '温度异常': 28,
                '外观缺陷': 25,
                '短路': 20,
                '漏液': 18,
                '极耳不良': 15,
                '焊接问题': 12,
                '材料缺陷': 10
            },
            'top3_final': {
                '严重电压异常': 15,
                '容量严重不足': 10,
                '安全测试失败': 8
            }
        }

# 创建仪表板实例
dashboard = BatteryDashboard()

@app.route('/')
def index():
    """主页面 - 显示所有图表概览"""
    return render_template('index.html', title='电池数据分析仪表板')

@app.route('/yield-stats')
def yield_statistics():
    """良率统计页面"""
    results = dashboard.load_analysis_results()
    stats = results['yield_statistics']
    
    # 创建良率图表
    categories = ['一次通过率', '最终通过率', '返工率', '不良率']
    values = [stats['一次通过率'], stats['最终通过率'], stats['返工率'], stats['不良率']]
    
    fig = go.Figure(data=[
        go.Bar(x=categories, y=values, text=[f'{v}%' for v in values], 
               textposition='auto', marker_color=['green', 'blue', 'orange', 'red'])
    ])
    
    fig.update_layout(
        title='电池生产良率统计',
        xaxis_title='指标',
        yaxis_title='百分比 (%)',
        yaxis=dict(range=[0, 100]),
        template='plotly_white'
    )
    
    # 将图表转换为JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('chart.html', 
                          title='良率统计表',
                          graphJSON=graphJSON,
                          stats=stats)

@app.route('/top10-failures')
def top10_failures():
    """TOP10一次不良追踪页面"""
    results = dashboard.load_analysis_results()
    top10 = results['top10_first_pass']
    
    # 创建TOP10图表
    reasons = list(top10.keys())
    counts = list(top10.values())
    
    fig = go.Figure(data=[
        go.Bar(y=reasons[::-1],  # 反转顺序
               x=counts[::-1],
               orientation='h',
               marker_color='lightcoral')
    ])
    
    fig.update_layout(
        title='TOP10 一次不良原因追踪',
        xaxis_title='发生次数',
        yaxis_title='不良原因',
        height=500,
        template='plotly_white'
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('chart.html', 
                          title='TOP10一次不良追踪表',
                          graphJSON=graphJSON,
                          data=top10)

@app.route('/top3-final-failures')
def top3_final_failures():
    """TOP3最终不良页面"""
    results = dashboard.load_analysis_results()
    top3 = results['top3_final']
    
    # 创建TOP3饼图
    fig = go.Figure(data=[go.Pie(
        labels=list(top3.keys()),
        values=list(top3.values()),
        hole=.3,
        marker_colors=['red', 'darkred', 'firebrick']
    )])
    
    fig.update_layout(
        title='TOP3 最终不良原因分布',
        template='plotly_white'
    )
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('chart.html', 
                          title='TOP3最终不良表',
                          graphJSON=graphJSON,
                          data=top3)

@app.route('/api/data')
def api_data():
    """提供JSON格式的原始数据"""
    results = dashboard.load_analysis_results()
    return jsonify(results)

@app.route('/dashboard')
def full_dashboard():
    """完整仪表板 - 所有图表在一个页面"""
    results = dashboard.load_analysis_results()
    
    # 创建包含3个子图的仪表板
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('良率统计', 'TOP10一次不良追踪', 'TOP3最终不良分布', '生产数据概览'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'pie'}, {'type': 'table'}]]
    )
    
    # 图表1：良率统计
    stats = results['yield_statistics']
    categories = ['一次通过率', '最终通过率', '返工率', '不良率']
    values = [stats['一次通过率'], stats['最终通过率'], stats['返工率'], stats['不良率']]
    
    fig.add_trace(
        go.Bar(x=categories, y=values, name='良率统计'),
        row=1, col=1
    )
    
    # 图表2：TOP10一次不良
    top10 = results['top10_first_pass']
    fig.add_trace(
        go.Bar(y=list(top10.keys())[:5], x=list(top10.values())[:5], 
               orientation='h', name='TOP5不良原因'),
        row=1, col=2
    )
    
    # 图表3：TOP3最终不良
    top3 = results['top3_final']
    fig.add_trace(
        go.Pie(labels=list(top3.keys()), values=list(top3.values()), name='TOP3最终不良'),
        row=2, col=1
    )
    
    # 图表4：数据表格
    table_data = [
        ['指标', '数值'],
        ['总生产数量', stats['总数量']],
        ['一次通过率', f"{stats['一次通过率']}%"],
        ['最终通过率', f"{stats['最终通过率']}%"],
        ['不良数量', stats['不良数量']],
        ['不良率', f"{stats['不良率']}%"]
    ]
    
    fig.add_trace(
        go.Table(
            header=dict(values=['指标', '数值'], align='left'),
            cells=dict(values=[row[0] for row in table_data[1:]], 
                      [[row[1] for row in table_data[1:]]], align='left')
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False, title_text="电池生产数据分析仪表板")
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template('dashboard.html', 
                          title='完整数据分析仪表板',
                          graphJSON=graphJSON,
                          results=results)

# HTML模板 - 创建 templates 文件夹并添加以下文件
"""
templates/base.html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - 电池数据分析系统</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .navbar { background: #007bff; padding: 10px; margin-bottom: 20px; }
        .navbar a { color: white; margin: 0 15px; text-decoration: none; }
        .container { max-width: 1200px; margin: 0 auto; }
        .chart-container { border: 1px solid #ddd; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }
        .stat-card { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="/">首页</a>
        <a href="/yield-stats">良率统计</a>
        <a href="/top10-failures">TOP10不良</a>
        <a href="/top3-final-failures">TOP3最终不良</a>
        <a href="/dashboard">完整仪表板</a>
        <a href="/api/data">API数据</a>
    </div>
    <div class="container">
        <h1>{{ title }}</h1>
        {% block content %}{% endblock %}
    </div>
</body>
</html>

templates/chart.html
{% extends "base.html" %}
{% block content %}
    <div id="chart" class="chart-container"></div>
    
    {% if stats %}
    <div class="stats-grid">
        {% for key, value in stats.items() %}
        <div class="stat-card">
            <h3>{{ key }}</h3>
            <p>{{ value }}{% if '率' in key %}%{% endif %}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
    
    <script>
        var graph = {{ graphJSON | safe }};
        Plotly.newPlot('chart', graph.data, graph.layout);
    </script>
{% endblock %}

templates/dashboard.html
{% extends "base.html" %}
{% block content %}
    <div id="dashboard" class="chart-container"></div>
    <script>
        var graph = {{ graphJSON | safe }};
        Plotly.newPlot('dashboard', graph.data, graph.layout);
    </script>
{% endblock %}
"""

if __name__ == '__main__':
    # 创建模板目录
    os.makedirs('templates', exist_ok=True)
    
    print("电池数据分析系统启动中...")
    print("访问以下地址查看结果：")
    print("1. 良率统计表: http://localhost:5000/yield-stats")
    print("2. TOP10一次不良追踪表: http://localhost:5000/top10-failures")
    print("3. TOP3最终不良表: http://localhost:5000/top3-final-failures")
    print("4. 完整仪表板: http://localhost:5000/dashboard")
    
    # 启动Flask开发服务器
    app.run(host='localhost', port=5000, debug=True)