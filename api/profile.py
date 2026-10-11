import json
import re
from http.server import BaseHTTPRequestHandler
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # استخراج اليوزرنيم من الـ URL
        username = self.path.split('?username=')[-1] if '?username=' in self.path else ''
        username = username.replace('@', '').strip()
        
        if not username:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Username required'}).encode())
            return
        
        try:
            url = f"https://www.tiktok.com/@{username}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': f'TikTok returned {response.status_code}'}).encode())
                return
            
            # استخراج البيانات من HTML
            script_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>([\s\S]*?)</script>', response.text)
            
            if script_match:
                data = json.loads(script_match.group(1))
                user_detail = data.get('__DEFAULT_SCOPE__', {}).get('user/detail', {}).get('userInfo', {})
                
                if user_detail:
                    user = user_detail.get('user', {})
                    stats = user_detail.get('stats', {})
                    
                    result = {
                        'username': user.get('uniqueId', ''),
                        'nickname': user.get('nickname', ''),
                        'avatarLarger': user.get('avatarLarger', ''),
                        'avatarMedium': user.get('avatarMedium', ''),
                        'avatarThumb': user.get('avatarThumb', ''),
                        'signature': user.get('signature', ''),
                        'verified': user.get('verified', False),
                        'followers': stats.get('followerCount', 0),
                        'following': stats.get('followingCount', 0),
                        'likes': stats.get('heartCount', 0),
                        'videos': stats.get('videoCount', 0),
                    }
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(result).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'User not found'}).encode())
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Could not parse TikTok page'}).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
