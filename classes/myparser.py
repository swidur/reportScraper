import time
from bs4 import BeautifulSoup
import logging as log

class myParser:
    def __init__(self):
        pass

    def get_data(self,source):
        self.source = BeautifulSoup(source, 'html.parser')
        daty = []
        nazwy = []
        linki = []

        table = self.source.find('table', attrs={'class': 'table-dynamic'})
        rows = table.find_all('tr')

        for row in rows:
            columns = row.find_all('td')
            cols = [ele.text.strip() for ele in columns]
            tab = [ele for ele in cols if ele]
            # print(tab)
            if tab:
                daty.append(time.strptime((tab[1][0:10]), "%Y-%m-%d"))
                nazwy.append(tab[2].split('.SWX')[0] + '.SWX')

            for col in columns:
                anchors = col.find_all('a')
                for element in anchors:
                    if (element.attrs['href'][:31]) == '../../user/komstatmed/ppzrapget':
                        linki.append('https://szoi.nfz.poznan.pl/ap-mzwi' + element.attrs['href'][5:])



        return list(zip(nazwy, daty, linki))

