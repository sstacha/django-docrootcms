"""
The biggest problem with settings is you have to be careful of dependencies so there are no
    circular references.  These functions should be safe for settings to use.  Make sure
    any functions here can be imported without them using settings.
"""
import os
from typing import Tuple

try:
    import textwrap

    textwrap.indent
except AttributeError:  # undefined function (wasn't added until Python 3.3)
    def indent_string(text, amount, ch=' '):
        padding = amount * ch
        return ''.join(padding + line for line in text.splitlines(True))
else:
    def indent_string(text, amount, ch=' '):
        return textwrap.indent(text, amount * ch)

TRUE_VALUES = ["1", 1, "y", "Y", True, "t", "T", "TRUE", "True", "true", "YES", "Yes", "yes", "ON", "On", "on"]
FALSE_VALUES = ["0", 0, "n", "N", False, "f", "F", "False", "false", "No", "no", None]


def to_bool(value):
    """
    Convert <value> to boolean.  Mainly handles returning false values passed as parameters which
    would otherwise return a truthy value.  Returns false if None or FALSE_VALUES, otherwise
    returns normal boolean truthy value conversion.
    :param value: expects int, bool, string or None
    :return: python True/False value
    """
    # note: need this line because strings and numbers are truthy and will return true
    if value in FALSE_VALUES:
        return False
    return bool(value)


def mask(value: str):
    _iqtr = len(value) // 4
    if _iqtr <= 0:
        _iqtr = 1
    _mask = value[:_iqtr]
    if len(value) > (_iqtr * 2):
        for i in range(len(value) - (_iqtr * 2)):
            _mask += '*'
    _mask += value[-_iqtr:]
    return _mask


class TermColor:
    """
    Class to display output color around text printed in a terminal window
    USAGE IN MSG (color_output=False)
    NOTE: if color_output=True then the entire msg will be output in color based on log_level
    ---
    EX: print(TermColor.FAIL + "REMOVING: " + TermColor.ENDC + os.path.join(dirpath, name))
    """

    def __init__(self):
        pass

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    F_Default = "\x1b[39m"
    F_Black = "\x1b[30m"
    F_Red = "\x1b[31m"
    F_Green = "\x1b[32m"
    F_Yellow = "\x1b[33m"
    F_Blue = "\x1b[34m"
    F_Magenta = "\x1b[35m"
    F_Cyan = "\x1b[36m"
    F_LightGray = "\x1b[37m"
    F_DarkGray = "\x1b[90m"
    F_LightRed = "\x1b[91m"
    F_LightGreen = "\x1b[92m"
    F_LightYellow = "\x1b[93m"
    F_LightBlue = "\x1b[94m"
    F_LightMagenta = "\x1b[95m"
    F_LightCyan = "\x1b[96m"


