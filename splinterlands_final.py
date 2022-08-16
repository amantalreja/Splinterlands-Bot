# All Imports
import os
import itertools
import time
import logging
import requests
import threading
import configparser
import urllib
import json
import multiprocessing
import encodings.idna
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
###

info = """          WELCOME TO SPLINTERLANDS BOT

1. Insert/Edit an Account
2. Delete an Account
3. Set Summoners
4. Set cards for each Summoner
5. Set Splinter for Dragon card 
5. Reset Summoners
6. Reset Cards
0. Start Bot(s)

Note:  The programe may break if you use alot of userids and password!
        The max number of users depends on your hardware\nand internet.

"""
select_str = "Select any option or press any other key to start game:"


class Bot:

    def __init__(self, id, account, summoners_config, summoners_default, splinters, cards_config, times):
        self.id = str(id)
        self.browser = None
        self.account = account
        self.summoners_config = summoners_config
        self.summoners_default = summoners_default
        self.splinters = splinters
        self.cards_config = cards_config
        self.times = times

        # Logging Variables
        self.logFile = create_logs(self.id)
        self.log = logging.getLogger('Run' + self.id)
        myformatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        myhandler = logging.FileHandler(self.logFile)
        myhandler.setLevel(logging.DEBUG)
        myhandler.setFormatter(myformatter)
        self.log.addHandler(myhandler)
        self.log.setLevel(logging.DEBUG)

    def release_handlers(self):
        handlers = self.log.handlers[:]
        for h in handlers:
            h.close()
            self.log.removeHandler(h)
        print('Bot {} is shutting down!!'.format(self.id))

    # HELPER FUNCTIONS
    def find_click_by_id(self, elems, values):
        for i, elem in enumerate(elems):
            self.browser.find_element_by_id(elem).send_keys(values[i])

    def find_click_by_class(self, elems, values):
        for i, elem in enumerate(elems):
            self.browser.find_element_by_class_name(elem).send_keys(values[i])

    def button_click_by_class(self, elems):
        for i, elem in enumerate(elems):
            self.browser.find_element_by_class_name(elem).click()

    def wait_by_id(self, val, delay=5):
        try:
            WebDriverWait(self.browser, int(delay)).until(
                EC.visibility_of_element_located((By.ID, val)))
        except TimeoutException as e:
            #self.log.exception("Exception in Value: {} with delay {}".format(val, delay))

            return False
        return True

    def wait_by_class(self, val, delay=5):
        try:
            WebDriverWait(self.browser, delay).until(
                EC.visibility_of_element_located((By.CLASS_NAME, val)))
        except TimeoutException as e:
            self.log.exception(
                "Exception in Value: {} with delay {}".format(val, delay))
            raise TimeoutException
            return False
        return True

    def remove_Mana(self, input):
        index = input.find('ana')
        print('printing input')
        print(input)
        print(input[0:index-1])
        return input[0:index-1]

    # END - HELPER FUNCTIONS

    # Login to game
    def login(self, cred):
        try:
            WebDriverWait(self.browser, 5).until(
                EC.visibility_of_element_located((By.ID, 'email')))
            self.find_click_by_id(['email', 'password'], [cred[0], cred[1]])
            # self.browser.find_element_by_id("password").click()
            self.browser.find_element_by_xpath(
                '/html/body/div[3]/div/div/div/div[2]/div/div[2]/div[2]/div[3]/div/button').click()
            return True
        except TimeoutException as e:
            self.log.exception("Exception in login(): ")
            return False

    # Skipping welcome page
    def override_welcome_page(self):
        try:
            self.wait_by_class('section', 10)
        except Exception as e:
            self.log.exception("Exception in override_welcome_page(): ")
            logging.error('Account {}: {}'.format(self.id, e), exc_info=True)
        try:
            elem = self.browser.find_element_by_id('menu_item_battle')
            act = ActionChains(self.browser)
            act.move_to_element(elem)
            act.click().perform()
        except Exception as e:
            self.log.exception("Exception in override_welcome_page(): ")
            logging.error('Account {}: {}'.format(self.id, e), exc_info=True)

    def start_match(self):

        # Start ranking game
        try:
            try:
                self.browser.find_element_by_xpath(
                    "//button[@class='btn btn--done']").click()
            except:
                pass

            try:
                self.browser.find_element_by_css_selector(
                    "#dialog_container > div > div > div > div.modal-body > div:nth-child(3) > div:nth-child(2) > button").click()
                return True
            except:
                pass

            try:
                flg = False
                WebDriverWait(self.browser, 2)
                for elem in self.browser.find_elements_by_class_name('btn-battle'):
                    if elem.text.lower() == 'keep playing!':
                        flg = True
                        elem.click()
                if not flg:
                    raise NoSuchElementException
                print('Account {}: Congrats! Ranking increased.'.format(self.id))
                self.log.debug(
                    'Account {}: Congrats! Ranking increased.'.format(self.id))
            except:
                print('Account {}: Ranking is still the same!'.format(self.id))
                self.log.debug(
                    'Account {}: Ranking is still the same!'.format(self.id))

            self.wait_by_id('menu_item_battle')
            act = ActionChains(self.browser)
            act.move_to_element(
                self.browser.find_element_by_id('menu_item_battle'))
            act.click().perform()

            # WebDriverWait(self.browser, 60).until(
            #     EC.element_to_be_clickable((By.XPATH, "//div[@class='buttons']/div/button[@class='btn-battle'][1]")))
            # self.browser.find_elements_by_xpath("//div[@class='buttons']/div/button[@class='btn-battle']")[1].send_keys(
            #     Keys.RETURN)

            WebDriverWait(self.browser, 60).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='big_category_btn red']")))
            self.browser.find_element_by_xpath(
                "//button[@class='big_category_btn red']").click()

            # WebDriverWait(self.browser, 60).until(
            #     EC.element_to_be_clickable((By.CLASS_NAME, 'btn--create-team')))
            # self.browser.find_element_by_class_name('btn--create-team').send_keys(Keys.RETURN)

            WebDriverWait(self.browser, 60).until(
                EC.visibility_of_all_elements_located((By.CSS_SELECTOR,
                                                       "#dialog_container > div > div > div > div.modal-body > div:nth-child(3) > div:nth-child(2) > button")))
            self.browser.find_element_by_css_selector(
                "#dialog_container > div > div > div > div.modal-body > div:nth-child(3) > div:nth-child(2) > button").click()

        except Exception as e:
            self.log.exception("Exception in start_match(): ")
            print('Account {}: {}'.format(self.id, e))
            return False
        return True

    # SUMMONERS AND CARDS SETUP FUNCTIONS
    def click_on_card(self, elem):  # Used in set_summoner() function
        try:
            act = ActionChains(self.browser)
            act.move_to_element(elem).perform()
            WebDriverWait(self.browser, 0.3)
            act.click().perform()
        except Exception as e:
            print('Account {}: {}'.format(self.id, e))

    # Helper functions to set cards
    def sort_cards(self, cards, base):
        n = len(cards[base])

        for i in range(n - 1):
            for j in range(n - i - 1):
                if cards[base][j] > cards[base][j + 1]:
                    for key in cards:
                        cards[key][j], cards[key][j +
                                                  1] = cards[key][j + 1], cards[key][j]

    def multi_pop(self, cards, ind):
        cards['id'].pop(ind)
        cards['card_mana'].pop(ind)
        cards['card_melee'].pop(ind)
        cards['card_ranged'].pop(ind)

    # Main algorithm to select cards (Recursive function)
    def select(self, cards, idx, c_type, total, j=1, slots=2, calculated_ids=[]):

        # DEBUG
        mana_sum = sum([cards['card_mana'][i] for i in idx])
        self.log.debug('idx = {} j = {} total = {}'.format(idx, j, total))
        self.log.debug('Total mana for cards selected: {}'.format(mana_sum))
        self.log.debug('Selected card id is {} and mana is {}:'.format(
            cards['id'][len(cards['id']) - j], cards['card_mana'][len(cards['id']) - j]))
        ###
        if (len(idx) == slots and sum([cards['card_mana'][i] for i in idx]) <= total) or cards[c_type][
                len(cards[c_type]) - j] == -1 or j > len(cards[c_type]):
            self.log.debug('First if')
            return None
        elif (cards['card_mana'][len(cards[c_type]) - j] + sum([cards['card_mana'][i] for i in idx])) <= total and (len(calculated_ids) == 0 or (cards['card_mana'][len(cards['id']) - j] in calculated_ids)):
            self.log.debug('Second if')
            idx.append(len(cards[c_type]) - j)
            self.log.debug('Chosen card id is {} and mana is {}:'.format(cards['id'][len(cards['id']) - j],
                                                                         cards['card_mana'][len(cards['id']) - j]))
            j += 1
            self.select(cards, idx, c_type, total, j, slots)
        else:
            j += 1
            self.select(cards, idx, c_type, total, j, slots)

    # another helper function for algorithm
    def select_cards(self, cards, total):
        idx = []
        slots_rem = 6
        # DEBUG
        self.log.debug('Remaining mana: {}'.format(total))
        self.log.debug(cards)
        self.log.debug('Number of cards in deck: {}'.format(len(cards['id'])))
        l = 0
        # 2 melee, 2 ranged and 2 on mana
        for c_type in ['card_melee', 'card_ranged', 'card_mana']:
            l += 1
            self.log.debug('Ctype loop Iteration number: {}'.format(l))
            self.sort_cards(cards, c_type)
            self.log.debug('Starting recursive function select()...')
            if c_type == ['card_mana']:
                print('calculate ran here 1')
                ids_chosen_by_calculate = self.calculate_target(
                    cards['card_mana'], total, slots_rem)
                self.select(cards, idx, c_type, total, 1, slots_rem)
            else:
                print('calculate ran here 2')
                self.calculate_target(cards['card_mana'], total, slots_rem)
                self.select(cards, idx, c_type, total)
            self.log.debug('Getting out of recursive function select()...')
            for i in idx:
                slots_rem -= 1
                total -= cards['card_mana'][i]
                #             click_on_card(cards['elements'][i])
                time.sleep(1)
                try:
                    act = ActionChains(self.browser)
                    # DEBUG
                    self.log.debug('Chosen card id is {} and mana is {}:'.format(
                        cards['id'][i], cards['card_mana'][i]))
                    ###
                    act.move_to_element(self.browser.find_element_by_xpath(
                        "//div[@class='deck-builder-page2__cards']/div[@card_detail_id='{}']".format(
                            cards['id'][i]))).perform()
                    WebDriverWait(self.browser, 0.3)
                    act.click().perform()
                    self.browser.find_element_by_tag_name(
                        'body').send_keys(Keys.CONTROL + Keys.HOME)
                except Exception as e:
                    print('Account {}: {}'.format(self.id, e))
                    self.log.error("Exception occurred", exc_info=True)
                self.multi_pop(cards, i)

            self.log.debug(
                'Number of cards in deck (After selection): '.format(len(cards['id'])))
            idx = []

    # Helper function

    def click_card(self, cards, ids, click_card_wait=20):
        slot = 0
        mana = 0
        for id in ids:
            try:
                act = ActionChains(self.browser)
                if click_card_wait == 20:
                    time.sleep(20)
                    click_card_wait = 0
                print(
                    "//div[@class='deck-builder-page2__cards']/div[@card_detail_id='{}']".format(id))
                time.sleep(2)
                #input('verify your card id before getting it clicked');
                act.move_to_element(self.browser.find_element_by_xpath(
                    "//div[@class='deck-builder-page2__cards']/div[@card_detail_id='{}']".format(id))).perform()
                WebDriverWait(self.browser, 1)
                # time.sleep(4)
                act.click().perform()
                time.sleep(1)
                self.browser.find_element_by_tag_name(
                    'body').send_keys(Keys.CONTROL + Keys.HOME)
                mana += cards['card_mana'][cards['id'].index(id)]
                self.multi_pop(cards, cards['id'].index(id))
            except NoSuchElementException as e:
                print('Account {}: {}'.format(self.id, e))
                self.log.error("Exception occurred", exc_info=True)
                slot += 1
        return slot, mana

    def validate_ids(self, cards, ids, rem_mana):

        ids_mana = {'id': [i for i in ids if i in cards['id']],
                    'mana': [cards['card_mana'][cards['id'].index(i)] for i in ids if i in cards['id']]}

        total = sum(ids_mana['mana'])

        if total <= rem_mana:
            return ids_mana['id']

        self.sort_cards(ids_mana, 'mana')
        removal_ids = []

        for i in range(len(ids_mana['mana'])):
            if ids_mana['mana'][i] == 0:
                continue
            elif total - ids_mana['mana'][i] <= rem_mana:
                removal_ids.append(ids_mana['id'][i])
                break
            elif total - ids_mana['mana'][i] > rem_mana:
                removal_ids.append(ids_mana['id'][i])
                total -= ids_mana['mana'][i]

        for j in removal_ids:
            ids.remove(j)
        # Debug
        self.log.debug('Length: {} and ids: {}'.format(len(ids), ids))
        return ids

    def select_template_cards(self, card_c, cards, rem_mana, total_mana):
        #input('allow me to run temlate cards');
        colors = {'blue': 'water',
                  'red': 'fire',
                  'gold': 'dragon',
                  'green': 'earth',
                  'white': 'life',
                  'black': 'death'}
        print('aa Print statement location here')
        print('these are the details received by template cards')
        print('total mana')
        print(total_mana)
        print('remaining mana')
        print(rem_mana)
        mana = 0
        slot = 0

        ids = self.cards_config[colors[card_c]]

        if total_mana in ids:
            validated_ids = self.validate_ids(cards, ids[total_mana], rem_mana)
            slot = 6 - len(validated_ids)
            print('these are the choosen ids')
            print(validated_ids)
            val = self.click_card(cards, validated_ids, click_card_wait=20)
            slot += val[0]
            mana = val[1]
            # THE MANA USED IS SHOWING
        else:
            self.select_cards(cards, rem_mana)
        self.log.debug('Total mana: {} and Remaining mana: {}'.format(
            total_mana, rem_mana))
        self.log.debug('Slots: {} and mana used: {}'.format(slot, mana))

        if slot > 0:
            idx = []
            rem_mana -= mana
            self.log.debug("Inside slot 'if'")
            try:
                self.sort_cards(cards, 'card_mana')
                #input('aa starting select card here')
                print('printing what was given to calculate_target')
                print(cards['card_mana'])
                print('mana')
                print(rem_mana)
                print('slot')
                print(slot)
                calculated_array = self.calculate_target(
                    cards['card_mana'], rem_mana, slot)
                self.select(cards, idx, 'card_mana', rem_mana, 1,
                            slot, calculated_ids=calculated_array)
            except Exception as e:
                self.log.exception(
                    'Exception in select_template_cards()', exc_info=True)
                print('Account {}: {}'.format(self.id, e))
            for i in idx:
                try:
                    act = ActionChains(self.browser)
                    print('trying to find card by suggested ids')
                    time.sleep(1)
                    act.move_to_element(self.browser.find_element_by_xpath(
                        "//div[@class='deck-builder-page2__cards']/div[@card_detail_id='{}']".format(
                            cards['id'][i]))).perform()
                    print('trying passseddd!!')
                    WebDriverWait(self.browser, 2)
                    act.click().perform()
                    self.browser.find_element_by_tag_name(
                        'body').send_keys(Keys.CONTROL + Keys.HOME)
                except Exception as e:
                    print(' THIS PIIEC OF SHIT DIDN"T EVEN SELECT CARD THE FUCK??????')
                    self.log.exception(
                        'Exception in select_template_cards()', exc_info=True)
                    print('Account {}: {}'.format(self.id, e))
                self.multi_pop(cards, i)
        elif slot < 0:
            self.log.warning(
                'Invalid number of cards selected please fix the {}.text file'.format(self.id, card_c))
            print('Account {}: Invalid number of cards selected please fix the {}.text file'.format(
                self.id, card_c))

    def set_cards(self, card_c, rem_mana, total_mana):

        cards_elems = self.browser.find_elements_by_xpath(
            "//div[@class='deck-builder-page2__cards']/div")
        cards_mana = self.browser.find_elements_by_xpath(
            "//div[@class='deck-builder-page2__cards']/div/div[@class='relative-position']/div[@class='stat-mana']")

        cards_melee = []
        cards_ranged = []

        for elem in cards_elems:
            try:
                cards_ranged.append(
                    int(elem.find_element_by_css_selector("div.stat-ranged ").text))
            except:
                cards_ranged.append(-1)

        for elem in cards_elems:
            try:
                cards_melee.append(
                    int(elem.find_element_by_css_selector("div.stat-attack").text))
            except:
                cards_melee.append(-1)

        cards = {'id': [int(elem.get_attribute('card_detail_id')) for elem in cards_elems],
                 'card_mana': [int(self.remove_Mana((elem.text))) for elem in cards_mana],
                 'card_melee': cards_melee,
                 'card_ranged': cards_ranged}

        self.select_template_cards(card_c, cards, rem_mana, str(total_mana))

    # For Gold aka dragon only
    def select_splinter(self, card_c):
        try:
            WebDriverWait(self.browser, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='cancel link-btn']")))
            self.browser.find_elements_by_class_name('filter-option-button')

            print('Account {}: In Splinter Options...'.format(self.id))

            title_dict = {'water': 'blue', 'fire': 'red', 'earth': 'green',
                          'life': 'white', 'death': 'black'}
            elems = []
            titles = []

            for k in title_dict:
                WebDriverWait(self.browser, 5).until(
                    EC.visibility_of_element_located((By.ID, 'filter-element-{}-button'.format(k))))

            for elem in self.browser.find_elements_by_class_name('filter-option-button'):
                if ("(inactive)" in elem.get_attribute('data-original-title').lower() or
                        'gold' in elem.get_attribute('data-original-title').lower() or
                        'regular' in elem.get_attribute('data-original-title').lower()):
                    pass
                else:
                    elems.append(elem)
                    titles.append(elem.text.lower())

            options = {'titles': titles, 'elements': elems}

            for splinter in self.splinters:
                print(splinter)
                if splinter in options['titles']:
                    try:
                        # self.browser.find_element_by_xpath(
                        #     "//label[@for='filter-element-{}-button']".format(splinter)).click()
                        elem = self.browser.find_element_by_xpath(
                            "//label[@for='filter-element-{}-button']".format(splinter))
                        elem.location_once_scrolled_into_view
                        elem.click()

                    except:
                        self.log.debug('Script Execution Failed!!')

                    try:
                        act = ActionChains(self.browser)
                        act.move_to_element(
                            options['elements'][options['titles'].index(splinter)]).perform()
                        WebDriverWait(self.browser, 0.3)
                        act.click().perform()
                    except:
                        pass

                    card_c = title_dict[options['titles']
                                        [options['titles'].index(splinter)]]
                    splinter_selected = True
                    break

            if not splinter_selected:
                print('Splinter in config.ini is not present in the game!')
                try:
                    self.browser.find_element_by_xpath(
                        "//label[@for='filter-element-{}-button']".format(options['titles'][0])).click()
                    elem = self.browser.find_element_by_xpath(
                        "//label[@for='filter-element-{}-button']".format(options['titles'][0]))
                    elem.location_once_scrolled_into_view
                    elem.click()
                except:
                    self.log.debug('Script Execution Failed!!')

                try:
                    act = ActionChains(self.browser)
                    act.move_to_element(options['elements'][0]).perform()
                    WebDriverWait(self.browser, 0.3)
                    act.click().perform()
                except:
                    pass

                card_c = title_dict[options['titles'][0]]

            return card_c
        except Exception as e:
            return card_c

    # This functions sets summoners according to given color type or if none then it randomises the process
    def set_summoners(self):

        # Select a summoner
        card_selected = False

        try:
            try:
                self.browser.find_element_by_class_name(
                    'btn--create-team').send_keys(Keys.RETURN)
            except:
                pass

            WebDriverWait(self.browser, 2)
            self.wait_by_class('btn-green')
            self.wait_by_class("deck-builder-page2__cards")

            attempts = 2
            result = False

            while attempts:
                try:
                    summoner_elems = self.browser.find_elements_by_xpath(
                        "//div[@class='deck-builder-page2__cards']/div")
                    card_stats = self.browser.find_elements_by_xpath(
                        "//div[@class='deck-builder-page2__cards']/div/div[@class='relative-position']/div[@class='stat-mana']/div")
                    # /html/body/div[2]/div/div/div[4]/div[1]/div[2]/div[1]/div
                    card_stats_v2 = self.browser.find_elements_by_xpath(
                        "//div[@class='deck-builder-page2__cards']/div/div[@class='relative-position']/div[@class='stat-mana']")
                    print('sleeping')
                    try:
                        total_mana = self.browser.find_element_by_xpath(
                            "/html/body/div[2]/div/div/div[1]/div[1]/div/div/div[4]").text
                    except:
                        print('cannot get total mana')
                        time.sleep(200)

                    print(total_mana)
                    time.sleep(2)
                    total_mana = int(total_mana)
                    print(total_mana)
                    rem_mana = total_mana

                    summoners = {'id': [int(elem.get_attribute('card_detail_id')) for elem in summoner_elems],
                                 'card_color': [elem.get_attribute('card_color').lower() for elem in summoner_elems],
                                 'card_mana': [int(self.remove_Mana(elem.text)) for elem in card_stats],
                                 'elements': [elem for elem in summoner_elems]}
                    result = True
                    print('Account {}: Summoners Setup Complete!'.format(self.id))
                    self.log.debug(
                        'Account {}: Summoners Setup Complete!'.format(self.id))
                    break
                except StaleElementReferenceException as e:
                    print('Account {}: Retrying Summoners Setup...'.format(self.id))
                    self.log.debug(
                        'Account {}: Retrying Summoners Setup...'.format(self.id))
                    attempts -= 1

            if not result:
                raise StaleElementReferenceException

            if 0 in self.summoners_config:
                print('Account {}: Summoners card not specified! choosing default then...'.format(
                    self.id))
                self.summoners_config = []

            for summoner in self.summoners_config + self.summoners_default:
                # print('Account {}: Summoner id {} in summmoners id: {} '.format(self.id, summoner, summoners['id']))
                if summoner in summoners['id']:
                    self.click_on_card(self.browser.find_element_by_xpath(
                        "//div[@class='deck-builder-page2__cards']/div[@card_detail_id='{}']".format(summoner)))
                    card_c = summoners['card_color'][summoners['id'].index(
                        summoner)]
                    rem_mana -= summoners['card_mana'][summoners['id'].index(
                        summoner)]
                    card_selected = True
                    break

            if not card_selected:
                print('Account {}: Summoners card in config.ini is not present in the game!'.format(
                    self.id))
                self.click_on_card(summoners['elements'][0])
                rem_mana -= summoners['card_mana'][0]
                card_c = summoners['card_color'][0]

            print('Account {}: {} is chosen as Summoner!'.format(self.id, card_c))

            if card_c == 'gold':
                card_c = self.select_splinter(card_c)

            try:
                WebDriverWait(self.browser, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='cancel link-btn']")))
                self.browser.find_element_by_xpath(
                    "//button[@class='cancel link-btn']").click()
                print('\nAccount {}: !![WARNING]!! Dragon is not responding for this iteration!\n'.format(
                    self.id))
                self.log.error(
                    '!![WARNING]!! Dragon is not responding for this iteration!')
                raise NoSuchElementException
            except TimeoutException as e:
                self.set_cards(card_c, rem_mana, total_mana)

        except Exception as e:
            logging.error('Account {}: {}'.format(self.id, e), exc_info=True)
            self.log.error("Exception occurred", exc_info=True)
            return False
        return True

    # END - SUMMONERS AND CARDS SETUP FUNCTIONS

    # Start battle
    def start_battle(self):
        flg = False
        try:
            self.find_click_by_class(['btn-green'], [Keys.RETURN])

            count = 160
            while count:
                try:
                    WebDriverWait(self.browser, 1).until(
                        EC.visibility_of_element_located((By.XPATH, "//button[@class='btn btn--done']")))
                    self.browser.find_element_by_xpath(
                        "//button[@class='btn btn--done']").click()
                    break
                except:
                    try:
                        self.wait_by_id('btnRumble', 1)
                        self.find_click_by_id(['btnRumble'], [Keys.RETURN])
                        flg = True
                        break
                    except:
                        count -= 1
                if not count:
                    raise TimeoutException
            if flg:
                self.wait_by_id('btnSkip', 60)
                self.find_click_by_id(['btnSkip'], [Keys.RETURN])
                return True
        except Exception as e:
            print('Account {}: {}'.format(self.id, e))
        return False

    def battle_results(self):

        try:
            WebDriverWait(self.browser, 10).until(
                EC.visibility_of_element_located((By.XPATH, "//button[@class='btn btn--done']")))

            win_name = self.browser.find_elements_by_xpath(
                "//span[@class='bio__name__display']")[1].text
            win_guild_name = self.browser.find_elements_by_xpath(
                "//span[@class='bio__guild__name']")[0].text

            loser_name = self.browser.find_elements_by_xpath(
                "//span[@class='bio__name__display']")[4].text
            loser_guild_name = self.browser.find_elements_by_xpath(
                "//span[@class='bio__guild__name']")[3].text

            win_delta = self.browser.find_elements_by_xpath(
                "//span[@class='rating-delta']")[0].text
            win_score = self.browser.find_elements_by_xpath(
                "//span[@class='rating-total']")[0].text

            loser_delta = self.browser.find_elements_by_xpath(
                "//span[@class='rating-delta']")[1].text
            loser_score = self.browser.find_elements_by_xpath(
                "//span[@class='rating-total']")[1].text

            # Create score files and write
            path = os.path.join(os.getcwd(), "scores")
            if not os.path.exists(path):
                os.makedirs(path)

            now = datetime.now()
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            new_path = os.path.join(
                path, "{}_scores.txt".format(self.account[0]))

            f = open(new_path, 'a+')
            f.write(dt_string + '\n')
            f.write("Winner: {}".format(win_name) +
                    "\nWinner Guild: ".format(win_guild_name) +
                    "\nDelta: ".format(win_delta) +
                    "\nTotal: ".format(win_score) +
                    "\nLoser: ".format(loser_name) +
                    "\nLoser Guild: ".format(loser_guild_name) + "\n\n")

            f.close()

            print('Account {}: '.format(self.id))
            print("Winner: ", win_name)
            print("Winner Guild: ", win_guild_name)
            print("Delta: ", win_delta)
            print("Total: ", win_score)
            print("\nLoser: ", loser_name)
            print("Loser Guild: ", loser_guild_name)
            print("Delta: ", loser_delta)
            print("Total: ", loser_score)

            self.browser.find_element_by_xpath(
                "//button[@class='btn btn--done']").click()
        except Exception as e:
            logging.error(
                'Exception occured in battle_results()', exc_info=True)
            self.log.error(
                'Exception occured in battle_results()', exc_info=True)

    def calculate_target(self, input_array, target, slots):
        print('Calculate target got called')
        print('I received these values below')
        print('input_array')
        print(input_array)
        print('target')
        print(target)
        print('slots')
        print(slots)
        target_accumulated = 0
        target_val_index_array = []
        z = False
        for a in range(1, slots+1):
            for j in itertools.combinations(input_array, a):
                answer = 0
                for i in j:
                    answer += i
                if answer == target:
                    print(j)
                    target_val_index_array = j
                    target_accumulated = target
                    z = True
                    break
                if answer > target_accumulated and answer < target:
                    target_accumulated = answer
                    target_val_index_array = j
                if z == True:
                    break
            if z == True:
                break
        print('desired target '+str(target))
        print('target I could get'+str(target_accumulated))
        print('numbers that add up to accumulated target' +
              str(target_val_index_array))
        return target_val_index_array

    def start_browser(self):
        starttime = time.time()
        flag = False
        success = 0
        url = "https://splinterlands.com"

        print('Account {}: Starting bot...'.format(self.id))
        try:
            # Create browser
            # binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
            #
            # cap = DesiredCapabilities().FIREFOX
            # cap["marionette"] = True  # optional
            #
            # url = "https://splinterlands.com"
            # options = Options()
            # options.headless = True
            # options.binary = binary
            # self.browser = webdriver.Firefox(capabilities=cap, options=options)
            # self.browser.get(url)

            options = Options()
            # options.headless = True
            # options.add_argument("--headless")
            # options.add_argument("--disable-gpu")
            # options.add_argument("--disable-extensions")
            # options.add_argument('--no-proxy-server')
            # options.add_argument("--proxy-server='direct://'")
            # options.add_argument("--proxy-bypass-list=*")
            options.add_argument("--log-level=3")
            self.browser = webdriver.Chrome(options=options)
            self.browser.maximize_window()
            self.browser.get(url)

            self.wait_by_id('log_in_button', 20)
            self.browser.find_element_by_xpath(
                "//li[@id='log_in_button']/button").send_keys(Keys.RETURN)

            for i in range(3):
                flag = self.login(self.account)
                if flag:
                    break
                print('Account {}: Trying to login again...'.format(self.id))

            if not flag:
                return False

            print('Account {}: Logged in Successfully!'.format(self.id))

            # for i in range(3):
            self.override_welcome_page()

            for i in range(self.times):
                completion = False
                print('Account {} Iteration Number: {}'.format(self.id, i + 1))
                self.log.debug("Iteration Number: {}".format(i + 1))
                if self.start_match():
                    print('Account {}: Match started!'.format(self.id))
                    print('Match Started Successfully')
                    if self.set_summoners():
                        print('set_summoners successfully')
                        if self.start_battle():
                            self.battle_results()
                            completion = True
                            success += 1

                if completion:
                    print('Account {}: Iteration {} Completed!'.format(
                        self.id, i + 1))
                    self.log.debug(
                        'Account {}: Iteration {} Completed!'.format(self.id, i + 1))
                else:
                    print('Account {}: Iteration {} Failed!!'.format(self.id, i + 1))
                    self.log.debug(
                        'Account {}: Iteration {} Failed!!'.format(self.id, i + 1))
        except TimeoutException as e:
            print('Account {}: Timeout Error!'.format(self.id))
            self.log.exception("Exception in start_browser(): ", exc_info=True)
        except Exception as e:
            self.log.exception("Exception in start_browser(): ", exc_info=True)
            print('Account {}: {}'.format(self.id, e))

        self.release_handlers()
        print('Bot {} completed  {} matches!'.format(self.id, success))
        print('Bot {} took {} seconds'.format(
            self.id, time.time() - starttime))
        self.log.debug(
            'Bot {} completed  {} matches!'.format(self.id, success))
        self.log.debug('Bot {} took {} seconds'.format(
            self.id, time.time() - starttime))


