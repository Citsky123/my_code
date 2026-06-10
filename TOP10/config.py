# config.py
"""
系统配置文件
请根据你的实际环境修改这些配置
"""

# 数据库配置
DATABASE_CONFIG = {
    'development': {
        'dialect': 'mysql',
        'driver': 'mysqlconnector',
        'username': 'dev_user',
        'password': 'dev_password',
        'host': 'localhost',
        'port': '3306',
        'database': 'battery_quality_dev'
    },
    'production': {
        'dialect': 'mysql',
        'driver': 'mysqlconnector',
        'username': 'prod_user',
        'password': 'prod_password',
        'host': 'prod-db.example.com',
        'port': '3306',
        'database': 'battery_quality'
    }
}

# 查询参数默认值
DEFAULT_PARAMS = {
    'start_date': '2024-01-01',
    'end_date': '2024-12-31',
    'model_type': 'ALL'  # 或默认机种
}

# 图表配置
CHART_CONFIG = {
    'colors': {
        'pass': '#2ecc71',
        'fail': '#e74c3c',
        'warning': '#f39c12',
        'info': '#3498db'
    },
    'chart_height': 500,
    'chart_width': 800
}

# 系统路径
PATHS = {
    'data_results': './results',
    'templates': './templates',
    'logs': './logs'
}