class ColorLogger:
    """
    Class to encapsulate methods and data for logging at a specific log level with terminal colors
    TODO: figure out if we can somehow integrate this into django logging
    """
    # static constant values for determining log level by index low to high
    #   NOTE: requires all indexes to increment obviously in order to have different logging levels
    LOG_LEVELS = ['DEBUG', 'INFO', 'WARN', 'FATAL', 'ALWAYS']

    # I would really like to turn this into a Literal (python 3.8) but I don't want to force that just yet
    #   however, I am going to try and change the accepted params to be string to fit more with django.logging
    #   even if I can't use the Literal helper for tools pre runtime right now.  Consider TermColor param Literal too.
    # example literal code:
    # start with the literal
    # Argument = typing.Literal['DEBUG', 'INFO' ...]
    # build the list of accepted values from literal so it doesn't affect the lookups
    # VALID_ARGUMENTS: typing.Tuple[Argument, ...] = typing.get_args(Argument)
    # or
    # VALID_ARGUMENTS: typing.List[Argument] = list(typing.get_args(Argument))
    # NOTE: maybe do a generator to create the dict of values or use index if list stays in order (should)
    def __init__(self, name: str, level: str or int = None):
        self.name = name
        self._level = level
        # if no value passed then lookup from settings or default to warn for production
        if self._level is None:
            self._level = self.get_initial_log_level(name, 'WARN')
        self.level = self._level
        self.indention = 0
        self.indent_spaces = 4
        self.color_output = True
        self.repeat_msg = '.'
        self.repeat_max = 100
        self.repeat_cnt = 0
        self.repeat_indention = 0

    # logging helper functions
    def get_initial_log_level(self, name: str, default: str = 'INFO') -> str:
        """
        sets the initial value; for the default settings implementation this will simply be INFO
            or a valid value the developer gave us; for logging implementation this will be overridden
            to include a settings value check for the specified logger name
        @param name: Name to lookup in settings like LOGGING['<name>']['level']
        @param default: default the developer would like or INFO
        @return: one of ColorLogger.LOG_LEVELS[]
        """
        # in our base implementation that settings can use this simply defaults to INFO or passes
        #   whatever value was passed in
        if default not in self.LOG_LEVELS:
            default = 'INFO'
        return default

    @staticmethod
    def to_valid_level(level: str or int) -> str:
        """
        validate and return string version of LOG_LEVEL to use from LOG_LEVELS
        @param level: passed level value (int or string)
        @return: string log level value from LOG_LEVELS
        """
        # for backwards compatability if we pass an int (index) convert it
        if isinstance(level, int):
            if 0 <= level < len(ColorLogger.LOG_LEVELS):
                level = ColorLogger.LOG_LEVELS[level]
            else:
                raise ValueError(
                    f"ColorLogger.level [{str(level)}] must be one of {str(ColorLogger.LOG_LEVELS)} or the index")
        # last check to make sure our string is in the list of accepted values
        if level not in ColorLogger.LOG_LEVELS:
            raise ValueError(
                f"ColorLogger.level [{str(level)}] must be one of {str(ColorLogger.LOG_LEVELS)} or the index")
        return level

    @property
    def level(self) -> str:
        return self._level

    @level.setter
    def level(self, value: str or int) -> None:
        self._level = self.to_valid_level(value)

    def indent(self) -> int:
        self.indention += 1
        return self.indention

    def unindent(self) -> int:
        self.indention -= 1
        if self.indention < 0:
            self.indention = 0
        return self.indention

    def debug(self, msg: str, color: str = TermColor.F_DarkGray, indent: int = None, end: str = None) -> None:
        self.log(msg, 'DEBUG', color, indent, end)

    def info(self, msg: str, color: str = TermColor.OKBLUE, indent: int = None, end: str = None) -> None:
        self.log(msg, 'INFO', color, indent, end)

    def success(self, msg: str, color: str = TermColor.F_Green, indent: int = None, end: str = None) -> None:
        self.log(msg, 'INFO', color, indent, end)

    def warn(self, msg: str, color: str = TermColor.WARNING, indent: int = None, end: str = None) -> None:
        self.log(msg, 'WARN', color, indent, end)

    def fatal(self, msg: str, color: str = TermColor.FAIL, indent: int = None, end: str = None) -> None:
        self.log(msg, 'FATAL', color, indent, end)

    def always(self, msg: str, color: str = TermColor.F_Default, indent: int = None, end: str = None) -> None:
        self.log(msg, 'ALWAYS', color, indent, end)

    def log(self, msg: str, log_level: str or int, color: str = None, indent: int = None, end: str = None) -> None:
        """
        If we have a color and want color output we print it with color otherwise we just print it to screen
        :param msg: message to display
        :param log_level: the level for this message
        :param color: the color to use (SEE TermColor constants)
        :param indent: override indention otherwise uses indention property on logger
        :param end: pass end to print if exists to keep on same line for example
        :return: None; prints to screen with the proper color
        """
        log_level = self.to_valid_level(log_level)
        if self.LOG_LEVELS.index(log_level) >= self.LOG_LEVELS.index(self.level):
            c_msg = str(msg)
            if self.color_output and color:
                c_msg = color + c_msg + TermColor.ENDC
            if msg == self.repeat_msg:
                # the first time we start repeating track the indent level
                if not self.repeat_cnt:
                    if indent is not None:
                        self.repeat_indention = indent
                    else:
                        self.repeat_indention = self.indention
                    c_msg = indent_string(c_msg, self.repeat_indention * self.indent_spaces)
                self.repeat_cnt += 1
                if self.repeat_cnt > self.repeat_max:
                    # include the newline and index
                    c_msg = f'\n{indent_string(c_msg, self.repeat_indention * self.indent_spaces)}'
                    # reset out skipped message to our current length
                    self.repeat_cnt = 1
            else:
                if self.repeat_cnt:
                    c_msg = '\n' + c_msg
                    self.repeat_cnt = 0
                if indent is not None:
                    c_msg = indent_string(c_msg, indent * self.indent_spaces)
                elif self.indention is not None:
                    c_msg = indent_string(c_msg, self.indention * self.indent_spaces)

            if end is not None:
                print(c_msg, end=end)
            else:
                print(c_msg)


