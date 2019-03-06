import copy
import csv
import logging as log
import os
import time


class Writer:
    def __init__(self, directory, filename):
        self.contents = None
        self.directory = directory
        self.filename = filename

    def writeToCsv(self):
        if not os.path.exists(self.directory):
            try:
                os.mkdir(self.directory)
                log.debug('Directory did not exist, so it was created: {0}'.format(self.directory))
            except:
                log.exception('Directory did not exist, but it couldnt be created: {0}'.format(self.directory))
                return False
        try:
            log.debug('Trying to open: {0}\\{1}" for write'.format(self.directory, self.filename))
            file = open("{0}\\{1}".format(self.directory, self.filename), mode='w', encoding='windows-1250')
            csv_writer = csv.writer(file, delimiter=';', lineterminator='\n')

        except FileNotFoundError:
            log.error("File not found: {0}".format("{0}\\{1}".format(self.directory, self.filename)))
            return False

        for row in self.contents:
            row[1] = time.strftime("%Y-%m-%d", row[1])
            csv_writer.writerow([row[0], row[1]])

        file.close()
        log.debug('File closed successfully')

    def loadContent(self, content):
        self.contents = copy.deepcopy(content)

    def deleteSelf(self):
        try:
            os.remove("{0}\\{1}".format(self.directory, self.filename))
            log.info('{0} file deleted'.format(self.filename))
        except FileNotFoundError:
            log.error('File not found - can\'t be deleted')
        except PermissionError:
            log.error('PermissionError while deleting file')
        except:
            msg = 'Unhandled exception while deleting file'
            log.error(msg)
            print(msg)
