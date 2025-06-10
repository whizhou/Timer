#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Timer后端入口文件
使用方法: python run.py [--host HOST] [--port PORT] [--debug]
"""

import argparse
from app import create_app

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='Timer后端服务')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='主机地址')
    parser.add_argument('--port', type=int, default=5000, help='端口号')
    parser.add_argument('--debug', action='store_true', help='是否开启调试模式')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 导入配置
    from config.config import DevelopmentConfig
    
    # 创建应用
    app = create_app(DevelopmentConfig)
    
    print(f"Timer后端服务启动中...")
    print(f"访问地址: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main() 