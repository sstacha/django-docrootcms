"""
Basic logging utilities

"""
from django.conf import settings
from .settings import ColorLogger as SettingsColorLogger
from .settings import TermColor as SettingsTermColor


class TermColor(SettingsTermColor):
    pass


class ColorLogger(SettingsColorLogger):
    """
    Overrides the utils.settings.ColorLogger and implements settings lookup for different modules
    NOTE: this allows ColorLogger to be used by settings.py without circular reference but modules to use
        this implementation and have the log level defined in the settings file to be overridden
    """
    def get_initial_log_level(self, name: str, default: str = 'INFO') -> str:
        """
        sets the initial value; for the logging implementation this will be overridden
            to include a settings value check for the specified logger name
        @param name: Name to lookup in settings like LOGGING['<name>']['level']
        @param default: default the developer would like or INFO
        @return: one of ColorLogger.LOG_LEVELS[]
        """
        _logging = getattr(settings, "LOGGING")
        if 'loggers' in _logging:
            if name in _logging['loggers'] and 'level' in _logging['loggers'][name]:
                return _logging['loggers'][name]['level']
            # todo: try this moving up the chain ex: views.api.ppms_api -> api.ppms_api -> ppms_api
        return default
