import logging
import sys

class LogFormatter(logging.Formatter):

  grey = "\x1b[38;20m"
  yellow = "\x1b[93m"
  red = "\x1b[31;20m"
  bold_red = "\x1b[30;101;1m"
  purple = "\x1b[38;5;53;1m"
  light_blue = "\x1b[38;5;27m"
  reset = "\x1b[0m"
  
  format_prefix = '[%(asctime)s] - '
  format_string = '[%(asctime)s] - %(levelname)s - (%(filename)s:%(lineno)d) : %(name)s - %(message)s'

  formats = {
    logging.DEBUG:    light_blue + '[%(asctime)s]' + reset + ' - %(levelname)s - %(processName)s - %(threadName)s - (%(filename)s:%(lineno)d) : ' + reset + purple + '%(name)s' + reset + grey + ' - %(message)s' + reset,
    logging.INFO:     light_blue + '[%(asctime)s]' + reset + ' - %(levelname)s - %(processName)s - %(threadName)s - (%(filename)s:%(lineno)d) : ' + reset + purple + '%(name)s' + reset + grey + ' - %(message)s' + reset,
    logging.WARNING:  light_blue + '[%(asctime)s]' + reset + ' - ' + yellow + '%(levelname)s' + reset + ' - %(processName)s - %(threadName)s - (%(filename)s:%(lineno)d) : ' + reset + purple + '%(name)s' + reset + ' - ' + yellow + '%(message)s' + reset,
    logging.ERROR:    light_blue + '[%(asctime)s]' + reset + ' - ' + red + '%(levelname)s' + reset + ' - %(processName)s - %(threadName)s - (%(filename)s:%(lineno)d) : ' + reset + purple + '%(name)s' + reset + ' - ' + red + '%(message)s' + reset,
    logging.CRITICAL: light_blue + '[%(asctime)s]' + reset + ' - ' + bold_red + '%(levelname)s' + reset + ' - %(processName)s - %(threadName)s - (%(filename)s:%(lineno)d) : ' + reset + purple + '%(name)s' + reset + ' - ' + bold_red + '%(message)s' + reset
  }
  
  def format(self, record):
    formatter = logging.Formatter(self.formats[record.levelno], datefmt='%d.%b.%Y %H:%M:%S')
    return formatter.format(record)
  
def setup():
  root_logger = logging.getLogger()
  root_logger.setLevel(logging.INFO)
  root_handler = logging.StreamHandler(sys.stdout)
  root_handler.setLevel(logging.INFO)
  root_handler.setFormatter(LogFormatter())
  root_logger.addHandler(root_handler)