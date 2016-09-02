import logging
import logging.config

def main():
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('applog')

    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
#logging.shutdown()

if __name__ == '__main__':
    main()
