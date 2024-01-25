from utils import *

start_time = time.time()

create_json_folder_if_not_exists()

id = 'vacancia.ma'
base_url = 'https://vacancia.ma'
url = 'https://vacancia.ma/voyages'
source_logo = 'logos/vacancia.ma.webp'

response = requests.get(url)
html = response.content

soup = BeautifulSoup(html, 'html.parser')
packages = soup.find_all('div', class_='pbox')

scraped_data = []
for package in packages:
    image_tag = package.find('div', class_='pbox-image').find('img')
    link_tag = package.find('div', class_='pbox-image').find('a', href=True)

    title = package.find('h1', class_='pbox-title').text.strip()
    destination = package.find('div', class_='pbox-destination').text.strip().replace("Maroc", "Morocco")
    price = package.find('p', class_='price').text.strip()
    price = sanitize_price_and_return_as_float(price)
    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''
    package_link = link_tag['href'] if link_tag else ''

    html_description, short_description = get_descriptions(base_url + package_link, '#page-wrap')

    thumbnail = fetch_and_resize_image(id, base_url + image_url)

    scraped_data.append({
        'id': convert_to_lowercase_with_dashes(title, id),
        'project_id': id,
        'title': title,
        'destination': destination,
        'price': price,
        'short_description': short_description,
        'html_description': '',
        'image_url': image_url,
        'base_url': base_url,
        'image_full_url': base_url + image_url,
        'external_link': package_link,
        'external_full_link': base_url + package_link,
        'source': url,
        'thumbnail': thumbnail,
        'last_update_date': datetime.now().isoformat(),
        'source_logo': source_logo
    })

save_json_file(id, scraped_data)

print_elapsed_time(start_time)
