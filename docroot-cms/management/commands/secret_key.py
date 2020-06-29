from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from argparse import RawTextHelpFormatter
from django.conf import settings


class Command(BaseCommand):
    # todo: make the set secret_key replace the secret key in the settings file and add the help back
    help = """
        usage: ./manage.py secret_key [option]
        --------------------------------------
        example: ./manage.py secret_key generate
        example: ./manage.py secret_key get
    
        options
        --------
        generate - generates a new secret key and prints it to the screen
        get - prints the current .secret_key value
    """
    # help += "example: ./manage.py secret_key set [key]\n"
    # help += "example: ./manage.py secret_key set \"4h0u&vk3l(s2t#@c(-%s5_fa_=1ww02s_f6+g-_^^^s+^y8)bp\"\n"
    # help += "set - sets the .secret_key file value and prints it to the screen\n"

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument('option', nargs='+', type=str)

    def generate_secret(self):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return get_random_string(50, chars)
        # self.stdout.write(self.style.SUCCESS('SECRET KEY: "%s"' % get_random_string(50, chars)))

    def get_secret(self):
        return settings.SECRET_KEY
        # with open('.secret_key') as file:
        #     return file.read()

    # def set_secret(self, options):
    #     # if we were passed a key use it otherwise generate one
    #     if len(options) >= 2:
    #         secret_key = str(options[1])
    #     else:
    #         secret_key = self.generate_secret()
    #     with open('.secret_key', 'w+') as file:
    #         # write secret_key to the file
    #         file.write(secret_key)
    #     return self.get_secret()

    def handle(self, *args, **options):
        if "generate" in options['option']:
            self.stdout.write(self.style.SUCCESS('%s' % self.generate_secret()))
        elif "get" in options['option']:
            self.stdout.write(self.style.SUCCESS('%s' % self.get_secret()))
        # elif "set" in options['option']:
        #     # print warning
        #     self.stdout.write(self.style.WARNING('WARNING: You must restart the server to apply the new secret_key'))
        #     self.stdout.write(self.style.SUCCESS('%s' % self.set_secret(options['option'])))
        else:
            self.stdout.write(self.style.SUCCESS(self.help))