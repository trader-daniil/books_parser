from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('index.html')
with open("data_books/books_info.json", "r", encoding="utf-8") as write_file:
    books_info = write_file.read()
books_info = json.loads(books_info)


def on_reload(template, data, filename):
    rendered_page = template.render(books=data)
    with open(filename, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    server = Server()
    server.watch(
        'bage_with_books.html',
        on_reload(
            template=template,
            data=books_info,
            filename='bage_with_books.html'),
    )
    server.serve(root='.')

if __name__ == '__main__':
    main()

