import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse_library import check_redirect, download_book_text, parse_book_page, download_book_image
from pathlib import Path
import json
import os
from tqdm import tqdm


def get_books_ids(category_link):
    all_hrefs = []
    response = requests.get(url=category_link)
    response.raise_for_status()
    genresoup = BeautifulSoup(response.text, 'lxml')
    all_links = genresoup.select('div.bookimage')
    for link in all_links:
        booklink = link.select_one('a')['href']
        all_hrefs.append(booklink[2:])
    return all_hrefs


def main():
    parser = argparse.ArgumentParser(description='Программа скачивает книги')
    parser.add_argument(
        '--start_page',
        default=1,
        type=int
    )
    parser.add_argument(
        '--end_page',
        default=2,
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
    all_books_ids = []
    books_with_info = []
    fantasy_books = 'https://tululu.org/l55/'
    for page_num in  tqdm(range(args.start_page, args.end_page)):
        fantasy_books_page = urljoin(fantasy_books, str(page_num))
        books_links = get_books_ids(category_link=fantasy_books_page)
        all_books_ids += books_links
    for book_id in tqdm(all_books_ids):
        book_url = f'https://tululu.org/b{book_id}'
        book_response = requests.get(url=book_url)
        try:
            book_response = requests.get(url=book_url)
            check_redirect(book_response=book_response)
            book_response.raise_for_status()
            booksoup = BeautifulSoup(book_response.text, 'lxml')
            book_info = parse_book_page(booksoup=booksoup)
            bookname = book_info['bookname']
            image_link = book_info['image_link']
            filename, image_extension = os.path.splitext(image_link)
            image_name = bookname + image_extension
            book_data = {
                'title': bookname,
                'author': book_info['author'],
                'genres': book_info['genres'],
                'comments': book_info['comments'],
                'img_src': image_name,
            }
            books_with_info.append(book_data)
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
    with open("books_info.json", "a", encoding='utf8') as my_file:
        json.dump(books_with_info, my_file, ensure_ascii=False, indent = 4)


if __name__ == '__main__':
    main()