def clear():
    os.system('cls')


def create_logs(id):
    path = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(path):
        os.makedirs(path)

    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    new_path = os.path.join(path, dt_string + "_Account_{}.log".format(id))
    f = open(new_path, 'w+')
    f.close()

    return new_path


def get_summ_and_cards():

    try:

        with open('cards.txt') as json_file:
            data = json.load(json_file)

        card_detail_id = {'summoners': [s['id'] for s in data if s['type'].lower() == 'summoner'],
                          'monsters': [m['id'] for m in data if m['type'].lower() == 'monster']}

        return card_detail_id

    except Exception:
        logging.exception("Exception in get_summ_and_cards(): ")
        return False

# CHOICE functions


def insert_account():

    while True:
        config = configparser.ConfigParser()
        config.read('config.ini')

        print()
        for key, val in enumerate(config['ACCOUNTS']):
            print(str(key + 1) + '.', val, config['ACCOUNTS'][val])
        print("0. Return back to main menu")

        user = input('\nEnter the username or press 0: ')

        if user == '0':
            break

        password = input('Enter the password: ')

        if not user.isspace() and not password.isspace() and user != '' and password != '':
            config['ACCOUNTS'][user] = password
            config['SUMMONERS'][user] = '0'
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
        else:
            print('Invalid username or password!')

        clear()


