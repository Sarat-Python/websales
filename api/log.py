'''
PIT_STOP_RECHARGE_BEGIN_TAG
*
* Pit Stop Recharge CONFIDENTIAL
*
* COPYRIGHT Pit Stop Recharge P/L 2011, 2014
* All Rights Reserved
*
* The source code for this program is not published or otherwise 
* divested of its trade secrets, irrespective of what has been 
* deposited with the Australian Copyright Office. 
*
PIT_STOP_RECHARGE_END_TAG
'''
'''
Begin Change Log **************************************************************
                                                                      
  Itr    Def/Req  Userid      Date          Description
  -----  -------- --------    --------    --------------------------------------
  0.9    339      NaveeN      08/04/2014  Base log file for card activation
 End Change Log ***************************************************************
'''

import logging
import logging.handlers
from sys import stdout


class Logger(object):

    @classmethod
    def initialize(cls, log_file, debug_mode, log_level):
        """
        Initialize the logger
        """
        logging.basicConfig(level=logging.INFO,
                            format='[%(asctime)s] [%(levelname)s] [%(name)s %(lineno)s] %(message)s',
                            filename=log_file,
                            filemode='a')

        logger = logging.getLogger('')
        if debug_mode:
            handler = logging.StreamHandler(stdout)
            logger.addHandler(handler)
        logging.getLogger('').setLevel(_getLogLevel(log_level))

    @classmethod
    def get_logger(cls, name='pitstop'):
        """
        Get the logger for the given name with given configuration
        Args:
            name: Name of the logger
        Returns:
            Logger for the given name
        """

        return logging.getLogger(name)


def _getLogLevel(eventLogLevel='LOG_DEBUG'):
    """
    This is the mapper for log level to Python Log level
    Args:
        event_log_level: The log levels defined for the NADE engine
    Returns:
        Python log level
    """
    eventLogLevel = str(eventLogLevel).strip()
    logLevel = logging.FATAL

    if eventLogLevel == 'LOG_DEBUG':
        logLevel = logging.DEBUG
    elif eventLogLevel == 'LOG_INFO':
        logLevel = logging.INFO
    elif eventLogLevel == 'LOG_NOTICE':
        logLevel = logging.INFO
    elif eventLogLevel == 'LOG_WARN':
        logLevel = logging.WARNING
    elif eventLogLevel == 'LOG_ERR':
        logLevel = logging.ERROR
    elif eventLogLevel == 'LOG_CRIT':
        logLevel = logging.CRITICAL

    return logLevel


if __name__ == "__main__":
    Logger.initialize('test.log', True, "LOG_ERR")
    Logger.get_logger(__name__).error('Hello ERR')
