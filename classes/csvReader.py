import csv
import logging as log
import time


class Reader:
    def __init__(self, directory):
        self.directory = directory
        self.contents = []

    def readFromCsv(self):
        try:
            log.debug('Trying to open {0}'.format(self.directory))
            file = open(self.directory, mode='r', encoding='windows-1250')
            csv_reader = csv.reader(file, delimiter=';', lineterminator='\n')
            log.debug("File {0} opened successfully".format(self.directory))

        except FileNotFoundError:
            log.error("File: {0} not found".format(self.directory))
            return False

        if file is not None:
            for row in csv_reader:
                try:
                    row[1] = time.strptime(row[1], "%Y-%m-%d")
                    self.contents.append(row)
                except ValueError:
                    log.error('Dates in csv file could not be parsed to time data')
            file.close()
            log.debug('File closed successfully')
            return self.contents

        else:
            log.error("File empty")
            file.close()
            return False