def delete_account():

    while True:
        config = configparser.ConfigParser()
        config.read('config.ini')

        ids = [k for k in config['ACCOUNTS']]

        print()
        for key, val in enumerate(config['ACCOUNTS']):
            print(str(key + 1) + '.', val, config['ACCOUNTS'][val])
        print("0. Return back to main menu")

        num = input('Enter the number(s):')

        if num == '0':
            return False

        for n in num.split(' '):
            if n.isnumeric() and int(n) - 1 < len(ids) and int(n) - 1 >= 0:
                config.remove_option('ACCOUNTS', ids[int(n) - 1])
                config.remove_option('SUMMONERS', ids[int(n) - 1])
                print('\nAccount {} was deleted!'.format(int(n)))
            else:
                print('\nInvalid choice!')

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        clear()


def set_summoners_config(summ_ids):

    while True:
        config = configparser.ConfigParser()
        config.read('config.ini')

        for key, val in enumerate(config['ACCOUNTS']):
            if config['SUMMONERS'][val] == '0':
                print(str(key + 1) + '.', val, '-')
            else:
                print(str(key+1)+'.', val, config['SUMMONERS'][val])
        print("0. Return back to main menu")

        ids = [k for k in config['ACCOUNTS']]

        num = input('\nEnter the number(s): ')

        if num == "0":
            break

        for n in num.split(' '):
            if n.isnumeric() and int(n)-1 < len(ids) and int(n)-1 >= 0:
                summ = input('\nEnter the summoner id(s): ')
                summs = ''
                for i in summ.split(' '):
                    if i.isnumeric() and int(i) in summ_ids:
                        summs += i + ' '
                        print("\nSummoner id '{}' for account '{}' is successfully set!".format(
                            i, ids[int(n)-1]))
                    else:
                        print("\nSummoner id '{}' is invalid!".format(i))
                config['SUMMONERS'][ids[int(n) - 1]
                                    ] = '0' if summs == '' else summs
            else:
                print('\nInvalid choice!')
                continue

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        input('\nPress Enter to continue...')
        clear()


