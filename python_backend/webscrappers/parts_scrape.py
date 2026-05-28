from bs4 import BeautifulSoup
import requests
import time
import json
from dotenv import load_dotenv
import os
    
load_dotenv()

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")

def scrape_product_page(product_page_url, product): 
    """
    Scrapes a product page for part details, popular models and brands and related parts links.

    Args:
        product_page_url (str): The URL of the product page to scrape.
        product (str): A label or identifier for the product (used for return labeling).

    Returns:
        tuple:
            - dict: A dictionary containing:
                - "product" (str): The product type - Dishwasher, Refrigerator, etc.
                - "popular parts" (list of dict): Part information including names, numbers, descriptions, and instructions.
                - "models" (list of str): Model names extracted from the page.
                - "brands" (list of str): Brand names extracted from the page.
                - "common problems fixes" (str or None): Text describing common problems and fixes if found.
            - list of str: Links related to the brands.
            - list of str: Links related to the models.
            - list of str: Links to product related parts.
    """
    payload = { 'api_key': SCRAPER_API_KEY, 'url': product_page_url}
    page = requests.get('https://api.scraperapi.com/', params=payload)
    if page.status_code != 200:
        print(page.status_code)
        return None, [], [], []
    else:
        soup = BeautifulSoup(page.content, "html.parser")
        popular_parts = []
        for popular_part_div in soup.find_all("div", class_="nf__part__detail"):
            part_name = popular_part_div.find_all("a", class_="nf__part__detail__title")[0]
            if part_name:
                part_name = part_name.text
                part_name = part_name.replace('\n', '')
            select_no = popular_part_div.find("div", class_="nf__part__detail__part-number").get_text()
            manufacturing_no = popular_part_div.find("div", class_="nf__part__detail__part-number mb-2").get_text()
            manufacturing_el = popular_part_div.find("div", class_="nf__part__detail__part-number mb-2")
            if manufacturing_el:
                description = manufacturing_el.next_sibling.strip()
            # Find the 'Installation Instructions' div
            instruction_div = popular_part_div.find('div', class_='nf__part__detail__instruction__quote mt-1')
            # Extract the text from the <span> tag inside the instruction div
            instruction_text = instruction_div.find('span', class_='d-block').get_text()
            # Clean up the text by stripping unnecessary whitespace and newlines
            cleaned_installation_text = ' '.join(instruction_text.split())
            part_info = {"part name": part_name,
            "PartSelect Number": select_no,
            "Manufacturer Part Number": manufacturing_no,
            "description": description,
            "Installation instructions": cleaned_installation_text
            }
            popular_parts.append(part_info)
        # extract all links 
        uls = soup.find_all('ul', class_='nf__links')
        # List of tuples: (link text, href)
        links = [
            (a.get_text(strip=True), a['href'])
            for ul in uls
            for li in ul.find_all('li')
            for a in li.find_all('a', href=True)
        ]   
        # extract brand links, related parts links, model links 
        brands = []
        brand_links = []
        models = []
        model_links = []
        related_parts_links = []
        for text, link in links:
            if 'Refrigerator Parts' in text:
                brands.append(text)
                brand_links.append(link)
            elif '/Models/' in link:
                models.append(text)
                model_links.append(link)
            else:
                related_parts_links.append(link)

        # extract common problems
        common_problems = soup.find("div", class_="rich-content mb-4")
        if common_problems:
            common_problems = common_problems.get_text()

        return {
            "product": product,
            "popular parts": popular_parts,
            "models": models,
            "brands": brands,
            "common problems fixes": common_problems
        }, brand_links, model_links, related_parts_links


def scrape_model_links(models, model_page_links, filepath):
    """
    Scrapes parts data for each product model from its product page and appends the results to data file.

    Args:
        models (list of str): List of model.
        model_page_links (list of str): List of relative URLs to model pages.
        filepath (str): Path to the output file where the scraped data will be appended as JSON lines.
    """
    assert(len(models) == len(model_page_links))
    base_url = 'https://www.partselect.com/'
    for model, model_link in zip(models, model_page_links):
        time.sleep(2)
        payload = { 'api_key': SCRAPER_API_KEY, 'url': base_url + model_link}
        page = requests.get('https://api.scraperapi.com/', params=payload)
        # page = requests.get(base_url + model_link, headers=headers)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            parts = []
            for part_div in soup.find_all("div", class_="d-flex flex-col justify-content-between"):
            # for part_div in soup.find_all("div", class_="mega-m__part"):
                part_name = part_div.find("a", class_="bold mb-1 mega-m__part__name")
                select_no_div = part_name.next_sibling.next_sibling.next_sibling.next_sibling
                select_no = select_no_div.get_text() if select_no_div else 'N/A'
                manufacturing_no = select_no_div.next_sibling.next_sibling.get_text() if select_no_div else 'N/A'
                description = select_no_div.next_sibling.next_sibling.next_sibling.strip()
                price = part_div.find("div", class_="mega-m__part__price mt-2")
                if price:
                    price= price.get_text()
                part_info = {"part name": part_name.get_text() if part_name else "N/A",
                    "PartSelect Number": select_no,
                    "Manufacturer Part Number": manufacturing_no,
                    "description": description,
                    "Installation instructions": 'N/A',
                    "price": price.replace('\n', '').rstrip() if price else 'N/A'
                    }
                parts.append(part_info)
            model_info = {
                "model": model,
                "compatible parts": parts
            }
            
            with open(filepath, 'a') as f:
                f.write(json.dumps(model_info) + '\n')
        else: 
            print(f"Could not extract model: {model}")

