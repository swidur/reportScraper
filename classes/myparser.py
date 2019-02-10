import time

from bs4 import BeautifulSoup


class myParser:
    def __init__(self):
        pass

    def get_data(self, source):
        self.source = BeautifulSoup(source, 'html.parser')
        daty = []
        filenames = []
        links = []

        table = self.source.find('table', attrs={'class': 'table-dynamic'})
        rows = table.find_all('tr')

        for row in rows:
            columns = row.find_all('td')
            cols = [ele.text.strip() for ele in columns]
            tab = [ele for ele in cols if ele]
            if tab:
                daty.append(time.strptime((tab[1][0:10]), "%Y-%m-%d"))
                filenames.append(tab[2].split('.SWX')[0] + '.SWX')

            for col in columns:
                anchors = col.find_all('a')
                for element in anchors:
                    if (element.attrs['href'][:31]) == '../../user/komstatmed/ppzrapget':
                        links.append('https://szoi.nfz.poznan.pl/ap-mzwi' + element.attrs['href'][5:])

        return [list(x) for x in zip(filenames, daty, links)]