def set_splinter_config():

    colors = ['water',
              'fire',
              'dragon',
              'earth',
              'life',
              'death']

    while True:
        config = configparser.ConfigParser()
        config.read('config.ini')

        i = 1
        for val in config['SPLINTERS']['splinters'].split(' '):
            print('{}. {}'.format(i, val))
            i += 1
        print("0. Return back to main menu")

        spl = input("\nEnter splinters for dragon card or press 0: ")

        if spl == '0':
            break

        color_list = []
        for color in spl.split(' '):
            if color in colors:
                color_list.append(color)
                print('\n{} was added!'.format(color))
            else:
                print('\n{} is invalid splinter!'.format(color))

        config['SPLINTERS']['splinters'] = ' '.join(color_list)

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        input('\nPress Enter to continue...')
        clear()


def set_cards_config(card_ids):

    while True:
        config = configparser.ConfigParser()
        config.read('config.ini')

        for key, val in enumerate(config['CARDS']):
            mana_str = '  '
            try:
                mana_dict = json.loads(config.get('CARDS', val))
                for v in mana_dict:
                    mana_str += v + ': ' + \
                        ' '.join([str(i) for i in mana_dict[v]]) + '\n  '
                print(str(key + 1) + '.', val + ':\n' + mana_str)
            except:
                print(str(key + 1) + '.', val)

        print("0. Return back to main menu")

        c = input('\nSelect card type: ')

        card_type = [i[0] for i in config.items('CARDS')]

        if c.isnumeric() and int(c) - 1 < len(card_type) and int(c) - 1 >= 0:
            cards = json.loads(config.get('CARDS', card_type[int(c) - 1]))
        elif c == '0':
            break
        else:
            print('\nInvalid choice!')
            continue

        num = input('\nEnter mana(s): ')
        card = input('\nEnter the monster card id(s): ')

        nums = []
        for n in num.split(' '):
            if '-' in n:
                nums = [str(i) for i in range(
                    int(n.split('-')[0])-1, int(n.split('-')[1]))]
            for i in n.split('-') + nums:
                if i.isnumeric():
                    cards[i] = []
                    for cd in card.split(' '):
                        if cd.isnumeric() and int(cd) in card_ids:
                            cards[i].append(int(cd))
                        else:
                            print("\nCard id '{}' is invalid!".format(cd))
                else:
                    print('\nNot a valid mana!')

        print(cards)
        config.set('CARDS', card_type[int(c) - 1], json.dumps(cards))

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        input('\nPress Enter to continue...')
        clear()


