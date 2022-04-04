import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_redirect(book_response):
    if book_response.history:
        raise requests.exceptions.HTTPError


def get_book_image_link(booksoup):
    image_path = booksoup.find('table', class_='d_book').find('img')['src']
    full_image_link = urljoin('https://tululu.org', image_path)
    if requests.get(full_image_link).content:
        return full_image_link


def download_book_text(book_link, bookname):
    book_response = requests.get(url=book_link)
    check_redirect(book_response=book_response)
    book_response.raise_for_status()
    book_path = f'books/{bookname}.txt'
    with open(book_path, 'wb') as file:
        file.write(book_response.content)


def download_book_image(image_link):
    image_response = requests.get(url=image_link)
    check_redirect(book_response=image_response)
    image_response.raise_for_status()
    image_name = urlsplit(image_link).path.split('/')[-1]
    image_path = os.path.join('images', image_name)
    with open(image_path, 'wb') as image:
        image.write(image_response.content)


def parse_book_page(booksoup):
    book_info = {}
    bookname = booksoup.find('body').find(
        'table',
        class_='tabs',
        ).find('h1').text
    bookname = bookname.split('::')[0].strip()
    bookname = sanitize_filename(bookname)
    book_info['bookname'] = bookname
    comments = booksoup.find_all('div', class_='texts')
    comments = [f'{comment.span.text}' for comment in comments]
    book_info['comments'] = comments
    genres = booksoup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres]
    book_info['genres'] = genres
    return book_info


def get_booksoup(book_link):
    book_response = requests.get(url=book_link)
    check_redirect(book_response=book_response)
    book_response.raise_for_status()
    booksoup = BeautifulSoup(book_response.text, 'lxml')
    return booksoup


def main():
    parser = argparse.ArgumentParser(description='Программа скачивает книги')
    parser.add_argument(
        '--start_id',
        default=0,
        type=int
    )
    parser.add_argument(
        '--end_id',
        default=11,
        type=int
    )
    args = parser.parse_args()
    photos_path = 'books'
    Path(photos_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    photos_path = 'images'
    Path(photos_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    for book_id in range(args.start_id, args.end_id):
        book_url = f'https://tululu.org/b{book_id}/'
        downloading_book_url = f'https://tululu.org/txt.php?id={book_id}'
        try:
            booksoup = get_booksoup(book_link=book_url)
        except requests.exceptions.HTTPError:
            continue
        book_info = parse_book_page(booksoup=booksoup)
        bookname = book_info['bookname']
        comments = book_info['comments']
        genres = book_info['genres']
        try:
            download_book_text(
                book_link=downloading_book_url,
                bookname=bookname,
            )
        except requests.exceptions.HTTPError:
            continue
        image_link = get_book_image_link(booksoup=booksoup)
        download_book_image(image_link=image_link)
        print(bookname)
        print(('\n').join(comments))
        print((', ').join(genres), '\n')

    

if __name__ == '__main__':
    main()
