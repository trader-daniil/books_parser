import argparse
import os
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm


def check_redirect(book_response):
    if book_response.history:
        raise requests.exceptions.HTTPError


def download_book_text(bookname, book_id):
    params = {'id': book_id}
    downloading_book_url = 'https://tululu.org/txt.php'
    book_response = requests.get(
        url=downloading_book_url,
        params=params,
    )
    check_redirect(book_response=book_response)
    book_response.raise_for_status()
    book_path = f'books/{bookname}.txt'
    with open(book_path, 'w') as file:
        file.write(book_response.text)


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
    comments = booksoup.find_all('div', class_='texts')
    comments = [comment.span.text for comment in comments]
    genres = booksoup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres]
    image_path = booksoup.find('table', class_='d_book').find('img')['src']
    full_image_link = urljoin('https://tululu.org', image_path)
    book_info = {
        'bookname': bookname,
        'comments': comments,
        'genres': genres,
        'image_link': full_image_link,
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
        default=11,
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
            genres = book_info['genres']
            image_link = book_info['image_link']
            download_book_text(
                book_id=book_id,
                bookname=bookname,
            )
            download_book_image(image_link=image_link)
        except requests.exceptions.HTTPError:
            continue
        print(bookname)
        print(('\n').join(comments))
        print((', ').join(genres), '\n')


if __name__ == '__main__':
    main()
