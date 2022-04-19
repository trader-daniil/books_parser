import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import json

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm


def check_redirect(book_response):
    if book_response.history:
        raise requests.exceptions.HTTPError


def download_book_text(bookname, book_id):
    params = {'id': book_id}
    downloading_book_url = 'https://tululu.org/txt.php?id=1'
    book_response = requests.get(
        url=downloading_book_url,
        params=params,
    )
    check_redirect(book_response=book_response)
    book_response.raise_for_status()
    book_path = f'books/{bookname}.txt'
    with open(book_path, 'wb') as file:
        file.write(book_response.content)


def download_book_image(image_link, image_name):
    image_response = requests.get(url=image_link)
    check_redirect(book_response=image_response)
    image_response.raise_for_status()
    image_path = os.path.join('images', image_name)
    with open(image_path, 'wb') as image:
        image.write(image_response.content)


def parse_book_page(booksoup):
    book_info = {}
    bookselector = 'body .tabs h1'
    bookname = booksoup.select_one(bookselector).text
    author = bookname.split('::')[-1].strip()
    bookname = bookname.split('::')[0].strip()
    bookname = sanitize_filename(bookname)
    comments = booksoup.select('div.texts')
    comments = [comment.span.text for comment in comments]
    genres = booksoup.select('span.d_book a')
    genres = [genre.text for genre in genres]
    image_path = booksoup.select_one('table.d_book img')['src']
    full_image_link = urljoin('https://tululu.org', image_path)
    book_info = {
        'bookname': bookname,
        'comments': comments,
        'genres': genres,
        'image_link': full_image_link,
        'author': author,
    }
    return book_info


def main():
    parser = argparse.ArgumentParser(description='Программа скачивает книги')
    parser.add_argument(
        '--start_id',
        default=0,
        type=int
    )
    parser.add_argument(
        '--end_id',
        default=10,
        type=int
    )
    args = parser.parse_args()
    books_path = 'books'
    Path(books_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    photos_path = 'images'
    Path(photos_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    for book_id in tqdm(range(args.start_id, args.end_id)):
        book_url = f'https://tululu.org/b{book_id}/'
        try:
            book_response = requests.get(url=book_url)
            check_redirect(book_response=book_response)
            book_response.raise_for_status()
            booksoup = BeautifulSoup(book_response.text, 'lxml')
            book_info = parse_book_page(booksoup=booksoup)
            bookname = book_info['bookname']
            comments = book_info['comments']
            author = book_info['author']
            genres = book_info['genres']
            image_link = book_info['image_link']
            filename, image_extension = os.path.splitext(image_link)
            image_name = bookname + image_extension
            download_book_text(
                book_id=book_id,
                bookname=bookname,
            )
            download_book_image(
                image_link=image_link,
                image_name=image_name,
            )
        except requests.exceptions.HTTPError:
            continue
        print(bookname)
        print(author)
        print(('\n').join(comments))
        print((', ').join(genres), '\n')


if __name__ == '__main__':
    main()
