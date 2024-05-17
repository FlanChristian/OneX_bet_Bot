import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.expected_conditions import  NoAlertPresentException, presence_of_element_located
import random
from datetime import datetime
import pyperclip
from termcolor import colored
import time

options = Options()
# options.add_argument("--headless")
# options.add_argument("--start-maximized")

driver = webdriver.Firefox(options=options)
driver.maximize_window()


# go to 1xbet website and Wait for the aside element to load by waiting for 5 seconds 
driver.get('https://1xbet.com/')

driver.implicitly_wait(5)

# delete the pop up pub
driver.find_element(By.XPATH, '//a[@class="pf-subs-btn-link"]').click()
time.sleep(5)

# filter the match by date today and the next day
driver.find_element(By.ID, 'line_href').click()
time.sleep(5)

selectdate = driver.find_elements(By.XPATH, '//span[@class="ls-filter__check"]')

for element in selectdate:
    element.click()

datpicker = driver.find_elements(By.XPATH, '//div[@class="vdp-datepicker ls-filter__input c-filter-datepiker"]')

debut = True


wait = WebDriverWait(driver, 10)

# we find the inputs of the filters end we asign them our date (today and the next day)
for element in datpicker:
    element.click()
    wait.until(presence_of_element_located((By.XPATH, '//span[@class="cell day today"]')))

    if debut == True:
        today = driver.find_element(By.XPATH, '//span[@class="cell day today"]')
        today.click()
        day = today.text
        print(day)
        debut = False
    else:
        print("else")
        xpath_expression = f'//span[@class="cell day" and text()="{int(day) + 1}"]'
        driver.find_element(By.XPATH, xpath_expression).click()
   
driver.find_element(By.XPATH, '//button[@class="ls-filter__btn"]').click()    

                          
def get_categories_link():
    """
        This function select the link of all sport categories from an <aside> and returns them in a dict format
    
    """

    
    print(colored("[*INFO*] Step 1: Getting Sport Category....", "blue"))

    # find the datepiker input for the debut
    # input_element = driver.find_element(By.XPATH, '//input[@class="c-filter-datepiker__input"]')
    # input_element.clear()  # delete previous text
    # input_element.send_keys(datetime.now().strftime('%d/%m/%Y'))

    
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
    # get game subcategory list
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

             # Utilisation d'une expression XPath pour sélectionner le deuxième élément <span> à l'intérieur de <span class="date">
            
            date_elements = game_event_container.find_elements(By.XPATH, ".//span[@class='date']/span")
            if len(date_elements) > 1:
                date_element = date_elements[-1]  # Sélectionner le dernier élément s'il y en a plusieurs
            else:
                date_element = date_elements[0]  # Sélectionner le seul élément s'il y en a un seul
            date = date_element.text

            game_info = game_event_container.find_element(By.CLASS_NAME, 'game-info').text

        except NoSuchElementException:
            # if game info is not available
            game_info = 'Unavailable'

        # print(f"""
        #          Game name: {game_name}
        #          Date: {date}
        #          Info: {game_info}
        #          href: {href}
        #          ---------------------
        #    """)

        game_event_list.append({"href": href,
                                "game_name": game_name,
                                "date": date,
                                "info": game_info})
        
    return game_event_list


def make_bet(date:str="14/05/2024", odd:float=1.180): #1.180 #datetime.now().strftime('%d/%m/%Y')
    """
    This function take a game event and make a single bet

    Parameters:
          date: the maximum date we want the bot to not exceed while making the bet slip.
                  eg: if the date is set to tomorow, it will randomly select bets ranging from today to tomorow. 
                  We are not considering live bets because the odds are not stables.
                  default is today's date in format dd/mm/yy.

            odd: the maximum odd. eg: if the odd is 1.1000 the bot we select all games'odd that are lower or equal the selected value
                 default is 1.180
    """
    games_event =  get_games_link()
    random_game_event = random.choice(games_event)

    if is_date_less(random_game_event["date"], date):
    
  
        print(colored(f"[*INFO*] Step 3: Done. {random_game_event['game_name']} Selected.", "green"))
        driver.get(random_game_event['href'])
        print(colored(f"[*INFO*] Step 4: Getting a Bet...", "blue"))
        
        driver.implicitly_wait(2)

        bet_contents = driver.find_elements(By.XPATH, "//div[@class='bet-inner']")
        odds_filtered = []

        for bet_content in bet_contents:
            bet_content_elements = bet_content.find_elements(By.TAG_NAME, "span")
            bet_content_btn = bet_content_elements[0]
            bet_content_odd = bet_content_elements[1].text

            if bet_content_odd:
                try:
                    koef = float(bet_content_odd)
                    if koef <= odd:
                        odds_filtered.append((bet_content_btn, bet_content_odd))
                except ValueError:
                    print(colored("An Unexpected Error Occured While Retrieving The Odds", "red"))
                    return 0

        
        if odds_filtered:
            random_bet = random.choice(odds_filtered)
            random_bet[0].click()
            print(colored(f"[*INFO*] Step 4: Done. Bet: {random_bet[0].text} - Odd: {random_bet[1]}", "green"))
            print(colored(f"Overall Odds: {get_overall_odds()}", "magenta"))
            print("-----------------------------------------------------")

        else:
            print(colored(f"[*INFO*] Step 3: No Bet Found for Odd {odd}. Skipping..", "yellow"))

    else:
        print(colored(f"[*INFO*] Step 3: No Games Found for {date}. skipping...", "yellow"))
    

def make_bet_slip(total_odds:float=1000):
    """
    This function is continously looping as long as the the total odds values is not the reach.
    The games will be randomly selected to decrease the loss probabilities. 

    Parameters:

            total_odds: the total odds to reach. eg: if the value is set to 1000, the bot we continously selecting games with the given odd
                        that will accumulate to reach the value of the total odds.
                        defaut is 1000
    """
    current_odd = 0.0 
    while current_odd < total_odds:
        make_bet()
        try:
            current_odd = get_overall_odds() 
        except NoSuchElementException:
            continue
    
    #  if we reach an overall odd of 1000, click on the save/load button
    driver.find_element(By.XPATH, "//button[@class='cpn-btn cpn-events__trigger cpn-btn--size-m cpn-btn--block']").click()
    # wait until the save button is clickable then click it
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//button[@class="cpn-btn cpn-events__btn cpn-btn--theme-accent cpn-btn--size-m cpn-btn--default"]'))).click()
    # wait for 5 more seconds
    driver.implicitly_wait(5)
    # get the bet slip code

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

make_bet_slip()





