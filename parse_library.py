import os
from pathlib import Path
from pathvalidate import sanitize_filename

import requests
from bs4 import BeautifulSoup


def check_redirect(book_response):
    if book_response.history:
        requests.exceptions.HTTPError


def get_book_soup(book_link):
    book_response = requests.get(url=book_link)
    book_response.raise_for_status()
    soup = BeautifulSoup(book_response.text, 'lxml')
    return soup


def get_book_name(booksoup):
    bookname = booksoup.find('body').find('table', class_='tabs').find('h1').text
    bookname = bookname.split('::')[0].strip()
    bookname = sanitize_filename(bookname)
    return bookname


def get_book_image(booksoup):
    image_path = booksoup.find('table', class_='d_book').find('img')['src']
    full_image_link = f'https://tululu.org{image_path}'
    return full_image_link


def check_redirect(book_response):
    if book_response.history:
        raise requests.HTTPError


def download_book(book_link, bookname):
    book_response = requests.get(url=book_link)
    check_redirect(book_response)
    book_response.raise_for_status()
    book_path = f'books/{bookname}.txt'
    with open(book_path, 'wb') as file:
        file.write(book_response.content)
    


photos_path = 'books'
Path(photos_path).mkdir(
    parents=True,
    exist_ok=True,
)


for book_id in range(1, 11):
    book_url = f'https://tululu.org/b{book_id}/'
    downloading_book_url = f'https://tululu.org/txt.php?id={book_id}'
    booksoup = get_book_soup(book_link=book_url)
    bookname = get_book_name(booksoup=booksoup)
    try:
        download_book(
            book_link=downloading_book_url,
            bookname=bookname,
        )
    except requests.exceptions.HTTPError:
        continue

    

    

