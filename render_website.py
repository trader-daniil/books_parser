import json
import math
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload(template, data, filename, pages_amount, page_num):
    next_page = math.ceil(page_num) + 1
    prev_page = math.ceil(page_num) - 1
    pages_info = {
        'pages_amount': pages_amount,
        'next_page': next_page,
        'prev_page': prev_page,
        'page_num': page_num,
    }
    rendered_page = template.render(
        books_info=data,
        pages_info=pages_info,
    )
    with open(filename, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml']),
    )
    template = env.get_template('index.html')
    with open(
        "data_books/books_info.json",
        "r",
        encoding="utf-8",
    ) as write_file:
        books_info = write_file.read()
    books_info = json.loads(books_info)
    books_info = list(chunked(books_info, 20))
    pages_path = 'pages'
    Path(pages_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    server = Server()
    for books_num, books in enumerate(books_info, start=1):
        file_with_books_path = f'pages/page_with_books{books_num}.html'
        books_list = list(chunked(books, 2))
        server.watch(
            file_with_books_path,
            on_reload(
                page_num=books_num,
                pages_amount=len(books_info) + 1,
                template=template,
                data=books_list,
                filename=file_with_books_path),
        )
    server.serve(root='.')


if __name__ == '__main__':
    main()