_utils_settings_logger = ColorLogger("utils.settings")


def override_database_environment_variables(db_dict: dict, var_name: str = "DATABASES", logger: ColorLogger = None,
                                            log_level: str = "INFO",
                                            secret_properties: Tuple[str] = ("PW", "PWD", "PASSWORD")) -> dict:
    """
    Overrides all database connection variables according to a set of rules.
    Expects: variable_name__connection_name__property=value
    For each match found, replaces the variable value in the settings file
    NOTE: secret_properties will be masked so output can't see sensitive data but know it was changed
    Ex:
    DATABASES = {
        'test': {
            'DRIVER': 'FreeTDS',
            # 'DRIVER': 'ODBC Driver 17 for SQL Server',
            'SERVER': 'localhost',
            'PORT': 1433,
            'DATABASE': 'test_db',
            'UID': 'test_user',
            'PWD': 'test_pwd',
            'TDS_VERSION': 7.2
        },
    }
    Env:
    DATABASES__test__SERVER=docker.host.internal
    DATABASES__test__PWD=another_pwd

    Would result in:
    DATABASES = {
        'test': {
            'DRIVER': 'FreeTDS',
            # 'DRIVER': 'ODBC Driver 17 for SQL Server',
            'SERVER': 'docker.host.internal',
            'PORT': 1433,
            'DATABASE': 'test_db',
            'UID': 'test_user',
            'PWD': 'another_pwd',
            'TDS_VERSION': 7.2
        },
    }
    @param db_dict: The database dictionary to replace values in if found
    @param var_name: Since we don't know the settings variable name with the dict passed in
        and the environment variable uses that to only apply values we want to the right database dict
        we need to say what the variable name is.  Defaults to Django DATABASES
    @param logger: optional logger to use instead of creating a new one
    @param log_level: Set log level of output during run
    @param secret_properties: List of property names to obscure in printing
    @return dict with replaced values
    """
    return override_database_variables(db_dict, var_name, logger, log_level, os.environ.items(), secret_properties)


