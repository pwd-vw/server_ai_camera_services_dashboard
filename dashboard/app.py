#!/usr/bin/env python3
"""
AI Camera Services Dashboard Backend
API สำหรับควบคุมและตรวจสอบสถานะของ services
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import re
from pathlib import Path

# Base directory ของ dashboard (สำหรับโหลด config)
DASHBOARD_DIR = Path(__file__).resolve().parent
CONFIG_PATH = DASHBOARD_DIR / 'config.json'

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)


def load_services_config():
    """โหลด Services config จากไฟล์หรือ environment variables"""
    default_services = {
        'websocket': {
            'name': 'websocket.service',
            'display_name': 'WebSocket Service',
            'description': 'AI Camera Websocket Service',
            'config_path': '/etc/systemd/system/websocket.service',
            'working_dir': '/home/devuser/aicamera/server/ws-service',
            'port': 3001
        },
        'mqtt': {
            'name': 'mqtt.service',
            'display_name': 'MQTT Microservice',
            'description': 'AI Camera MQTT Microservice',
            'config_path': '/etc/systemd/system/mqtt.service',
            'working_dir': '/home/devuser/aicamera/server/mqtt-service',
            'port': None
        },
        'aicamera-mqtt': {
            'name': 'aicamera-mqtt.service',
            'display_name': 'AI Camera MQTT Broker',
            'description': 'AI Camera MQTT Broker (Mosquitto)',
            'config_path': '/etc/systemd/system/aicamera-mqtt.service',
            'mosquitto_config': '/etc/mosquitto/conf.d/aicamera.conf',
            'working_dir': None,
            'port': 1883
        }
    }
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'services' in config:
                    return config['services']
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load config from {CONFIG_PATH}: {e}")
    return default_services


def get_storage_default():
    """ดึง default storage path"""
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'storage' in config and 'default_path' in config['storage']:
                    return config['storage']['default_path']
        except (json.JSONDecodeError, IOError):
            pass
    return '/home/devuser/aicamera/server/storage'


# โหลด Services config
SERVICES = load_services_config()


def run_systemctl_command(command, service_name):
    """รัน systemctl command และคืนค่าผลลัพธ์"""
    try:
        cmd = ['sudo', 'systemctl', command, service_name]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Command timeout',
            'returncode': -1
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'returncode': -1
        }


def get_service_status(service_name):
    """ดึงสถานะของ service"""
    # ดึงข้อมูลจาก systemctl show ก่อน (แม่นยำกว่า)
    show_result = subprocess.run(
        ['systemctl', 'show', '--property=ActiveState,SubState,MainPID,MemoryCurrent,CPUUsageNSec', service_name],
        capture_output=True,
        text=True
    )
    
    details = {}
    if show_result.returncode == 0:
        for line in show_result.stdout.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                details[key] = value
    
    # ตรวจสอบสถานะจาก ActiveState
    active_state = details.get('ActiveState', 'unknown')
    is_active = active_state == 'active'
    
    # ถ้า ActiveState ไม่ชัดเจน ให้ใช้ is-active command
    if active_state == 'unknown':
        result = run_systemctl_command('is-active', service_name)
        is_active = result['success'] and result['output'].strip() == 'active'
        if is_active:
            active_state = 'active'
    
    return {
        'active': is_active,
        'state': active_state,
        'substate': details.get('SubState', 'unknown'),
        'pid': details.get('MainPID', '0'),
        'memory': details.get('MemoryCurrent', '0'),
        'cpu_time': details.get('CPUUsageNSec', '0')
    }


@app.route('/api/services', methods=['GET'])
def get_services():
    """ดึงรายการ services ทั้งหมดพร้อมสถานะ"""
    services_status = []
    
    for key, service_info in SERVICES.items():
        status = get_service_status(service_info['name'])
        services_status.append({
            'id': key,
            'name': service_info['name'],
            'display_name': service_info['display_name'],
            'description': service_info['description'],
            'status': status,
            'port': service_info.get('port'),
            'working_dir': service_info.get('working_dir')
        })
    
    return jsonify({
        'success': True,
        'services': services_status
    })


@app.route('/api/services/<service_id>', methods=['GET'])
def get_service(service_id):
    """ดึงข้อมูล service เฉพาะ"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_info = SERVICES[service_id]
    status = get_service_status(service_info['name'])
    
    return jsonify({
        'success': True,
        'service': {
            'id': service_id,
            'name': service_info['name'],
            'display_name': service_info['display_name'],
            'description': service_info['description'],
            'status': status,
            'port': service_info.get('port'),
            'working_dir': service_info.get('working_dir')
        }
    })


