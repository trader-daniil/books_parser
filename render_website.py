from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('index.html')
with open("data_books/books_info.json", "r", encoding="utf-8") as write_file:
    books_info = write_file.read()
books_info = json.loads(books_info)
rendered_page = template.render(books=books_info)
with open('bage_with_books.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)


server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()