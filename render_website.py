from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
import json
from livereload import Server
from more_itertools import chunked


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)
template = env.get_template('index.html')
with open("data_books/books_info.json", "r", encoding="utf-8") as write_file:
    books_info = write_file.read()
books_info = json.loads(books_info)
books_info = list(chunked(books_info, 5))


def on_reload(template, data, filename):
    rendered_page = template.render(books_info=data)
    with open(filename, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    pages_path = 'pages'
    Path(pages_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    server = Server()
    for books_num, books in enumerate(books_info):
        file_with_books_path = f'pages/page_with_books{books_num}.html'
        books_list = list(chunked(books, 2))
        server.watch(
            file_with_books_path,
            on_reload(
                template=template,
                data=books_list,
                filename=file_with_books_path),
        )
    server.serve(root='.')

if __name__ == '__main__':
    main()