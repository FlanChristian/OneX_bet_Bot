import os
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
import random
import time


options = Options()
# options.add_argument("--headless")

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
driver.maximize_window()



def get_categories_link():
    """
        This function select the link of all sport categories from an <aside> and returns them in a dict format
    
    """
    
    # go to 1xbet website and Wait for the aside element to load by waiting for 5 seconds 
    driver.get('https://1xbet.com/')
    driver.implicitly_wait(5)
    
    # since the aside is split in two part we are going to get both
    aside1 = driver.find_element(By.XPATH, '//div[@class="assideCon_body top5 3 u-display-block"]')
    aside2 = driver.find_element(By.XPATH, '//div[@class="assideCon_body not_top"]')
 
    # randomly select an aside part 
    random_aside = random.choice([aside1, aside2])
    # then we find all <li> elements to the aside (those are the sport categories)
    sports_categories_list = random_aside.find_elements(By.TAG_NAME, 'li')

    # get all catgories of the randomly selected aside with their corresponding link
    categories = {}
    for category in sports_categories_list:
        a_link = category.find_element(By.TAG_NAME, 'a')
        href = a_link.get_attribute('href')
        category_name = a_link.get_attribute('data-sporturl')
        categories[category_name] = href

    return categories



def get_subcategries_link():
    """
        This function returns all subcategories of a given category with their corresponding link
    """

    # get all sport category with their corresponding links
    sport_categories = get_categories_link()
    # randomly select a sport category with its corresponding link
    random_category, random_link = random.choice(list(sport_categories.items()))
    # go the the link
    driver.get(random_link)
    # get all subcategories of the selected sport category
    sport_subcategories_list = driver.find_elements(By.XPATH, "//ul[contains(@class, 'liga_menu') or contains(@class, 'subcategory-menu')]")
    subcategories = {}

    for subcategory in sport_subcategories_list:

        # if classname is 'liga-menu' then get directly the 'href' and the subategory name
        if subcategory.get_attribute('class') == 'liga_menu':
            a_link = subcategory.find_element(By.TAG_NAME, 'a')
            href = a_link.get_attribute('href')
            subcategory_name = subcategory.find_element(By.XPATH, ".//span[@class='link-title__label']").text
            subcategories[subcategory_name] = href

        # if classname is 'subcategory-menu' it means that the subcategory have their own categories
        if subcategory.get_attribute('class') == 'subcategory-menu':
            # first we get the name of the subcategory
            subcategory_name = subcategory.find_element(By.XPATH, ".//span[@class='link-title__label']").text
            subcategory.click()
            driver.implicitly_wait(1)
            # now we get all category of the subcategory 
            categories_of_subcategory_list = subcategory.find_element(By.XPATH, ".//ul[@class='liga_menu']").find_elements(By.TAG_NAME, 'li')

            subcategories_of_subcategory_list_hrefs = []
            for category_of_subcategory in categories_of_subcategory_list:
                # we loop throug each category of subcategories ot get their 'href' and add them to a dict
                href = category_of_subcategory.find_element(By.TAG_NAME, 'a').get_attribute('href')
                subcategories_of_subcategory_list_hrefs.append(href)
                

            subcategories[subcategory_name] = subcategories_of_subcategory_list_hrefs
       
                
    return subcategories


def get_games_link():
    """
        This function get the game name,  game info, the date, and the game link of the slected game subcatecaory
    """
    # get game sbcategry list
    sport_subcategories = get_subcategries_link()
    # make it random
    random_sport_subcategory, random_link = random.choice(list(sport_subcategories.items()))

    if isinstance(random_link, list):
        random_link = random.choice(random_link)

    # go to the randomly selected category
    driver.get(random_link)

    # get all game infos of the selected subcategory
    games_event = driver.find_element(By.XPATH, "//ul[@class='event_menu']").find_elements(By.TAG_NAME, 'li')

    for game_event in games_event:
        game_event_list = []
        try:
            game_event_container = game_event.find_element(By.TAG_NAME, 'a')
            href = game_event_container.get_attribute('href')
            game_name = game_event_container.find_element(By.CLASS_NAME, "gname").text
            date = game_event_container.find_element(By.CLASS_NAME, "date").text
            game_info = game_event_container.find_element(By.CLASS_NAME, 'game-info').text
        except NoSuchElementException:
            # if game info is not available
            game_info = 'Unavailable'

        print(f"""
                Game name: {game_name}
                Date: {date}
                Info: {game_info}
                href: {href}
                ---------------------
              """)

        game_event_list.append({"href": href,
                                "game_name": game_name,
                                "date": date,
                                "info": game_info})
        

    return game_event_list
print(get_games_link())

# def make_bet_slip(date=None, odd=None, total_odds=None):
#     """
#     This function is continously looping as long as the the total odds values is not the reach.
#     The games will be randomly selected to decrease the loss probabilities. 

#     Parameters:

#             date: the maximum date we want the bot to not exceed while making the bet slip.
#                   eg: if the date is set to tomorow, it will randomly select bets ranging from today to tomorow. 
#                   We are not considering live bets because the odds are not stables.

#             odd: the maximum odd. eg: if the odd is 1.1000 the bot we select all games'odd that are lower or equal the selected value
#             total_odds: the total odds to reach. eg: if the value is set to 1000, the bot we continously selecting games with the given odd
#                         that will accumulate to reach the value of the total odds.
    
#     """

#     games_event =  get_games_link()
#     random_game_event = random.choice(games_event)
#     driver.get(random_game_event['href'])

#     bet_content = driver.find_element(By.XPATH, "//div[@class='bets_content betsscroll']")
#     odds_label = 



# make_bet_slip()



   

# make_bet_slip()