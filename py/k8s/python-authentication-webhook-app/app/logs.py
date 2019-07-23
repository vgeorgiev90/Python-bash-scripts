import logging


def setup_logger(logger_name, log_file, level=logging.INFO):
    log_setup = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    log_setup.setLevel(level)
    log_setup.addHandler(fileHandler)
    log_setup.addHandler(streamHandler)

def logger(msg, level, logfile):

    if logfile == 'one'   : log = logging.getLogger('log_one')
    if logfile == 'two'   : log = logging.getLogger('log_two')
    if level == 'info'    : log.info(msg)
    if level == 'warning' : log.warning(msg)
    if level == 'error'   : log.error(msg)



