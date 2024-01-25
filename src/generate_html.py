import xml.etree.ElementTree as ET
import htmlmin
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from utils import *

env = Environment(
    loader=FileSystemLoader('src/templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

combined_data = []

# Read each JSON file and add its contents to combined_data
for filename in os.listdir(json_files_path):
    if filename.endswith('.json'):
        with open(os.path.join(json_files_path, filename), 'r') as file:
            data = json.load(file)
            combined_data.extend(data)


# Function to read JSON data
def read_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def get_last_update_date(package):
    return package["price"]


def generate_packages_list(package, root_image_path=""):
    price_formatted = float(package['price'])
    price_formatted = f"{price_formatted:,.0f} MAD"

    if package['html_description'] != '':
        link = f""" href="{root_image_path}voyages-organise-maroc-tours/{package['id']}.html" """
    else:
        link = f""" href="{package['external_full_link']}" target="_blank" """

    template = env.get_template('fragment/packages_list.template.j2')
    return template.render(package=package, link=link, price_formatted=price_formatted,
                           root_image_path=root_image_path)


def generate_home_page_html(packages_html, cheapest_packages_list, by_destination_packages, main_page_structured_data):
    template = env.get_template('home_page.template.j2')
    return template.render(packages_html=packages_html, cheapest_packages_list=cheapest_packages_list,
                           by_destination_packages=by_destination_packages,
                           main_page_structured_data=main_page_structured_data)


def generate_voyages_page_html(packages_html, main_page_structured_data):
    template = env.get_template('voyages_page.template.j2')
    return template.render(packages_html=packages_html, main_page_structured_data=main_page_structured_data)


def generate_structured_data(package, url):
    return f"""
{{"@context":"http://schema.org/","@type":"Product","name":"{package['title']}","image":"{package['image_full_url']}","description":"Discover Your Next Adventure and explore the world's most beautiful places with us","brand":{{"@type":"Brand","name":"{package['project_id']}"}},"offers":{{"@type":"Offer","priceCurrency":"MAD","price":"{package['price']}","url":"{url}","itemCondition":"https://schema.org/NewCondition"}}}}
    """


def generate_details_page_html(package, url, structured_data, similar_packages_list):
    template = env.get_template('details_page.template.j2')
    return template.render(package=package, url=url, similar_packages_list=similar_packages_list,
                           product_structured_data=structured_data)


def create_page_url(package):
    if package['html_description'] != '':
        return f"https://www.voyagesorganisemaroc.com/voyages-organise-maroc-tours/{package['id']}.html"
    return 'https://www.voyagesorganisemaroc.com/'


def build_sitemap(sorted_packages):
    sitemap_root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    sitemap_root.set("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")

    add_url_to_sitemap(sitemap_root,
                       "https://www.voyagesorganisemaroc.com/",
                       "https://www.voyagesorganisemaroc.com/logos/bg.webp")

    for package in sorted_packages:
        if package['html_description'] != '':
            add_url_to_sitemap(sitemap_root,
                               f"https://www.voyagesorganisemaroc.com/voyages-organise-maroc-tours/{package['id']}.html",
                               package['image_full_url'])

    tree = ET.ElementTree(sitemap_root)
    tree.write(output_folder + "/html/sitemap.xml", encoding="utf-8", xml_declaration=True)


def generate_html(packages):
    sorted_packages = sorted(packages, key=get_last_update_date)
    build_sitemap(sorted_packages)

    child_pages_id_html_map = {}

    cheapest_packages = sorted_packages[:3]

    # group by destination
    by_destination_packages = defaultdict(list)
    for item in packages:
        by_destination_packages[item["destination"]].append(item)

    cheapest_packages_list = ""
    for package in cheapest_packages:
        cheapest_packages_list += generate_packages_list(package)

    similar_packages_list = ""
    for package in cheapest_packages:
        similar_packages_list += generate_packages_list(package, "../")

    by_dest_packages_list = ""
    for destination, items in by_destination_packages.items():
        items_list = items[:3]
        if len(items) >= 6:
            items_list = items[:6]
        elif 3 <= len(items) <= 6:
            items_list = items[:3]

        if len(items_list) == 3 or (len(items_list) == 6):
            by_dest_packages_list += f"""
                    <div class="container px-4 mx-auto">
                        <h2 id=content class="py-2 text-3xl font-bold text-center sm:text-4xl">
                           {destination}
                        </h2></div>
                    <div
                            style="margin-left: auto;margin-right: auto;max-width: 1100px;"
                            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4 md:p-6">
                """

            for item in items_list:
                by_dest_packages_list += generate_packages_list(item)

        by_dest_packages_list += "</div>"

    main_page_structured_data = ""
    packages_list_html_content = ""
    for package in sorted_packages:
        packages_list_html_content += generate_packages_list(package)

        if package['html_description'] != '':
            url = create_page_url(package)
            product_structured_data = generate_structured_data(package, url)
            main_page_structured_data += """<script type="application/ld+json">""" + product_structured_data + "</script>"
            child_pages_id_html_map[package['id']] = generate_details_page_html(package, url, product_structured_data,
                                                                                similar_packages_list)
        else:
            child_pages_id_html_map[package['id']] = ''

    home_page_html_content = generate_home_page_html(packages_list_html_content, cheapest_packages_list,
                                                     by_dest_packages_list, main_page_structured_data)

    voyages_page_html_content = generate_voyages_page_html(packages_list_html_content, main_page_structured_data)

    return home_page_html_content, child_pages_id_html_map, voyages_page_html_content


if __name__ == "__main__":
    start_time = time.time()

    copy_assets()
    create_folder_if_not_exists(output_folder + "/html/voyages-organise-maroc-tours")

    html_output, child_pages_map, voyages_page_html_content = generate_html(combined_data)

    with open(output_folder + "/html/index.html", 'w') as html_file:
        html_file.write(htmlmin.minify(html_output))

    with open(output_folder + "/html/voyages.html", 'w') as html_file:
        html_file.write(htmlmin.minify(voyages_page_html_content))

    for page_id, html_content in child_pages_map.items():
        if html_content:
            with open(output_folder + "/html/voyages-organise-maroc-tours/" + page_id + ".html", 'w') as html_file:
                html_file.write(htmlmin.minify(html_content))
    print("HTML file created")

    print_elapsed_time(start_time)
