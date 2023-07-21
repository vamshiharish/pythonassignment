import requests
from bs4 import BeautifulSoup
import csv

def get_product_details(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_description = soup.find('div', {'id': 'productDescription'})
    asin = soup.find('th', string='ASIN').find_next_sibling('td').text.strip() if soup.find('th', string='ASIN') else 'N/A'
    manufacturer = soup.find('th', string='Manufacturer').find_next_sibling('td').text.strip() if soup.find('th', string='Manufacturer') else 'N/A'

    return product_description.text.strip() if product_description else 'N/A', asin, manufacturer

def get_product_listings(pages):
    base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}'

    all_products = []
    for page in range(1, pages + 1):
        url = base_url.format(page)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        for product in soup.find_all('div', {'data-component-type': 's-search-result'}):
            product_url = product.find('a', {'class': 'a-link-normal'})['href']
            product_name = product.find('span', {'class': 'a-text-normal'}).text.strip()
            product_price = product.find('span', {'class': 'a-offscreen'}).text.strip()
            rating = product.find('span', {'class': 'a-icon-alt'}).text.split()[0] if product.find('span', {'class': 'a-icon-alt'}) else 'N/A'
            num_reviews = product.find('span', {'class': 'a-size-base'}).text.strip() if product.find('span', {'class': 'a-size-base'}) else 'N/A'

            all_products.append({
                'Product URL': product_url,
                'Product Name': product_name,
                'Product Price': product_price,
                'Rating': rating,
                'Number of Reviews': num_reviews
            })

    return all_products

if __name__ == "__main__":
    # Set the number of pages to scrape for product listings
    num_pages = 20

    # Scrape product listings
    scraped_data = get_product_listings(num_pages)

    # Scrape product details for each URL
    for product in scraped_data:
        url = 'https://www.amazon.in' + product['Product URL']
        description, asin, manufacturer = get_product_details(url)

        product['Description'] = description
        product['ASIN'] = asin
        product['Manufacturer'] = manufacturer

    # Export data to CSV
    with open('amazon_products.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Product URL', 'Product Name', 'Product Price', 'Rating', 'Number of Reviews', 'Description', 'ASIN', 'Manufacturer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for product in scraped_data:
            writer.writerow(product)
