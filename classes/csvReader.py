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

        counter = 0
        if file != '':
            if ';' in file.read():
                file.seek(0)
                for row in csv_reader:
                    if len(row[0]) > 0:
                        try:
                            row[1] = time.strptime(row[1], "%Y-%m-%d")
                            self.contents.append(row)
                            counter += 1
                        except ValueError:
                            log.error('Dates in csv file could not be parsed to time data')
                            return False
                    else:
                        log.error('First column of csv file must contain string with report name')
                        return False

                file.close()
                log.debug('File closed successfully. {0} rows read.'.format(counter))
                return self.contents

            else:
                log.error('{0} is not properly delimited. ";" character must be used.'.format(self.directory))
                return False

        else:
            log.error("File {0} is empty".format(self.directory))
            file.close()
            return False
