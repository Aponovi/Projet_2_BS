# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import csv
import hashlib
import shutil
import os

books_links = []
books_results = []
os.mkdir('Images')

start_url = 'http://books.toscrape.com/catalogue/category/books_1/index.html'
response = requests.get(start_url)


def list_books(url):
    response_list = requests.get(url)
    soup = BeautifulSoup(response_list.text, 'html.parser')

    if response_list.ok:
        books = soup.findAll('h3')
        for book in books:
            a = book.find('a')
            link = a['href']
            link = link.replace('../../', 'http://books.toscrape.com/catalogue/')
            books_links.append(link)
            description_book(link)
        next_page = soup.find('li', class_='next')
        if next_page is not None:
            list_books('http://books.toscrape.com/catalogue/category/books_1/' + next_page.find('a').attrs['href'])


def description_book(url):
    response_book = requests.get(url)
    response_book.encoding = 'utf-8'
    soup_book = BeautifulSoup(response_book.text, 'html.parser')
    if response_book.ok:
        product_page_url = url
        tds = soup_book.findAll('td')
        upc = tds[0].text
        title = soup_book.find('h1').text
        price_including_tax = tds[3].text
        price_excluding_tax = tds[2].text
        number_available = re.search(r"[^\D]+", tds[5].text).group()
        div_description = soup_book.find('div', id='product_description')
        product_description = ''
        if div_description is not None:
            product_description = div_description.find_next_sibling('p').text
        category = soup_book.find('ul', class_='breadcrumb').findAll('a')[2].text
        review_rating = soup_book.find('p', class_='star-rating').attrs['class'][1]
        review_rating = review_rating.replace(
            "One", "1").replace("Two", "2").replace("Three", "3").replace("Four", "4").replace("Five", "5")
        image_url = soup_book.find('img').attrs['src'].replace('../../', 'http://books.toscrape.com/')
        book = {'product_page_url': product_page_url,
                'universal_product_code (upc)': upc,
                'title': title,
                'price_including_tax': price_including_tax,
                'price_excluding_tax': price_excluding_tax,
                'number_available': number_available,
                'product_description': product_description,
                'category': category,
                'review_rating': review_rating,
                'image_url': image_url,
                'image': hashlib.sha1(image_url.encode('utf-8')).hexdigest()
                }
        books_results.append(book)
        csv_manager(book)
        image_manager(book)


def csv_manager(item):
    vide = False
    with open(item["category"] + '.csv', 'a', newline='') as file:
        pass

    with open(item["category"] + '.csv', 'r+', newline='') as file:
        line = file.readline()
        if line == '':
            vide = True

    with open(item["category"] + '.csv', 'a', newline='') as file:
        writer = csv.DictWriter(file, [
            'product_page_url',
            'universal_product_code (upc)',
            'title',
            'price_including_tax',
            'price_excluding_tax',
            'number_available',
            'product_description',
            'category',
            'review_rating',
            'image_url',
            'image'])
        if vide:
            writer.writeheader()
        writer.writerow(item)
    return item


def image_manager(item):
    image_url = item['image_url']
    r = requests.get(image_url, stream=True)
    if r.ok:
        r.raw.decode_content = True
        with open('Images/' + item['image']+'.jpg', 'wb') as f:
            shutil.copyfileobj(r.raw, f)


list_books('http://books.toscrape.com/catalogue/category/books_1/index.html')
print(len(books_results))
