import logging as log
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from classes.csvReader import Reader
from classes.csvWriter import Writer


class Crawler:
    def __init__(self, browser, parser, username, password, since, till, status, directory, fromfile,
                 reader_directory=None):
        self.browserInstance = browser.browserInstance
        self.browser = browser
        self.parser = parser
        self.eol = 0
        self.selected = []
        self.directory = directory
        self.fromfile = fromfile
        self.reader_directory = reader_directory

        self.downloaded = []
        self.not_downloaded = []

        self.username = username
        self.password = password
        self.since = since
        self.till = till
        self.status = status

        self.downloaded_filename = 'pobrane.csv'
        self.not_downloaded_filename = 'pominiete.csv'

        self.downloaded_writer = Writer(self.directory, self.downloaded_filename)
        self.not_downloaded_writer = Writer(self.directory, self.not_downloaded_filename)

        self.timeout = 60

        if self.fromfile:
            reader = Reader(self.reader_directory)
            reader_contents = reader.readFromCsv()
            if type(reader_contents) == bool:
                msg = 'Reader encountered error with csv file. Consult logs about details - exiting now'
                log.critical(msg)
                print(msg)
                self.close_browser()
            else:
                self.report_names = []
                for line in reader_contents:
                    self.report_names.append(line[0])

    def is_running(self):
        return self.browser.browserFlag

    def close_browser(self):
        log.debug('close_browser called')
        self.browser.stop_browser()

    def check_condition(self, source_string, message=None, exit_on_success=True):
        log.debug('Checking condition for: {0}'.format(source_string))
        if message is None:
            message = source_string

        source = self.browserInstance.page_source

        if source_string not in source:
            try:
                self.browserInstance.switch_to.frame(self.browserInstance.find_element_by_name('tekst'))
                source = self.browserInstance.page_source

                if source_string not in source:
                    return False

            except selenium.common.exceptions.NoSuchElementException:
                return False

        log.error(message)
        print(message)
        if exit_on_success:
            self.close_browser()
        return True

    def login_szoi(self):
        if self.is_running():
            self.browserInstance.get(r"https://szoi.nfz.poznan.pl/ap-mzwi/")
            if 'prace serwisowe' in self.browserInstance.page_source:
                msg = 'SZOI: Prace serwisowe.'
                log.error(msg)
                print(msg)
                self.close_browser()
                return False

            try:
                self.browserInstance.switch_to.frame(self.browserInstance.find_element_by_name('info'))
            except selenium.common.exceptions.NoSuchElementException:
                msg = 'https://szoi.nfz.poznan.pl/ap-mzwi/ could not be reached. Check your internet connection and service availability.'
                log.error(msg)
                print(msg)
                return False

            username = self.browserInstance.find_element_by_name("FFFRAB0520login")
            password = self.browserInstance.find_element_by_name("FFFRAB0520pasw")
            username.send_keys(self.username)
            password.send_keys(self.password)
            self.browserInstance.find_element_by_name("sub1").click()

            if self.check_condition('Wprowadzono błędny PIN lub błędne hasło'):
                return False
            if self.check_condition('W celu dalszej pracy z systemem wymagana jest zmiana hasła.'):
                return False
            if self.check_condition(
                    'Uwaga: Dalsza praca w systemie możliwa po potwierdzeniu zapoznania się z komunikatem.'):
                return False
            if self.check_condition('Konto zostało czasowo zablokowane'):
                return False
            if self.check_condition('System: System zarządzania obiegiem informacji', 'User logged in successfully',
                                    False):
                self.browserInstance.get("https://szoi.nfz.poznan.pl/ap-mzwi/servlet/komstatmed/raport")
                return True

            else:
                log.critical('Unhandled situation while logging in')
                self.close_browser()
                return False


    def order_by_status(self):
        if self.is_running():
            report_status = self.browserInstance.find_element_by_name("FFFOAXrapZwr")
            if self.status == 0:
                report_status.send_keys('-')
                log.info('Filtered reports by "all"')
            elif self.status == 1:
                report_status.send_keys('z')
                log.info('Filtered reports by "not downloaded"')
            self.browserInstance.find_element_by_name('SEARCH_BUTTON').click()

    def get_source(self):
        return self.browserInstance.page_source

    def next_page(self):
        if self.is_running():
            log.debug('Request next page')
            try:
                WebDriverWait(self.browserInstance, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@value='20 >> ']")))
                self.browserInstance.find_element_by_xpath("//input[@value='20 >> ']").click()
                log.debug('Next page reached')

            except selenium.common.exceptions.TimeoutException:
                self.eol = 1
                log.debug('Run out of pages to load, set "end of list [self.eol] to 1"')

    def select(self):
        start = time.time()
        if self.is_running():
            self.all_pages = self.parser.get_data(self.get_source())
            self.are_we_there()

        if self.fromfile:
            for row in self.all_pages:
                if (self.since <= row[1] <= self.till) and (row[0] in self.report_names):
                    self.selected.append(row)
        else:
            for row in self.all_pages:
                if self.since <= row[1] <= self.till:
                    self.selected.append(row)

        msg = 'There are total of {} reports in between these dates'.format(len(self.selected))
        log.info(msg)
        print(msg)
        stop = time.time()
        log.info('Report lookup took: {0}s'.format(round(stop - start, 2)))
        self.down_selected(self.selected)

    def are_we_there(self):
        log.debug('Checking if we since date is reached')
        if self.since > (self.all_pages[-1][1]) or self.eol:
            if self.eol:
                log.debug('Crawler.eol = 1, list goes to selection')
            else:
                log.debug('-Since date- is within gathered links, list goes to selection')

        else:
            log.debug('Going to request another page..')
            self.next_page()
            tab = self.parser.get_data(self.get_source())
            for row in tab:
                self.all_pages.append(row)
            log.debug('Appended new data to all_pages')
            self.are_we_there()

    def down_selected(self, selected):
        if len(selected) > 0 and self.is_running():
            counter = 0
            time_sum = 0
            count = len(selected)

            for report in selected:
                start = time.time()
                self.browserInstance.get(report[2])
                self.browserInstance.find_element_by_name("BUTX_NEXT").click()
                msg = 'Waiting for report "{0}" from {1}'.format(report[0], time.strftime("%Y-%m-%d", report[1]))
                log.debug(msg)

                try:
                    WebDriverWait(self.browserInstance, self.timeout).until(
                        EC.presence_of_element_located((By.LINK_TEXT, "pobierz plik")))
                    self.browserInstance.find_element_by_link_text("pobierz plik").click()
                    self.browserInstance.find_element_by_name("BUTX_FINISH").click()
                    stop = time.time()
                    download_time = round(stop - start, 2)
                    time_sum += download_time
                    counter += 1
                    msg = 'Downloaded report {0} out of {1}. Action took: {2}'.format(counter, count,
                                                                                      download_time)
                    print(msg)
                    log.warning(msg)
                    self.downloaded.append(report)


                except selenium.common.exceptions.TimeoutException:
                    log.error('Waited for {0}s for {1}. Moving on to the next'.format(self.timeout, report[0]))
                    print(msg)
                    self.not_downloaded.append(report)

                except selenium.common.exceptions.NoSuchElementException:
                    log.error('Element not found')
                    print(msg)
                    self.not_downloaded.append(report)

            self.close_browser()
            msg = 'Download complete. {0} file/s downloaded. Mean time: {1}'.format(counter, time_sum / counter)
            print(msg)
            log.info(msg)

            if self.downloaded:
                self.downloaded_writer.loadContent(self.downloaded)
                self.downloaded_writer.writeToCsv()
            if self.not_downloaded:
                log.warning("Some files were not downloaded, check {0} in {1}".format(self.not_downloaded_filename,
                                                                                      self.directory))
                print(msg)
                self.not_downloaded_writer.loadContent(self.not_downloaded)
                self.not_downloaded_writer.writeToCsv()


        else:
            msg = 'No files for given dates or encountered unknown error'
            print(msg)
            log.error(msg)
            self.close_browser()
