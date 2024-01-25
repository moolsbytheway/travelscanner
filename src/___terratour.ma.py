from utils import *

start_time = time.time()

create_json_folder_if_not_exists()

id = 'terratour.ma'
base_url = 'https://terratour.ma'
url = 'https://terratour.ma/en/morocco-tours/'
source_logo = 'logos/terratour.ma.webp'

response = requests.get(url)
html = response.content

soup = BeautifulSoup(html, 'html.parser')
packages = soup.find_all('div', class_='tour_container')

scraped_data = []
for package in packages:
    image_tag = package.find('img')
    link_tag = package.find('a', href=True)

    title = package.find('h3').text.strip()
    price = package.find('span', class_='price').text.strip()
    price = sanitize_price_and_return_as_float(price)
    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''
    package_link = link_tag['href'] if link_tag else ''

    thumbnail = fetch_and_resize_image(id, image_url)

    html_description, short_description = get_descriptions(package_link, '#single_tour_desc')

    scraped_data.append({
        'id': convert_to_lowercase_with_dashes(title, id),
        'project_id': id,
        'title': title,
        'destination': 'Morocco',
        'price': price,
        'image_url': image_url,
        'base_url': base_url,
        'image_full_url': image_url,
        'external_link': package_link,
        'external_full_link': package_link,
        'source': url,
        'thumbnail': thumbnail,
        'html_description': html_description,
        'short_description': short_description,
        'last_update_date': datetime.now().isoformat(),
        'source_logo': source_logo
    })

save_json_file(id, scraped_data)

print_elapsed_time(start_time)
