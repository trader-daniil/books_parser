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
    books_per_page = 10
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
        books_on_page = json.load(write_file)
    books_on_page = list(chunked(books_on_page, books_per_page))
    pages_path = 'pages'
    Path(pages_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    server = Server()
    for books_num, books in enumerate(books_on_page, start=1):
        file_with_books_path = f'pages/page_with_books{books_num}.html'
        books_in_block = list(chunked(books, 2))
        on_reload(
            page_num=books_num,
            pages_amount=len(books_on_page) + 1,
            template=template,
            data=books_in_block,
            filename=file_with_books_path,
        )

    server.watch('pages/*.html')
    server.serve(root='.')


if __name__ == '__main__':
    main()
