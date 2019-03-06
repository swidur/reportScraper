import logging as log
from os import getcwd
from sys import path

from selenium import webdriver
from selenium.webdriver.remote.remote_connection import LOGGER

path.append(getcwd())


class myBrowser:
    def __init__(self, dl_dir='C:\KS\swzScraper', headless=1):
        self.dl_dir = dl_dir
        self.headless = headless
        self.browserInstance = None
        self.browserFlag = True

    def set_download_dir(self, new_dl_dir):
        self.dl_dir = new_dl_dir
        msg = 'Download directory is: {}'.format(self.dl_dir)
        log.info(msg)

    def enable_download_in_headless_chrome(self):
        # add missing support for chrome "send_command"  to selenium webdriver by  shawnbut...@gmail.com
        self.browserInstance.command_executor._commands["send_command"] = (
            "POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self.dl_dir}}
        self.browserInstance.execute("send_command", params)

    def init_browser(self):
        log.debug('Creating browser instance')
        service_args = None

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option('prefs', {'download.default_directory': self.dl_dir})
        LOGGER.setLevel(log.CRITICAL)
        log.getLogger("urllib3").setLevel(log.CRITICAL)

        if self.headless:
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_argument('headless')
            log.debug('Chrome in headless mode')

        else:
            log.warning('DEBUG MODE: verbose logging + chromedriver.log in cwd')
            service_args = ["--log-path=chromedriver.log"]

        self.browserInstance = webdriver.Chrome(options=chrome_options, service_args=service_args)
        self.enable_download_in_headless_chrome()

    def stop_browser(self):
        self.browserInstance.close()
        self.browserInstance.quit()
        self.browserFlag = False
        log.warning('Closing browser. Bye for now')
