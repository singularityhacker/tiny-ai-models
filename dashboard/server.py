#!/usr/bin/env python3
"""
Simple HTTP server for the Tiny AI Models Dashboard
Serves the dashboard and provides API endpoints for evaluation results
"""

import json
import os
import glob
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser

class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, results_dir="../results", **kwargs):
        self.results_dir = results_dir
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/models':
            self.handle_get_models()
        elif parsed_path.path == '/api/runs':
            self.handle_get_runs()
        elif parsed_path.path.startswith('/api/data/'):
            self.handle_get_run_data()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_get_models(self):
        """Return list of available models"""
        try:
            models = []
            
            # Scan results directory for model folders
            if os.path.exists(self.results_dir):
                for model_dir in os.listdir(self.results_dir):
                    model_path = os.path.join(self.results_dir, model_dir)
                    if os.path.isdir(model_path) and not model_dir.startswith('.'):
                        # Find JSON files in this model directory
                        json_files = glob.glob(os.path.join(model_path, "results_*.json"))
                        if json_files:
                            models.append({
                                'id': model_dir,
                                'name': model_dir.replace('__', ' ').replace('_', ' ').title(),
                                'run_count': len(json_files)
                            })
            
            self.send_json_response(models)
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_get_runs(self):
        """Return list of runs for a specific model"""
        try:
            query_params = parse_qs(urlparse(self.path).query)
            model_id = query_params.get('model_id', [None])[0]
            
            if not model_id:
                self.send_error_response("model_id parameter required")
                return
            
            model_dir = os.path.join(self.results_dir, model_id)
            if not os.path.exists(model_dir):
                self.send_error_response(f"Model {model_id} not found")
                return
            
            runs = []
            json_files = glob.glob(os.path.join(model_dir, "results_*.json"))
            
            for json_file in json_files:
                filename = os.path.basename(json_file)
                # Extract timestamp from filename
                timestamp_match = filename.replace('results_', '').replace('.json', '')
                
                try:
                    # Parse timestamp - handle the format with hyphens in time
                    # Convert "2025-10-03T14-37-54.407411" to "2025-10-03T14:37:54.407411"
                    iso_timestamp = timestamp_match.replace('-', ':', 2)  # Only replace first 2 hyphens
                    timestamp = datetime.fromisoformat(iso_timestamp)
                    
                    # Try to determine if this is a limited test by reading the config
                    test_type = "Full Evaluation"
                    try:
                        with open(json_file, 'r') as f:
                            data = json.load(f)
                            config = data.get('config', {})
                            limit = config.get('limit')
                            if limit and limit < 1000:
                                test_type = f"Limited Test ({int(limit)} samples)"
                    except:
                        pass
                    
                    runs.append({
                        'id': filename.replace('.json', ''),
                        'timestamp': timestamp.isoformat(),
                        'label': test_type,
                        'filename': json_file
                    })
                except:
                    runs.append({
                        'id': filename.replace('.json', ''),
                        'timestamp': timestamp_match,
                        'label': f"Run {timestamp_match}",
                        'filename': json_file
                    })
            
            # Sort by timestamp (newest first)
            runs.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self.send_json_response(runs)
        except Exception as e:
            self.send_error_response(str(e))
    
    def handle_get_run_data(self):
        """Return data for a specific run"""
        try:
            # Extract run_id from path like /api/data/run_id
            path_parts = self.path.split('/')
            if len(path_parts) < 4:
                self.send_error_response("Invalid path format")
                return
            
            run_id = path_parts[3]
            
            # Find the JSON file
            json_files = glob.glob(os.path.join(self.results_dir, "**", f"{run_id}.json"), recursive=True)
            
            if not json_files:
                self.send_error_response(f"Run {run_id} not found")
                return
            
            # Load and return the JSON data
            with open(json_files[0], 'r') as f:
                data = json.load(f)
            
            self.send_json_response(data)
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def send_error_response(self, message, code=400):
        """Send error response"""
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        error_data = {'error': message}
        self.wfile.write(json.dumps(error_data).encode('utf-8'))

def create_handler(results_dir):
    """Factory function to create handler with results directory"""
    def handler(*args, **kwargs):
        return DashboardHandler(*args, results_dir=results_dir, **kwargs)
    return handler

def start_server(port=8080, results_dir="../results"):
    """Start the dashboard server"""
    handler = create_handler(results_dir)
    
    with HTTPServer(('localhost', port), handler) as httpd:
        print(f"🚀 Tiny AI Models Dashboard starting...")
        print(f"📊 Serving results from: {os.path.abspath(results_dir)}")
        print(f"🌐 Dashboard available at: http://localhost:{port}")
        print(f"📁 API endpoints:")
        print(f"   GET /api/models - List available models")
        print(f"   GET /api/runs?model_id=<id> - List runs for model")
        print(f"   GET /api/data/<run_id> - Get run data")
        print(f"\n⏹️  Press Ctrl+C to stop the server")
        
        # Open browser automatically
        def open_browser():
            import time
            time.sleep(1)
            webbrowser.open(f'http://localhost:{port}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    port = 8080
    results_dir = "../results"
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        results_dir = sys.argv[2]
    
    start_server(port, results_dir)
