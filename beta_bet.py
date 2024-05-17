import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
import random
from datetime import datetime
import pyperclip
from termcolor import colored

options = Options()
# options.add_argument("--headless")
# options.add_argument("--start-maximized")

driver = webdriver.Firefox(options=options)
driver.maximize_window()



def get_categories_link():
    """
        This function select the link of all sport categories from an <aside> and returns them in a dict format
    
    """
    
    # go to 1xbet website and Wait for the aside element to load by waiting for 5 seconds 
    driver.get('https://1xbet.ci/')
    print(colored("[*INFO*] Step 1: Getting Sport Category....", "blue"))
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
        if category_name not in ['Politique', 'Sumo', 'Roller hockey', 'Pesäpallo', 'Formule 1', 'Beach Soccer', 'Hockey sur Gazon']:
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
    print(colored(f"[*INFO*] Step 1 - Done. {random_category}", "green"))
    # go the the link
    driver.get(random_link)
    print(colored("[*INFO*] Step 2: Getting Sport Subcategory...", "blue"))
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
    # else:
    #     print(colored("An Unexpected Error Occured While Getting The Subcategories...Skipping",'red'))
    #     get_subcategries_link()


def get_games_link():
    """
        This function get the game name,  game info, the date, and the game link of the slected game subcatecaory
    """
    # get game sbcategry list
    sport_subcategories = get_subcategries_link()
    # make it random
    random_sport_subcategory, random_link = random.choice(list(sport_subcategories.items()))
    print(colored(f"[*INFO*] Step 2: Done. {random_sport_subcategory}", "green"))

    if isinstance(random_link, list):
        random_link = random.choice(random_link)

    # go to the randomly selected category
    driver.get(random_link)
    print(colored(f"[*INFO*] Step 3: Getting Games...", "blue"))

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

        # print(f"""
        #         Game name: {game_name}
        #         Date: {date}
        #         Info: {game_info}
        #         href: {href}
        #         ---------------------
        #       """)

        game_event_list.append({"href": href,
                                "game_name": game_name,
                                "date": date,
                                "info": game_info})
        
    return game_event_list


def make_bet(start_date: str = "14/05/2024", end_date: str = "15/05/2024", min_odd: float = 1.01, max_odd: float = 1.50, num_games: int = 10):
    """
    This function takes a game event and makes a single bet

    Parameters:
        start_date: the starting date for the range of games to consider.
                    default is "14/05/2024".
        end_date: the ending date for the range of games to consider.
                  default is "15/05/2024".
        min_odd: the minimum odd value for the bet.
                 default is 1.01
        max_odd: the maximum odd value for the bet.
                 default is 1.50
        num_games: the number of games to include in the bet slip.
                   default is 10
    """
    games_event = get_games_link()
    selected_games = []

    for game_event in games_event:
        game_date = datetime.strptime(game_event["date"].split()[0], '%d/%m/%Y')
        start_date_obj = datetime.strptime(start_date.split()[0], '%d/%m/%Y')
        end_date_obj = datetime.strptime(end_date.split()[0], '%d/%m/%Y')

        if start_date_obj <= game_date <= end_date_obj:
            driver.get(game_event['href'])
            bet_contents = driver.find_elements(By.XPATH, "//div[@class='bet-inner']")
            odds_filtered = []

            for bet_content in bet_contents:
                bet_content_elements = bet_content.find_elements(By.TAG_NAME, "span")
                bet_content_btn = bet_content_elements[0]
                bet_content_odd = bet_content_elements[1].text

                if bet_content_odd:
                    try:
                        koef = float(bet_content_odd)
                        if min_odd <= koef <= max_odd:
                            odds_filtered.append((bet_content_btn, bet_content_odd))
                    except ValueError:
                        print(colored("An Unexpected Error Occurred While Retrieving The Odds", "red"))

            if odds_filtered:
                random_bet = random.choice(odds_filtered)
                random_bet[0].click()
                print(colored(f"[*INFO*] Game: {game_event['game_name']} - Bet: {random_bet[0].text} - Odd: {random_bet[1]}", "green"))
                selected_games.append(game_event)

            if len(selected_games) >= num_games:
                break

    if len(selected_games) < num_games:
        print(colored(f"[*INFO*] Not enough games found for the specified range ({start_date} to {end_date}), odd range ({min_odd} to {max_odd}), and number of games ({num_games})", "yellow"))
    else:
        print(colored(f"Overall Odds: {get_overall_odds()}", "magenta"))
        print("-----------------------------------------------------")

def make_bet_slip(min_odd: float = 1.01, max_odd: float = 1.50, num_games: int = 10, total_odds: float = 1000.0, start_date: str = "14/05/2024", end_date: str = "15/05/2024"):
    """
    This function continuously loops until the total odds value is reached or the maximum number of games is selected.
    The games will be randomly selected to decrease the loss probabilities.

    Parameters:
        min_odd: the minimum odd value for the bet.
                 default is 1.01
        max_odd: the maximum odd value for the bet.
                 default is 1.50
        num_games: the number of games to include in the bet slip.
                   default is 10
        total_odds: the total odds to reach. eg: if the value is set to 1000, the bot will continuously select games with the given odd
                    range that will accumulate to reach the value of the total odds.
                    default is 1000.0
        start_date: the starting date for the range of games to consider.
                    default is "14/05/2024".
        end_date: the ending date for the range of games to consider.
                  default is "15/05/2024".
    """
    current_odd = 0.0
    while current_odd < total_odds:
        make_bet(start_date=start_date, end_date=end_date, min_odd=min_odd, max_odd=max_odd, num_games=num_games)
        try:
            current_odd = get_overall_odds()
        except NoSuchElementException:
            continue

    # If we reach an overall odd of 1000, click on the save/load button
    driver.find_element(By.XPATH, "//button[@class='cpn-btn cpn-events__trigger cpn-btn--size-m cpn-btn--block']").click()
    # Wait until the save button is clickable, then click it
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="cpn-btn cpn-events__btn cpn-btn--theme-accent cpn-btn--size-m cpn-btn--default"]'))).click()
    # Wait for 5 more seconds
    driver.implicitly_wait(5)
    # Get the bet slip code
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="save-coupon__copy save-coupon-copy-btn"]'))).click()

    driver.implicitly_wait(5)
    code = pyperclip.paste()

    print(colored(f"Here is the code: {code}", "light_grey"))

def get_overall_odds():
    try:
        overall_oods = float(driver.find_element(By.XPATH, "//div[@class='cpn-total__coef']//span").text)
        return overall_oods
    except ValueError:
        print(colored("An Unexpected Error Occured Whiled Getting the Overall Odds", "red"))
        return 0.0

def is_date_less(input_date_str, limit_date_str):
  input_date = datetime.strptime(input_date_str.split()[0], '%d/%m/%Y')
  limit_date = datetime.strptime(limit_date_str.split()[0], '%d/%m/%Y')
  
  # Check if input date is less or equal than the limit date
  return input_date <= limit_date

# make_bet_slip()
# make_bet_slip(min_odd=1.01, max_odd=1.50, num_games=210, total_odds=35.0)
make_bet_slip(min_odd=1.01, max_odd=1.2, num_games=100, total_odds=10, start_date="18/05/2024", end_date="19/05/2024")