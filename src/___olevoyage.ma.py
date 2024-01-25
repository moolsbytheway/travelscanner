from langdetect import detect
from utils import *

start_time = time.time()

create_json_folder_if_not_exists()

id = 'olevoyages.ma'
url = 'https://www.olevoyages.ma/'
source_logo = 'logos/olevoyages.ma.webp'

response = requests.get(url)
html = response.content

soup = BeautifulSoup(html, 'html.parser')
packages = soup.find_all('div', class_='card mb-0 item-card2-card')

scraped_data = []
for package in packages:
    price = package.find('h4', class_='mb-0').text.strip()
    price = sanitize_price_and_return_as_float(price)
    title = package.find('h4', class_='font-weight-bold mb-3').text.strip()
    location = package.find('li').text.strip().replace(" -  Places", "")

    link_tag = package.find('a', href=True)
    package_link = link_tag['href'] if link_tag else ''

    image_tag = package.find('img', class_='cover-image')
    image_url = image_tag['src'] if image_tag and 'src' in image_tag.attrs else ''

    html_description, short_description = get_descriptions(package_link, '#collapseOne .card-body')

    thumbnail = fetch_and_resize_image(id, url + image_url)

    if detect(title) != 'ar':
        scraped_data.append({
            'id': convert_to_lowercase_with_dashes(title, id),
            'project_id': id,
            'title': title,
            'destination': location,
            'price': price,
            'html_description': html_description,
            'short_description': short_description,
            'image_url': image_url,
            'base_url': url,
            'image_full_url': url + image_url,
            'external_link': package_link,
            'external_full_link': package_link,
            'source': url,
            'thumbnail': thumbnail,
            'last_update_date': datetime.now().isoformat(),
            'source_logo': source_logo
        })

save_json_file(id, scraped_data)

print_elapsed_time(start_time)
