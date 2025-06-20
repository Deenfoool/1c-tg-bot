import http.server
import socketserver
import os

PORT = 8000

# Путь к текущей директории (где находится index.html)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/docs':
            self.path = 'App.jsx'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

with socketserver.TCPServer(("", PORT), MyHttpRequestHandler) as httpd:
    print(f"Запуск сервера на http://localhost:{PORT}")
    print("Файлы находятся в: ", CURRENT_DIR)
    print("Для остановки нажмите Ctrl+C")
    httpd.serve_forever()