def scrape_related_parts(related_parts_links, filepath):
    """
    Scrapes parts information from related parts links and appends results to a file.

    Args:
        related_parts_links (list of str): List of relative URLs pointing to related parts pages.
        filepath (str): Path to the output file where the scraped data will be appended as JSON lines.
    """
    base_url = 'https://www.partselect.com/'
    for related_link in related_parts_links[1:]:
        time.sleep(2)
        payload = { 'api_key': SCRAPER_API_KEY, 'url': base_url + related_link}
        page = requests.get('https://api.scraperapi.com/', params=payload)
        if page.status_code == 200:
            soup = BeautifulSoup(page.content, "html.parser")
            group_name = soup.find("h2", class_="section-title bold mt-4 mb-3 mb-sm-4")
            parts = []
            for popular_part_div in soup.find_all("div", class_="nf__part mb-3"):
                part_name = popular_part_div.find_all("a", class_="nf__part__detail__title")[0]
                if part_name:
                    part_name = part_name.text
                    part_name = part_name.replace('\n', '')
                select_no = popular_part_div.find("div", class_="nf__part__detail__part-number").get_text()
                manufacturing_no = popular_part_div.find("div", class_="nf__part__detail__part-number mb-2").get_text()
                manufacturing_el = popular_part_div.find("div", class_="nf__part__detail__part-number mb-2")
                if manufacturing_el:
                    description = manufacturing_el.next_sibling.strip()
                # Find the 'Installation Instructions' div
                instruction_div = popular_part_div.find('div', class_='nf__part__detail__instruction__quote mt-1')
                # Extract the text from the <span> tag inside the instruction div
                instruction_text = instruction_div.find('span', class_='d-block').get_text() if instruction_div else 'N/A'
                # Clean up the text by stripping unnecessary whitespace and newlines
                cleaned_installation_text = ' '.join(instruction_text.split())
                price = popular_part_div.find("div", class_="mt-sm-2 price")
                if price:
                    price= price.get_text()
                part_info = {"part name": part_name,
                    "PartSelect Number": select_no,
                    "Manufacturer Part Number": manufacturing_no,
                    "description": description,
                    "Installation instructions": cleaned_installation_text,
                    "price": price.replace('\n', '').rstrip() if price else 'N/A'
                    }
                parts.append(part_info)
            part_group_info = {
                "dishwasher part type": group_name.get_text().rstrip().replace('\n', '') if group_name else 'N/A',
                "popular parts": parts
            }
            
            with open(filepath, 'a') as f:
                f.write(json.dumps(part_group_info) + '\n')
        else: 
            print(f"Could not extract related link: {related_link}")


def scrape_repair_page(repair_link, product, filepath):
    base_url = "https://www.partselect.com"
    payload = { 'api_key': SCRAPER_API_KEY, 'url': repair_link}
    page = requests.get('https://api.scraperapi.com/', params=payload)
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        symptoms_div = soup.find("div", class_="symptom-list")
        problems = symptoms_div.find_all("a", class_="row text-black no-underline b-b")
        product_problems = []
        for problem in problems:
            problem_title = problem.find("h3", class_="title-md mb-3")
            problem_name = problem_title.get_text()
            troubleshooting_page_link = problem['href'] if problem and 'href' in problem.attrs else None
            problem_description = problem.find("p").get_text()
            problem_info = {
                "name of problem": product + problem_name,
                "troubleshooting steps and videos link": base_url + troubleshooting_page_link,
                "parts to examine": problem_description
            }
            print(problem_info)
            product_problems.append(problem_info)
        with open('./data/fridge_repair.jsonl', 'a') as f:
            f.write(json.dumps(product_problems) + '\n')
    else:
        print("Scraping failed")           




if __name__ == "__main__":

    print("Scraping product page ...")
    product_info_json, brand_links, model_links, related_parts_links = scrape_product_page("https://www.partselect.com/Refrigerator-Parts.htm", 'Dishwashers')
    with open('./data/fridge_cleaned_data.jsonl', 'a') as f:
        f.write(json.dumps(product_info_json) + '\n')

    # scrape popular models info
    print("Scraping model information and parts...")
    scrape_model_links(product_info_json['models'], model_links, './data/fridge_cleaned_data.jsonl')
    
    # scrape related links
    print("Scraping related parts...")
    scrape_related_parts(related_parts_links, './data/fridge_cleaned_data.jsonl')

    # scrape repairs page
    print("Scraping repair page")
    repair_link = "https://www.partselect.com/Repair/Refrigerator/"
    product =  "Refrigerator "
    scrape_repair_page(repair_link, product, "./data/fridge_repair.jsonl")


    print("Scraping product page ...")
    product_info_json, brand_links, model_links, related_parts_links = scrape_product_page("https://www.partselect.com/Dishwasher-Parts.htm", 'Dishwashers')
    with open('./data/dishwasher_cleaned_data.jsonl', 'a') as f:
        f.write(json.dumps(product_info_json) + '\n')

    # scrape popular models info
    print("Scraping model information and parts...")
    scrape_model_links(product_info_json['models'], model_links, './data/dishwasher_cleaned_data.jsonl')
    
    # scrape related links
    print("Scraping related parts...")
    scrape_related_parts(related_parts_links, './data/dishwasher_cleaned_data.jsonl')

    # scrape repairs page
    print("Scraping repair page")
    repair_link = "https://www.partselect.com/Repair/Dishwasher/"
    product =  "Dishwasher "
    scrape_repair_page(repair_link, product, "./data/dishwasher_repair.jsonl")
    

