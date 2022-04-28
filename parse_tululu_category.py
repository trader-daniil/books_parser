import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from parse_library import (
                           check_redirect,
                           download_book_text,
                           parse_book_page,
                           download_book_image)
from pathlib import Path
import json
import os
from tqdm import tqdm


def get_books_ids(category_link):
    hrefs = []
    response = requests.get(url=category_link)
    response.raise_for_status()
    genresoup = BeautifulSoup(response.text, 'lxml')
    links = genresoup.select('div.bookimage')
    for link in links:
        booklink = link.select_one('a')['href']
        hrefs.append(booklink[2:])
    return hrefs


def get_total_pages(tululu_link):
    paginator_selector = 'table.tabs p.center a'
    response = requests.get(url=tululu_link)
    response.raise_for_status()
    pagesoup = BeautifulSoup(response.text, 'lxml')
    paginator = pagesoup.select(paginator_selector)
    return paginator[-1].text


def main():
    parser = argparse.ArgumentParser(description='Программа скачивает книги')
    fantasy_books_url = 'https://tululu.org/l55/'
    total_pages = get_total_pages(tululu_link=fantasy_books_url)
    parser.add_argument(
        '--start_page',
        default=1,
        type=int
    )
    parser.add_argument(
        '--end_page',
        default=total_pages,
        type=int
    )
    parser.add_argument(
        '--dest_folder',
        default='data_books',
        type=str,
    )
    parser.add_argument(
        '--skip_imgs',
        action='store_true',
    )
    parser.add_argument(
        '--skip_txt',
        action='store_true',
    )
    args = parser.parse_args()
    books_path = f'{args.dest_folder}/books'
    Path(books_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    photos_path = f'{args.dest_folder}/images'
    Path(photos_path).mkdir(
        parents=True,
        exist_ok=True,
    )
    books_ids = []
    books_with_info = []
    for page_num in tqdm(range(args.start_page, args.end_page)):
        fantasy_books_page = urljoin(fantasy_books_url, str(page_num))
        page_books_ids = get_books_ids(category_link=fantasy_books_page)
        books_ids += page_books_ids
    for book_id in tqdm(books_ids):
        book_url = f'https://tululu.org/b{book_id}'
        try:
            book_response = requests.get(url=book_url)
            check_redirect(book_response=book_response)
            book_response.raise_for_status()
            booksoup = BeautifulSoup(book_response.text, 'lxml')
            book_info = parse_book_page(booksoup=booksoup)
            bookname = book_info['bookname'].replace('.', ' ')
            #bookname = book_info['bookname']
            book_path = f'{books_path}/{bookname}.txt'
            if not args.skip_txt:
                book_info['txt_path'] = book_path
                download_book_text(
                    book_path=book_path,
                    book_id=book_id,
                )
            if args.skip_imgs:
                continue
            image_link = book_info['image_link']
            filename, image_extension = os.path.splitext(image_link)
            image_name = bookname + image_extension
            book_info['img_src'] = f'{args.dest_folder}/images/{image_name}'
            image_path = os.path.join(photos_path, image_name)
            download_book_image(
                image_link=image_link,
                image_path=image_path,
            )
            if os.path.getsize(image_path) < 5000:
                book_info['img_src'] = 'static/book_image_for_none.jpg'
            books_with_info.append(book_info)
        except requests.exceptions.HTTPError:
            continue
    with open(
        f'{args.dest_folder}/books_info.json',
        "w",
        encoding='utf8',
    ) as file:
        json.dump(books_with_info, file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()
