"""
Basic logging utilities

"""


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
    # constants for picking the log_level and determining if we log to console based on it
    LOG_DEBUG = 0
    LOG_INFO = 1
    LOG_WARN = 2
    LOG_FATAL = 3
    LOG_ALWAYS = 4

    def __init__(self, name, level=LOG_FATAL):
        self.name = name
        self.level = level
        self.color_output = True

    # logging helper functions
    def debug(self, msg, color=TermColor.F_DarkGray) -> None:
        self.log(msg, self.LOG_DEBUG, color)

    def info(self, msg, color=TermColor.OKBLUE) -> None:
        self.log(msg, self.LOG_INFO, color)

    def success(self, msg, color=TermColor.F_Green) -> None:
        self.log(msg, self.LOG_INFO, color)

    def warn(self, msg, color=TermColor.WARNING) -> None:
        self.log(msg, self.LOG_WARN, color)

    def fatal(self, msg, color=TermColor.FAIL) -> None:
        self.log(msg, self.LOG_FATAL, color)

    def always(self, msg, color=TermColor.F_Default) -> None:
        self.log(msg, self.LOG_ALWAYS, color)

    def log(self, msg, log_level, color=None) -> None:
        """
        If we have a color and want color output we print it with color otherwise we just print it to screen

        :param msg: message to display
        :param log_level: the level for this message
        :param color: the color to use (SEE TermColor constants)
        :return: None; prints to screen with the proper color
        """
        if log_level >= self.level:
            c_msg = msg
            if self.color_output and color:
                c_msg = color + msg + TermColor.ENDC
            print(c_msg)
