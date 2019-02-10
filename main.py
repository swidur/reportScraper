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


class Main:
    def __init__(self, directory="C:\ks\\reportScraper"):

        log.basicConfig(filename='reportINFO.log', format='%(asctime)s %(levelname)s: %(message)s',
                        datefmt='/%d-%m-%Y %H:%M:%S/', level='INFO')

        log.info('*********** Logging ***********')
        info = 'reportScraper by Dawid Świdurski https://github.com/swidur/reportScraper'
        log.info(info)
        print(info)

        self.directory = directory
        self.reader_directory = None
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
                self.since_input = input('Raporty od [rrrr-mm-dd]: ')
                try:
                    self.since = time.strptime(self.since_input, '%Y-%m-%d')
                    break
                except ValueError:
                    self.invald_input(self.since_input, "Niepoprawny format daty 'od'")

            while True:
                self.till_input = input('Raporty do [rrrr-mm-dd]: ')
                try:
                    self.till = time.strptime(self.till_input, '%Y-%m-%d')
                    break
                except ValueError:
                    self.invald_input(self.till_input, "Niepoprawny format daty 'do'")

            if self.since <= self.till:
                break
            self.invald_input('', 'Niepoprawny zakres, "do" nie może być mniejsze od "od"')

        while True:
            self.status = input('Status raportów [n]owe/[w]szystkie: ')
            if self.status.lower() in ('n', 'nowe'):
                self.status = 1
                break
            elif self.status.lower() in ('w', 'wszystkie'):
                self.status = 0
                break
            self.invald_input(self.status)

        while True:
            self.head = input('Widoczność przeglądarki [t]ak/[n]ie: ')
            if self.head.lower() in ('tak', 't'):
                self.head = 0
                break
            elif self.head.lower() in ('nie', 'n'):
                self.head = 1
                break
            elif self.head.lower() == 'debug':
                self.head = 0
                log.getLogger().setLevel('DEBUG')
                break
            self.invald_input(self.head)

        while True:
            self.fromfile = input('Pobierz raporty, które pominięto w innej sesji [t]ak/[n]ie: ')
            if self.fromfile in ('tak', 't'):
                self.fromfile = 1
                break
            elif self.fromfile in ('nie', 'n'):
                self.fromfile = 0
                break
            self.invald_input(self.fromfile)

        if self.fromfile:
            while True:
                self.reader_directory = input('Ścieżka do pliku csv z pominiętymi raportami: ')
                try:
                    test = open(self.reader_directory, 'r')
                    test.close()
                    break
                except FileNotFoundError:
                    self.invald_input(self.reader_directory, 'File not found')

        while True:
            directory_input = input('Ścieżka zapisu raportów [domyślna: C:\KS\\reportScraper\.. ]: ')
            if directory_input == '':
                break
            self.directory = directory_input
            break

        log.info(
            "User: {0}, since: {1} till: {2}, status: {3}, browser: {4}, fromfile: {5}, fromfile dir: {6}, download dir: {7}".format(
                self.username, time.strftime("%Y-%m-%d", self.since), time.strftime("%Y-%m-%d", self.till), self.status,
                self.head, self.fromfile, self.reader_directory, self.directory))

        self.run()

    def invald_input(self, value, msg=''):
        invalid = ("Podana wartość: [{0}] jest nieprawidłowa. ".format(value) + msg)
        log.warning(invalid)
        print(invalid)

    def run(self):
        chrome = myBrowser(headless=self.head)
        reportDirectory = "{0}\{1}_{2}".format(self.directory, self.username,
                                               str(datetime.datetime.now()).split('.')[0].replace(' ', '_').replace(':',
                                                                                                                    ''))
        chrome.set_download_dir(reportDirectory)
        chrome.init_browser()

        parser = myParser()

        crawler = Crawler(chrome, parser, self.username, self.password, self.since, self.till, self.status,
                          reportDirectory, self.fromfile, self.reader_directory)

        if crawler.login_szoi():
            crawler.order_by_status()
            crawler.select()

    def downloadChromedriver(self):
        if not os.path.exists("chromedriver.exe"):
            msg = "Chromedriver not found in cwd, attempting download.."
            log.error(msg)
            print(msg)
            try:
                request.urlretrieve("https://chromedriver.storage.googleapis.com/2.43/chromedriver_win32.zip",
                                    "chromedriver.zip")
            except error.URLError:
                msg = "Chromedriver could not be downloaded"
                log.error(msg)
                print(msg)
            if os.path.exists("chromedriver.zip"):
                with zipfile.ZipFile('chromedriver.zip', mode='r') as chrome_zip:
                    chrome_zip.extract('chromedriver.exe')
                    chrome_zip.close()
                    os.remove("chromedriver.zip")
                    msg = 'Chromedriver downloaded successfully'
                    log.info(msg)
                    print(msg)
            else:
                log.error("Unhandled download error")
                print(msg)


main = Main()
