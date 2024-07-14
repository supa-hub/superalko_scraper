"""
Copyright (c) 2024 Tomi Bilcu. All rights reserved.

This work is licensed under the terms of the MIT license.  
For a copy, see LICENSE.txt.
"""

import requests
from bs4 import BeautifulSoup
import json


class get_superalko:
    def __init__(self):

        # we initialise the scraper by getting the main page,
        # so we get all the different categories
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        }

        self.main_link = "https://viinarannasta.eu/en/"

        self.r = requests.get(self.main_link, headers=self.headers)
        self.sublinks_and_names: dict[str, list[list[str]]] = {}


    # pretty self-explanatory, but yes it gets all the the links for the different drink
    # categories on the website
    def get_sublinks(self) -> None:
        
        self.soppa = BeautifulSoup(self.r.content, "lxml")
        last_category = ""

        # loop through the main page and get all the links to drinks categories
        for a_sublink in self.soppa.find_all("li", attrs={"class":"mo_ml_level_0 mo_ml_column"}):

            # the main category, aka. if its Beer or Soft drink etc.
            current_main_category: str = a_sublink.find("a", attrs={"class":"mo_ma_level_0"}).text.replace("\n", "")
            last_category = current_main_category
            categories = {current_main_category: []}

            # this part runs if the drink has other subcategories on the site,
            # for example: if the Beer category has Finnish beer and German beer
            if a_sublink.find("a", {'class': 'mo_ma_level_1 mo_sub_a'}):
                for subcategory in a_sublink.find_all("a", {'class': 'mo_ma_level_1 mo_sub_a'}):
                    categories[current_main_category].append([subcategory.text.replace("\n", ""), subcategory.attrs.get("href", "")])

                self.sublinks_and_names[current_main_category] = categories[current_main_category]

            else:
                # if the drink doesn't have subcategories, then we run this part
                last_category_list = self.sublinks_and_names.get(last_category)

                if last_category_list != None and [current_main_category, a_sublink.find("a", {'class': 'mo_ma_level_0'}).attrs.get("href", "")] in last_category_list:
                    continue
                
                else:
                    categories = ["noSubcategories", a_sublink.find("a", {'class': 'mo_ma_level_0'}).attrs.get("href", "")]

                    self.sublinks_and_names[current_main_category] = [categories]


            # clean up the sublinks to ensure that there isn't any invalid links
            # used normal for loop for clarity
            temp = {}
            for main, sub in self.sublinks_and_names.items():
                temp[main] = []
                for links in sub:
                    if links[1] != "":
                        temp[main].append(links)
            
            self.sublinks_and_names = temp
            




    # returns all the found category names
    def category_names(self) -> list[str]:
        return [category for category in self.sublinks_and_names]

    

    # Returns the responses for all the subcategories of a category.
    # I used dictionary comprehension, so thats why it might be
    # very difficult to read or understand.
    def __getNewCategory(self, sublink) -> dict[str, requests.models.Response]:
        return {a_category[0]: requests.get(a_category[1], headers = self.headers) for a_category in sublink}
    
    
    def get_products(self, product: str):
        if product not in self.sublinks_and_names:
            return {}
        
        else:
            r = self.__getNewCategory(self.sublinks_and_names[product])
            
            # this will hold the final data, 
            # <product> is the drink category, which will hold the subcategories
            main_products_dict = {product: []} 


            main_products_dict[product] == "no"

            # loop through all the subcategories of 
            # a certain type of drink
            for names, responses in r.items():
                products_dict = {}

                soppa = BeautifulSoup(responses.content, "lxml")

                # gets all the products from a category
                products = soppa.find_all("div", {"class": "pro_second_box pro_block_align_0"})

                # had to make 2 almost similar loops in if-statements, because of 
                # the noSubcategories-place having too many products in some
                # categories
                if names == 'noSubcategories':
                    subCategory_num = 1


                    for index, a_product in enumerate(products):
                        product_name = a_product.find("div", attrs={"class":"flex_box flex_start mini_name"}).text.strip().strip("\n")
                        product_price = float(a_product.find("div", attrs={"class":"pro_kuan_box"}).text.strip().replace("\n", "").replace("(tax incl.)", "").replace("€", "").replace("\u00a0\u0101\u201a\u00ac","").replace("\u00a0\u00e2\u201a\u00ac",""))

                        products_dict[product_name] = product_price
                        # if its already looped through 300 products, save them in a custom subcategory and
                        # the next ones save in a different one
                        if index >= 300:
                            main_products_dict[product].append({str(subCategory_num): products_dict})
                            subCategory_num += 1
                            products_dict = {}
                            
                    # we also add the last products
                    main_products_dict[product].append({str(subCategory_num): products_dict})
                    subCategory_num += 1
                    products_dict = {}


                else:
                    for index, a_product in enumerate(products):
                        product_name = a_product.find("div", attrs={"class":"flex_box flex_start mini_name"}).text.strip().strip("\n")
                        product_price = float(a_product.find("div", attrs={"class":"pro_kuan_box"}).text.strip().replace("\n", "").replace("(tax incl.)", "").replace("€", "").replace("\u00a0\u0101\u201a\u00ac","").replace("\u00a0\u00e2\u201a\u00ac",""))

                        products_dict[product_name] = product_price

                    main_products_dict[product].append({names: products_dict})

            return main_products_dict

    




class Scraper:
    def __init__(self):
        self.aa = get_superalko()
        self.aa.get_sublinks()

    def get_category(self, name):
        while self.aa.get_products(name) == False:
            name = input(f"The category name <<< {name} >>> was wrong, you can fix it here: ")
            if name == "skip":
                return {}

        else:
            return self.aa.get_products(name)
    
    # if you dont want a specific category, and you just want all the names
    # to input into get_category() method
    def category_names(self):
        return self.aa.category_names()
        

        

# example in which we get every product from superalko and 
# store them in a JSON file parsed into separate categories
if __name__ == "__main__":
    scraper = Scraper()

    categories = ["Spirits", "Wine", "Liqueur", "Beer", "Long drink & cider", "Non-alcoholic beverages", "Sweets", "Other"]

    all_products = [scraper.get_category(data) for data in categories]
    filter( lambda x: x != {}, all_products) # filter out the empty values

    with open("products.json", "w+") as file:
        json.dump(all_products, file, indent = 5)

    print("done")