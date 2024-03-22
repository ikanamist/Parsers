from abc import ABC, abstractmethod
import requests
import json
import requests_html

class Parser(ABC):
    def __init__(self, base_url):
        self.base_url = base_url

    @abstractmethod
    def get_products(self, *args, **kwargs):
        pass

    def save_data_to_file(self, data, file_name):
        with open(file_name, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

class AfishaAPI(Parser):
    def get_products(self):
        response = requests.get(self.base_url, params={"city": "2"})
        if response.status_code == 200:
            return response.json()
        raise RuntimeError(f"Was status code: {response.status_code}")

class BY7745API(Parser):
    def get_products(self):
        response = requests.get(self.base_url, params={"term": "wortex"})
        if response.status_code == 200:
            return response.json()
        raise RuntimeError(f"Was status code: {response.status_code}")

class Url7745(Parser):
    ITEMS_ROOT = "#catalog-best .swiper-wrapper"
  
    def get_products(self, page_num=1):
        self.session = requests_html.HTMLSession()
        response = self.session.get(self.base_url, params={"page": page_num})
        
        if response.status_code == 200:
            page = response
            page.html.render()
            items_box = page.html.find(self.ITEMS_ROOT, first=True)
            items = items_box.find(".swiper-slide")
            result = []

            for item in items:
                item_data = {}

                img_box = item.find(".item-block_photo img", first=True)
                item_data["img"] = img_box.attrs["src"]

                title_box = item.find(".catalog-item__middle-container.item-block a", first=True)
                item_data["title"] = title_box.text

                link_box = item.find(".catalog-item__middle-container.item-block", first=True)
                item_data["link"] = list(link_box.links)[0]

                cost_box = item.find(".item-block_main-price", first=True)
                item_data["cost"] = cost_box.text

                item_data["promo"] = True if item.find(".item-block_secondary-price span", first=True) else False

                result.append(item_data)
            return result
        else:
            raise RuntimeError(f"Was status code: {response.status_code}")

if __name__ == "__main__":
    api_7745 = BY7745API("https://7745.by/site-search")
    api_afisha = AfishaAPI("https://www.afisha.ru/rests/api/public/v1/restaurant/")
    parser = Url7745("https://7745.by/articles/vse-dlya-sada-i-ogoroda-v-kataloge-7745")
    try:
        result = parser.get_products()
        info_7745 = api_7745.get_products()
        info_afisha = api_afisha.get_products()
    except RuntimeError as err:
        print(err)
    else:
        api_7745.save_data_to_file(info_7745, "api7745.json")
        api_afisha.save_data_to_file(info_afisha, "api_afisha.json")
        parser.save_data_to_file(result, "parse_7745.json")
