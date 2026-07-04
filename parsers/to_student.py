import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json

def parse_url(url):
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")
    main_block = soup.find("div", class_="page-content__text-common")

    for tag in main_block.find_all(['a', 'span', 'strong', 'em', 'b', 'i']):
        tag.unwrap()

    text = main_block.get_text(separator=" ", strip=True)

    json_dict = {
        "url": url,
        "content": text
    }

    return json_dict

#TODO: собрать несколько страниц 

def main():
    urls = ["https://www.sgu.ru/studentu-vsyo-pro-uchyobu/ot-sessii-do-sessii", "https://www.sgu.ru/studentu-vsyo-pro-uchyobu/studencheskiy-bilet"]

    parser_dir = Path(__file__).resolve().parent
    output_file = parser_dir.parent / 'data' / 'to_student_output.json'

    with open(output_file, "w", encoding="utf-8") as f:
        data = []
        for url in urls:
            data.append(parse_url(url))
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()