@app.route('/api/services/<service_id>/start', methods=['POST'])
def start_service(service_id):
    """เริ่ม service"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_name = SERVICES[service_id]['name']
    result = run_systemctl_command('start', service_name)
    
    if result['success']:
        status = get_service_status(service_name)
        return jsonify({
            'success': True,
            'message': f'Service {service_name} started successfully',
            'status': status
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to start service'),
            'output': result.get('output', '')
        }), 500


@app.route('/api/services/<service_id>/stop', methods=['POST'])
def stop_service(service_id):
    """หยุด service"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_name = SERVICES[service_id]['name']
    result = run_systemctl_command('stop', service_name)
    
    if result['success']:
        status = get_service_status(service_name)
        return jsonify({
            'success': True,
            'message': f'Service {service_name} stopped successfully',
            'status': status
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to stop service'),
            'output': result.get('output', '')
        }), 500


@app.route('/api/services/<service_id>/restart', methods=['POST'])
def restart_service(service_id):
    """รีสตาร์ท service"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_name = SERVICES[service_id]['name']
    result = run_systemctl_command('restart', service_name)
    
    if result['success']:
        status = get_service_status(service_name)
        return jsonify({
            'success': True,
            'message': f'Service {service_name} restarted successfully',
            'status': status
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Failed to restart service'),
            'output': result.get('output', '')
        }), 500


@app.route('/api/services/<service_id>/logs', methods=['GET'])
def get_service_logs(service_id):
    """ดึง logs ของ service"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_name = SERVICES[service_id]['name']
    lines = request.args.get('lines', 100, type=int)
    
    try:
        result = subprocess.run(
            ['journalctl', '-u', service_name, '-n', str(lines), '--no-pager'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'logs': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/services/<service_id>/config', methods=['GET'])
def get_service_config(service_id):
    """ดึง config ของ service"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_info = SERVICES[service_id]
    config_path = service_info.get('config_path')
    
    if not config_path or not os.path.exists(config_path):
        return jsonify({
            'success': False,
            'error': 'Config file not found'
        }), 404
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # สำหรับ aicamera-mqtt ให้ดึง mosquitto config ด้วย
        additional_config = None
        if service_id == 'aicamera-mqtt' and 'mosquitto_config' in service_info:
            mosquitto_config_path = service_info['mosquitto_config']
            if os.path.exists(mosquitto_config_path):
                with open(mosquitto_config_path, 'r', encoding='utf-8') as f:
                    additional_config = f.read()
        
        return jsonify({
            'success': True,
            'config': content,
            'additional_config': additional_config,
            'path': config_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/services/<service_id>/config', methods=['POST'])
def update_service_config(service_id):
    """อัปเดต config ของ service"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    data = request.get_json()
    if not data or 'config' not in data:
        return jsonify({
            'success': False,
            'error': 'Config content is required'
        }), 400
    
    service_info = SERVICES[service_id]
    config_path = service_info.get('config_path')
    
    if not config_path:
        return jsonify({
            'success': False,
            'error': 'Config path not defined'
        }), 400
    
    try:
        # Backup config ก่อน
        backup_path = f"{config_path}.backup"
        if os.path.exists(config_path):
            subprocess.run(['sudo', 'cp', config_path, backup_path], check=True)
        
        # เขียน config ใหม่
        with open('/tmp/service_config_update', 'w', encoding='utf-8') as f:
            f.write(data['config'])
        
        result = subprocess.run(
            ['sudo', 'cp', '/tmp/service_config_update', config_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Failed to write config: {result.stderr}'
            }), 500
        
        # Reload systemd และ restart service
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        if data.get('restart', True):
            restart_result = run_systemctl_command('restart', service_info['name'])
            if not restart_result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Config updated but restart failed: {restart_result.get("error")}'
                }), 500
        
        return jsonify({
            'success': True,
            'message': 'Config updated successfully',
            'backup_path': backup_path if os.path.exists(backup_path) else None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/services/<service_id>/storage-path', methods=['GET'])
def get_storage_path(service_id):
    """ดึงเส้นทางสำหรับการบันทึกข้อมูล"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    service_info = SERVICES[service_id]
    working_dir = service_info.get('working_dir')
    
    # พยายามหาข้อมูล storage path จาก config หรือ environment
    storage_paths = {}
    
    if working_dir:
        # ตรวจสอบว่ามี config file หรือ .env file หรือไม่
        possible_paths = [
            os.path.join(working_dir, '.env'),
            os.path.join(working_dir, 'config.json'),
            os.path.join(working_dir, 'config', 'config.json'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    if path.endswith('.env'):
                        with open(path, 'r') as f:
                            for line in f:
                                if 'STORAGE' in line.upper() or 'PATH' in line.upper():
                                    if '=' in line:
                                        key, value = line.split('=', 1)
                                        storage_paths[key.strip()] = value.strip()
                    elif path.endswith('.json'):
                        with open(path, 'r') as f:
                            config = json.load(f)
                            if 'storage' in config:
                                storage_paths = config['storage']
                except:
                    pass
    
    # Default storage path
    default_storage = get_storage_default()
    if default_storage and os.path.exists(default_storage):
        storage_paths['default'] = default_storage
    
    return jsonify({
        'success': True,
        'working_dir': working_dir,
        'storage_paths': storage_paths
    })


@app.route('/api/services/<service_id>/storage-path', methods=['POST'])
def update_storage_path(service_id):
    """อัปเดตเส้นทางสำหรับการบันทึกข้อมูล"""
    if service_id not in SERVICES:
        return jsonify({
            'success': False,
            'error': 'Service not found'
        }), 404
    
    data = request.get_json()
    if not data or 'path' not in data:
        return jsonify({
            'success': False,
            'error': 'Storage path is required'
        }), 400
    
    new_path = data['path']
    service_info = SERVICES[service_id]
    working_dir = service_info.get('working_dir')
    
    if not working_dir:
        return jsonify({
            'success': False,
            'error': 'Working directory not defined for this service'
        }), 400
    
    try:
        # สร้าง directory ถ้ายังไม่มี
        os.makedirs(new_path, exist_ok=True)
        
        # อัปเดตใน .env file
        env_path = os.path.join(working_dir, '.env')
        env_content = []
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_content = f.readlines()
        
        # หาและแทนที่ STORAGE_PATH หรือเพิ่มใหม่
        updated = False
        for i, line in enumerate(env_content):
            if line.startswith('STORAGE_PATH=') or line.startswith('DATA_PATH='):
                env_content[i] = f"STORAGE_PATH={new_path}\n"
                updated = True
                break
        
        if not updated:
            env_content.append(f"STORAGE_PATH={new_path}\n")
        
        # เขียนไฟล์ .env
        with open('/tmp/service_env_update', 'w') as f:
            f.writelines(env_content)
        
        result = subprocess.run(
            ['sudo', 'cp', '/tmp/service_env_update', env_path],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': f'Failed to update storage path: {result.stderr}'
            }), 500
        
        # Restart service ถ้าต้องการ
        if data.get('restart', True):
            restart_result = run_systemctl_command('restart', service_info['name'])
            if not restart_result['success']:
                return jsonify({
                    'success': False,
                    'error': f'Storage path updated but restart failed: {restart_result.get("error")}'
                }), 500
        
        return jsonify({
            'success': True,
            'message': 'Storage path updated successfully',
            'new_path': new_path
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'services_count': len(SERVICES)
    })


@app.route('/dashboard/static/<path:filename>')
def serve_dashboard_static(filename):
    """Serve static files เมื่อเข้าผ่าน /dashboard/ path"""
    return send_from_directory(app.static_folder, filename)


@app.route('/')
@app.route('/dashboard/')
def index():
    """Serve dashboard index page - ใช้ relative paths (static/style.css) ให้ทำงานทั้ง direct และ nginx /dashboard/"""
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

