import os
from pathlib import Path

import requests




def download_book(book_link, bookname):
    book_response = requests.get(
        url=book_link,
    )
    book_response.raise_for_status()
    book_path = f'books/{bookname}.txt'
    with open(book_path, 'wb') as file:
        file.write(book_response.content)
    


def get_full_image_path(image_url, image_folder):
    image_name =  os.path.basename(image_url)
    full_image_path = f'{image_folder}/{image_name}'
    return full_image_path



def download_image(image_url, image_path):
    image_response = requests.get(
        url=image_url,
    )
    image_response.raise_for_status()
    with open(image_path, 'wb') as file:
        file.write(image_response.content)


photos_path = 'books'
Path(photos_path).mkdir(
    parents=True,
    exist_ok=True,
)

for book_id in range(1, 11):
    book_url = f'https://tululu.org/txt.php?id={book_id}'
    download_book(
        book_link=book_url,
        bookname=f'book{book_id}',
    )



"""
photos_path = 'images'
Path(photos_path).mkdir(
    parents=True,
    exist_ok=True,
)
photos_path = 'books'
Path(photos_path).mkdir(
    parents=True,
    exist_ok=True,
)
url = 'https://dvmn.org/media/Requests_Python_Logo.png'
images_path = get_full_image_path(
    image_url=url,
    image_folder=photos_path,
)
download_image(
    image_url=url,
    image_path=images_path,
)
"""