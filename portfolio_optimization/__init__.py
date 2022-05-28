import logging


class CustomFormatter(logging.Formatter):
    """Logging colored formatter"""

    blue = '\x1b[38;5;39m'
    green = '\x1b[32;1m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.blue + self.fmt + self.reset,
            logging.INFO: self.green + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger('portfolio_optimization')
if len(logger.handlers) == 0:
    logger.setLevel(logging.INFO)
    console_log = logging.StreamHandler()
    console_log.setLevel(logging.INFO)
    formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_log.setFormatter(formatter)
    logger.addHandler(console_log)
