import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging as log
import time


class Crawler:
    def __init__(self, browser, parser, username, password, since, till, status):
        self.browserInstance = browser.browserInstance
        self.browser = browser
        self.parser = parser
        self.eol = 0
        self.selected = []

        self.username = username
        self.password = password
        self.since = since
        self.till = till
        self.status = status

    def is_running(self):
        return self.browser.browserFlag

    def close_browser(self):
        log.warning('Close browser called')
        self.browser.stop_browser()

    def login_szoi(self):
        while self.is_running():
            self.browserInstance.get(r"https://szoi.nfz.poznan.pl/ap-mzwi/")
            if 'prace serwisowe' in self.browserInstance.page_source:
                msg = 'Prace serwisowe'
                log.error(msg)
                self.close_browser()
                break

            self.browserInstance.switch_to.frame(self.browserInstance.find_element_by_name('info'))
            username = self.browserInstance.find_element_by_name("FFFRAB0520login")
            password = self.browserInstance.find_element_by_name("FFFRAB0520pasw")
            username.send_keys(self.username)
            password.send_keys(self.password)
            self.browserInstance.find_element_by_name("sub1").click()

            if 'Wprowadzono błędny PIN lub błędne hasło' in self.browserInstance.page_source:
                msg = 'Wprowadzono błędny PIN lub błędne hasło'
                log.error(msg)
                self.close_browser()

            elif 'W celu dalszej pracy z systemem wymagana jest zmiana hasła.' in self.browserInstance.page_source:
                msg = 'Wymagana zmiana hasła operatora'
                log.error(msg)
                self.close_browser()

            else:
                self.browserInstance.get("https://szoi.nfz.poznan.pl/ap-mzwi/servlet/komstatmed/raport")
                log.info('logged into SZOI')

            break

    def order_by_status(self):
        if self.is_running():
            rapport_status = self.browserInstance.find_element_by_name("FFFOAXrapZwr")
            if self.status == 0:
                rapport_status.send_keys('-')
                log.info('Filtered rapports by "all"')
            elif self.status == 1:
                rapport_status.send_keys('z')
                log.info('Filtered rapports by "not downloaded"')
            self.browserInstance.find_element_by_name('SEARCH_BUTTON').click()

    def get_source(self):
        return self.browserInstance.page_source

    def next_page(self):
        if self.is_running():
            log.info('Request next page')
            try:
                WebDriverWait(self.browserInstance, 3).until(EC.presence_of_element_located((By.XPATH, "//input[@value='20 >> ']")))
                self.browserInstance.find_element_by_xpath("//input[@value='20 >> ']").click()
                log.info('Next page reached')

            except selenium.common.exceptions.TimeoutException:
                self.eol = 1
                log.info('Run out of pages to load, set "end of list [self.eol] to 1"')

    def select(self):
        if self.is_running():
            self.all_pages = self.parser.get_data(self.get_source())
            self.are_we_there()

            for row in self.all_pages:
                if self.since <= row[1] <= self.till:
                    self.selected.append(row)

            msg = 'There are total of {} rapports in between these dates'.format(len(self.selected))
            log.warning(msg)
            self.down_selected()

    def are_we_there(self):
        if self.since > (self.all_pages[-1][1]) or self.eol:
            if self.eol:
                log.info('Crawler.eol = 1, list goes to selection')
            else:
                log.info('-Since date- is within gathered links, list goes to selection')

        else:
            log.info('Going to request another page..')
            self.next_page()
            tab = self.parser.get_data(self.get_source())
            for row in tab:
                self.all_pages.append(row)
            log.info('Appended new data to all_pages')
            self.are_we_there()
            log.info('Checking again')



    def down_selected(self):
        selected = self.selected
        if len(selected) > 0 and self.is_running():
            counter = 0
            count = len(selected)

            for raport in selected:
                self.browserInstance.get(raport[2])
                self.browserInstance.find_element_by_name("BUTX_NEXT").click()
                msg = 'Waiting for rapport "{0}" from {1}'.format(raport[0], time.strftime("%Y-%m-%d", raport[1]))
                log.info(msg)

                try:
                    WebDriverWait(self.browserInstance, 15).until(EC.presence_of_element_located((By.LINK_TEXT, "pobierz plik")))
                    self.browserInstance.find_element_by_link_text("pobierz plik").click()
                    self.browserInstance.find_element_by_name("BUTX_FINISH").click()
                    counter += 1
                    msg = 'Downloaded rapport {} out of {}'.format(counter, count)
                    log.warning(msg)

                except selenium.common.exceptions.TimeoutException:
                    msq = 'Waited for 60s, and still couldnt find "pobierz plik"'
                    log.error(msq)


                if counter == count:
                    # self.browser_methods.stop_browser()
                    self.browserInstance.close()
                    self.browserInstance.quit()

                    msg = 'Download complete. {} file/s downloaded'.format(counter)

                    log.warning(msg)


        else:
            msg = 'No files for given dates or encountered unknown error'
            log.error(msg)
            self.close_browser()


