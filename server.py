from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

# Устанавливаем порт
PORT = 8000

# Создаем и запускаем сервер
def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f'Сервер запущен на порту {PORT}')
    print(f'Откройте http://localhost:{PORT} в браузере')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server() 