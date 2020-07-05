from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from argparse import RawTextHelpFormatter
from django.conf import settings
import pathlib
import re
from datetime import datetime
import shutil


class Command(BaseCommand):
    help = """
        usage: ./manage.py secret_key [option]
        --------------------------------------
        example: ./manage.py secret_key generate
        example: ./manage.py secret_key get
        example: ./manage.py secret_key set
        example: ./manage.py secret_key set "4h0u&vk3l(s2t#@c(-%s5_fa_=1ww02s_f6+g-_^^^s+^y8)bp"

        options
        --------
        generate - generates a new secret key and prints it to the screen
        get - prints the current loaded settings secret_key value
        set - sets the .secret_key file to value passed or generated value and prints it to the screen
    """

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument('option', nargs='+', type=str)

    @staticmethod
    def generate_secret():
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return get_random_string(50, chars)

    @staticmethod
    def get_secret():
        return settings.SECRET_KEY

    def set_secret(self, options):
        # if we were passed a key use it otherwise generate one
        if len(options) >= 2:
            secret_key = str(options[1])
        else:
            secret_key = self.generate_secret()
        local_path = pathlib.Path()
        # print(f'local path: {local_path}')
        settings_path = local_path / "docroot" / "settings.py"
        all_settings = settings_path.read_text()
        # find where we are replacing secret_key and replace the value
        qt_pattern = re.compile(r"\s*SECRET_KEY\s*=\s*'(\S*)'")
        new_string = self.replace_pattern_group(all_settings, qt_pattern, secret_key)
        dbqt_pattern = re.compile(r'\s*SECRET_KEY\s*=\s*"(\S*)"')
        new_string = self.replace_pattern_group(new_string, dbqt_pattern, secret_key)
        # print(f'new settings: {new_string}')
        # backup the old file before we mess with it
        datetime_ext = datetime.now().strftime("%Y%m%d-%H%M")
        new_file_name = settings_path.name + "." + datetime_ext
        shutil.copy(settings_path, settings_path.parent / new_file_name)
        settings_path.write_text(new_string)
        return secret_key

    def handle(self, *args, **options):
        if "generate" in options['option']:
            self.stdout.write(self.style.SUCCESS('%s' % self.generate_secret()))
        elif "get" in options['option']:
            self.stdout.write(self.style.SUCCESS('%s' % self.get_secret()))
        elif "set" in options['option']:
            self.stdout.write(self.style.WARNING('WARNING: You must restart the server to apply the new secret_key'))
            self.stdout.write(self.style.SUCCESS(self.set_secret(options['option'])))
        else:
            self.stdout.write(self.style.SUCCESS(self.help))

    @staticmethod
    def replace_pattern_group(string, pattern, value):
        last_match = 0
        new_string = ""
        for match in re.finditer(pattern, string):
            # print(match.group(1))
            group_start = match.span(1)[0]
            group_end = match.span(1)[1]
            new_string += string[last_match:group_start]
            new_string += value
            last_match = group_end
        new_string += string[last_match:]
        return new_string
