import shutil

import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import time
import json
import re
import os
from xml.etree import ElementTree
from datetime import datetime

output_folder = "output"
json_files_path = output_folder + "/json"


def fetch_and_resize_image(project_id, image_url):
    response = requests.get(image_url)
    image_data = response.content

    image = Image.open(BytesIO(image_data))

    image.thumbnail((500, 400))

    file_name = add_timestamp_and_limit_length(os.path.basename(image_url))

    image_folder_path = output_folder + "/html/images/" + project_id
    create_folder_if_not_exists(image_folder_path)
    file_path = os.path.join(image_folder_path, file_name)

    image.save(file_path, format="webp")
    return file_name


def sanitize_price_and_return_as_float(price):
    updated_price = re.sub(r'[^\d]', '', price)
    return float(updated_price)


def add_timestamp_and_limit_length(input_string, suffix=".webp"):
    timestamp = str(int(time.time()))

    cleaned_string = re.sub(r'[^a-zA-Z0-9\s]', '', input_string)

    result_string = timestamp + cleaned_string

    result_string = result_string[:30]

    return result_string + suffix


def convert_to_lowercase_with_dashes(input_string, suffix="travel-voyage"):
    underscored_string = re.sub(r'[^a-zA-Z0-9-]', '_', input_string)
    dashed_string = underscored_string.replace(" ", "-")
    lowercase_string = dashed_string.lower()

    return lowercase_string + "-" + suffix


def clean_up(html):
    return html.replace('ebecee', 'fff').replace('http:', 'https:')


def get_descriptions(package_link, element_id):
    html_description = ''
    short_description = ''

    if (package_link):
        response = requests.get(package_link)
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        description = soup.select(element_id)
        if (description):
            html_description = clean_up(str(description[0].prettify()))
            short_description = description[0].text.strip()[:120] + '...'

    return (html_description, short_description)


def create_json_folder_if_not_exists():
    create_folder_if_not_exists(json_files_path)


def create_folder_if_not_exists(folder_path, path_suffix=""):
    if not os.path.exists(folder_path + path_suffix):
        os.makedirs(folder_path + path_suffix)


def print_elapsed_time(start_time):
    elapsed_time = time.time() - start_time
    print(f"Took: {elapsed_time:.2f} seconds")


def add_url_to_sitemap(sitemap_root, loc, image_loc):
    current_datetime = datetime.utcnow()
    lastmod = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    url = ElementTree.SubElement(sitemap_root, "url")

    loc_elem = ElementTree.SubElement(url, "loc")
    loc_elem.text = loc

    lastmod_elem = ElementTree.SubElement(url, "lastmod")
    lastmod_elem.text = lastmod

    image_elem = ElementTree.SubElement(url, "image:image")

    image_loc_elem = ElementTree.SubElement(image_elem, "image:loc")
    image_loc_elem.text = image_loc

    image_caption_elem = ElementTree.SubElement(image_elem, "image:caption")
    image_caption_elem.text = image_loc


def copy_assets():
    source_folder = 'src/public'
    destination_folder = 'output/html'

    os.makedirs(destination_folder, exist_ok=True)

    for item in os.listdir(source_folder):
        source = os.path.join(source_folder, item)
        destination = os.path.join(destination_folder, item)
        if os.path.isdir(source):
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(source, destination)


def save_json_file(project_id, scraped_data):
    # Saving the data to a JSON file
    with open(json_files_path + '/' + project_id + '.json', 'w') as json_file:
        json.dump(scraped_data, json_file, indent=4)
        print("Data saved to json file")