def reset_summoners():

    ch = input('Are you sure you want to reset summoners?(y or n): ')

    if ch == 'y':
        config = configparser.ConfigParser()
        config.read('config.ini')

        for acc in config['ACCOUNTS']:
            config['SUMMONERS'][acc] = '0'

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        print("\nSummoners in config file successfully resetted!")

    return True


def reset_cards():
    ch = input('Are you sure you want to reset all cards?(y or n): ')

    if ch == 'y':
        config = configparser.ConfigParser()
        config.read('config.ini')

        card_types = [c for c in config['CARDS']]

        for c in card_types:
            config.set('CARDS', c, json.dumps({}))

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

        print("\nCards in config file successfully resetted!")

    return True


def get_all_info():

    config = configparser.ConfigParser()
    config.read('config.ini')

    return {'accounts': [[v, config['ACCOUNTS'][v]] for v in config['ACCOUNTS']],
            'summoners': [list(map(int, config['SUMMONERS'][v].split(' '))) for v in config['SUMMONERS']],
            'splinters': config['SPLINTERS']['splinters'].split(' '),
            'cards': [[v, json.loads(config['CARDS'][v])] for v in config['CARDS']],
            'default': [int(v) for v in config['SUMM_DEFAULT']['ids'].split(' ')]}


def set_accounts_and_run(all_info):
    filtered_info = {'accounts': [], 'summoners': []}

    for k, v in enumerate(all_info['accounts']):
        print("{}. {}".format(k + 1, v[0]))
    print("0. Select all")

    num = input('\nEnter any number(s): ')

    if num == '0':
        print('All accounts are selected!')
        return {'accounts': all_info['accounts'],
                'summoners': all_info['summoners']}

    nums = []
    for n in num.split(' '):
        if '-' in n:
            nums.extend(range(int(n.split('-')[0])-1, int(n.split('-')[1])))
        if n.isnumeric():
            nums.append(int(n)-1)
    nums.sort()

    for i in range(len(nums)-1, -1, -1):
        if nums[i] >= len(all_info['accounts']) or nums[i] < 0:
            nums.pop(nums[i])
            print('\n{} is Invalid choice!'.format(nums[i]))
        else:
            break

    for i in nums:
        filtered_info['accounts'].append(all_info['accounts'][i])
        filtered_info['summoners'].append(all_info['summoners'][i])
        print("Account {} {} is selected!".format(
            i + 1, all_info['accounts'][i][0]))

    return filtered_info