def override_database_variables(db_dict: dict, var_name: str = "DATABASES", logger: ColorLogger = None,
                                log_level: str = None, items=os.environ.items(),
                                secret_properties: Tuple[str] = ("PW", "PWD", "PASSWORD")) -> dict:
    """
    Overrides all database connection variables according to a set of rules.
    Expects: variable_name__connection_name__property=value
    For each match found, replaces the variable value in the settings file
    Ex:
    DATABASES = {
        'test': {
            'DRIVER': 'FreeTDS',
            # 'DRIVER': 'ODBC Driver 17 for SQL Server',
            'SERVER': 'localhost',
            'PORT': 1433,
            'DATABASE': 'test_db',
            'UID': 'test_user',
            'PWD': 'test_pwd',
            'TDS_VERSION': 7.2
        },
    }
    items:
    DATABASES__test__SERVER=docker.host.internal
    DATABASES__test__PWD=another_pwd

    Would result in:
    DATABASES = {
        'test': {
            'DRIVER': 'FreeTDS',
            # 'DRIVER': 'ODBC Driver 17 for SQL Server',
            'SERVER': 'docker.host.internal',
            'PORT': 1433,
            'DATABASE': 'test_db',
            'UID': 'test_user',
            'PWD': 'another_pwd',
            'TDS_VERSION': 7.2
        },
    }

    items_test = {
        'DATABASES__default__ENGINE': 'django.db.backends.mysql',
        'DATABASES__default__HOST': 'mysql8dmzdev.spe.org',
        'DATABASES__default__NAME': 'petrobowl',
        'DATABASES__default__USER': 'petrobowlapp',
        'DATABASES__default__PASSWORD': '7yMfOEP6S8tVgJF9N8Hj',
        'DATABASES__default__PORT': 3306,
        }

    @param db_dict: The database dictionary to replace values in if found
    @param var_name: Since we don't know the settings variable name with the dict passed in
        and the environment variable uses that to only apply values we want to the right database dict
        we need to say what the variable name is.  Defaults to Django DATABASES
    @param items: The items to iterate over and replace (requires key, value pair)
    @param logger: optional logger to use instead of creating a new one
    @param log_level: Set log level of output during run
    @param secret_properties: List of property names to obscure in printing
    @return dict with replaced values
    """
    _logger = logger or _utils_settings_logger
    _previous_level = _logger.level
    try:
        if log_level:
            _logger.level = log_level
        uc_secret_properties = []
        for property in secret_properties:
            if property:
                uc_secret_properties.append(property.strip().upper())
        for k, v in items:
            # _logger.debug(f'key: {k} value: {v}')
            db_parts = k.split('__')
            # must at least have a DATABASES['key']['property'] to override the value
            if len(db_parts) == 3:
                # env must start with the varname we said we want to replace and have values for all parts
                if db_parts[0] and var_name == db_parts[0] and db_parts[1] and db_parts[2]:
                    _logger.debug(f'environment variable: {k}')
                    _log_from_value = 'None'
                    _log_to_value = str(v)
                    # we may be setting up a completely new database from scratch so create if it doesn't exist
                    if not db_dict[db_parts[1]]:
                        _logger.debug(f'database {db_parts[0]}[{db_parts[1]}] was not found; creating...')
                        db_dict[db_parts[1]] = {}
                    # we now have db dict; we may not have a property already defined; if not we want to add it
                    if not db_dict[db_parts[1]].get(db_parts[2]):
                        _logger.debug(
                            f'property {db_parts[0]}[{db_parts[1]}][{db_parts[2]}] was not found; creating...')
                        db_dict[db_parts[1]][db_parts[2]] = v
                    else:
                        _logger.debug(
                            f'property {db_parts[0]}[{db_parts[1]}][{db_parts[2]}] was found; overriding...')
                        _log_from_value = db_dict[db_parts[1]][db_parts[2]]
                        # if we have an existing value and its secret be sure to mask it for logging before we override
                        if str(_log_from_value) != 'None' and db_parts[2].strip().upper() in uc_secret_properties:
                            _log_from_value = mask(str(_log_from_value))
                        db_dict[db_parts[1]][db_parts[2]] = v
                    # we may not mask from value because of 'None' for create but always mask to value if secret
                    if db_parts[2].strip().upper() in uc_secret_properties:
                        _log_to_value = mask(_log_to_value)
                    _logger.info(
                        f'set {db_parts[0]}[{db_parts[1]}][{db_parts[2]}] from ['
                        f'{_log_from_value}] to [{_log_to_value}]')
                else:
                    if db_parts[0] and var_name == db_parts[0]:
                        _logger.warn(
                            f"{db_parts[0]}[{db_parts[1]}][{db_parts[2]}] has a database or property naming issue!")
    finally:
        # reset our log level in case it was overridden when we are done
        if _logger.level != _previous_level:
            _logger.level = _previous_level
    return db_dict


def override_environment_variable(var_name, var_value, env_name: str = None, data_type: str = "str",
                                  log_level: str = "INFO"):
    """
    returns current value or overridden value based on an environment variable name.  trys to convert to expected type
    Ex:
    DEBUG = True
    Env:
    DEBUG_OVERRIDE=False

    DEBUG = override_envionment_variable(DEBUG, "DEBUG_OVERRIDE", "bool")
    Would result in:
    DEBUG = False (of type boolean not string)

    @param var_name: The current setting variable name (for logging)
    @param var_value: The current setting variable value
    @param env_name: environment variable name to look for and replace with if found (defaults to var_name if not passed)
    @param data_type: ["str", "bool", "int"] (default to str)
    @param: log_level: Set log level of output during run
    @return: original variable value or env value converted to requested type
    """
    if not var_name:
        raise ValueError("var_name must be passed!")
    _utils_settings_logger.level = log_level
    if not env_name:
        env_name = var_name
    _env_value = os.environ.get(env_name)
    if _env_value is not None:
        # attempt to convert to datatype if not str
        if data_type == 'bool':
            _env_value = to_bool(_env_value)
        if data_type == 'int':
            _env_value = int(_env_value)
        _utils_settings_logger.info(f'overriding {var_name}: [{str(var_value)}] to [{str(_env_value)}]')
        return _env_value
    return var_value
