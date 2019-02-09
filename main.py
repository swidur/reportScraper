import datetime
import logging as log
import os
import time
import urllib.request as request
import zipfile
from urllib import error

from classes.browser import myBrowser
from classes.crawler import Crawler
from classes.myparser import myParser

log.basicConfig(filename='swzDEBUG.log', format='%(asctime)s %(levelname)s: %(message)s',
                datefmt='/%d-%m-%Y %H:%M:%S/', level='INFO')


# log = logging.getLogger('swzScraperDebug')
# log.setLevel(logging.DEBUG)
#
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
#
# formatter = logging.Formatter('%(asctime)s %(name)% %(levelname)s: %(message)s')
# ch.setFormatter(formatter)
# log.addHandler(ch)
#

class Main:
    def __init__(self, directory="C:\ks\swzScraper"):
        self.directory = directory
        self.downloadChromedriver()
        self.get_input()

    def get_input(self):
        while True:
            self.username = input('Login: ')
            if 21 > len(self.username) > 4:
                break
            self.invald_input(self.username, 'To pole musi mieć długość pomiędzy 5 a 20 znaków.')
        while True:
            self.password = input('Hasło: ')
            if 21 > len(self.password) > 4:
                break
            self.invald_input(self.password, 'To pole musi mieć długość pomiędzy 5 a 20 znaków.')

        while True:
            while True:
                self.since = input('Raporty od [rrrr-mm-dd]: ')
                try:
                    self.since = time.strptime(self.since, '%Y-%m-%d')
                    break
                except ValueError:
                    self.invald_input('DATA', msg="Niepoprawny format daty 'od'")

            while True:
                self.till = input('Raporty do [rrrr-mm-dd]: ')
                try:
                    self.till = time.strptime(self.till, '%Y-%m-%d')
                    break
                except ValueError:
                    self.invald_input('DATA', msg="Niepoprawny format daty 'do'")

            if self.since <= self.till:
                break
            self.invald_input('', 'Niepoprawny zakres, "do" nie może być mniejsze od "od"')

        while True:
            self.status = input('Status raportów [n]owe/[w]szystkie: ')
            if self.status.lower() in ('n', 'nowe'):
                self.status_val = 1
                break
            elif self.status.lower() in ('w', 'wszystkie'):
                self.status_val = 0
                break
            self.invald_input(self.status)

        while True:
            self.head = input('Widoczność przeglądarki [0/1]: ')
            if self.head == '1':
                self.head = 1
                break
            elif self.head == '0':
                self.head = 0
                break
            self.invald_input(self.head)

        self.run()

    def invald_input(self, value, msg=''):
        invalid = ("Podana wartość: [{}] jest nieprawidłowa. ".format(value) + msg)
        log.warning(invalid)
        print(invalid)

    def run(self):
        chrome = myBrowser(headless=self.head)
        chrome.set_download_dir("{0}/{1}_{2}".format(self.directory, self.username,
                                                     str(datetime.datetime.now()).split('.')[0].replace(' ', '_')))
        chrome.init_browser()

        parser = myParser()

        crawler = Crawler(chrome, parser, self.username, self.password, self.since, self.till, self.status_val)

        crawler.login_szoi()
        crawler.order_by_status()
        crawler.select()

    def downloadChromedriver(self):
        if not os.path.exists("chromedriver.exe"):
            no_driver = "Chromedriver not found in cwd, attempting download.."
            log.error(no_driver)
            try:
                request.urlretrieve("https://chromedriver.storage.googleapis.com/2.43/chromedriver_win32.zip",
                                    "chromedriver.zip")
            except error.URLError:
                download_failed = "Chromedriver could not be downloaded"
                log.error(download_failed)
            if os.path.exists("chromedriver.zip"):
                with zipfile.ZipFile('chromedriver.zip', mode='r') as chrome_zip:
                    chrome_zip.extract('chromedriver.exe')
                    chrome_zip.close()
                    os.remove("chromedriver.zip")
            else:
                log.error("Unhandled download error")


main = Main()