def main():

    card_detail_id = get_summ_and_cards()

    if not card_detail_id:
        print('\nTheres some problem with your internet please restart the program')
        return

    while True:

        cont = False
        print(info)
        choice = input(select_str)

        if choice.isnumeric():
            clear()
            if choice == '1':
                insert_account()
            elif choice == '2':
                delete_account()
            elif choice == '3':
                set_summoners_config(card_detail_id['summoners'])
            elif choice == '4':
                set_splinter_config()
            elif choice == '5':
                set_cards_config(card_detail_id['monsters'])
            elif choice == '6':
                cont = reset_summoners()
            elif choice == '7':
                cont = reset_cards()
            elif choice == '0':
                break
        else:
            continue

        if cont:
            input('\nPress Enter to continue...')

        clear()

    all_info = get_all_info()

    print("{} accounts detected!".format(len(all_info['accounts'])))

    filtered_info = set_accounts_and_run(all_info)

    times = []
    for i in range(1, len(filtered_info["accounts"]) + 1):
        while True:
            try:
                times.append(int(input(
                    'For Account {} enter the number of times the bot should run: '.format(i))))
                break
            except:
                continue
    clear()

    bots = []
    # processes = []
    threads = []

    for i in range(len(filtered_info["accounts"])):
        bots.append(Bot(i+1,
                        filtered_info["accounts"][i],
                        filtered_info["summoners"][i],
                        all_info["default"],
                        all_info['splinters'],
                        dict(all_info["cards"]),
                        times[i]))
        # processes.append(multiprocessing.Process(target=bots[i].start_browser))
        # processes[i].start()
        threads.append(threading.Thread(target=bots[i].start_browser))
        threads[i].start()

    for i in range(len(filtered_info["accounts"])):
        # processes[i].join()
        threads[i].join()


if __name__ == '__main__':
    main()
