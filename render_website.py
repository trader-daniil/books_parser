import json
from logging import root
import math
import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']),
    )
    template = env.get_template('index.html')
    books_per_page = 10
    with open(
        "data_books/books_info.json",
        "r",
        encoding="utf-8",
    ) as write_file:
        books_on_page = json.load(write_file)
    books_on_page = list(chunked(books_on_page, books_per_page))
    for books_num, books in enumerate(books_on_page, start=1):
        file_with_books_path = f'pages/page_with_books{books_num}.html'
        books_in_block = list(chunked(books, 2))
        next_page = math.ceil(books_num) + 1
        prev_page = math.ceil(books_num) - 1
        pages_info = {
            'pages_amount': len(books_on_page) + 1,
            'next_page': next_page,
            'prev_page': prev_page,
            'page_num': books_num,
        }
        rendered_page = template.render(
            books_info=books_in_block,
            pages_info=pages_info,
        )
        with open(file_with_books_path, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    templates_path = 'pages/'
    Path(templates_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    server = Server()
    server.watch('pages/*.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()
