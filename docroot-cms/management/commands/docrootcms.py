from django.core.management.base import BaseCommand
from argparse import RawTextHelpFormatter
import os
import shutil
import pathlib
from datetime import datetime
from distutils.sysconfig import get_python_lib


class Command(BaseCommand):
    help = """
    usage: ./manage.py docroot-cms [option]
    --------------------------------------
    example: ./manage.py docroot-cms test update
    example: ./manage.py docroot-cms update

    options
    --------
    update - attempts to update user files with any configuration changes in settings and urls
    test - prints what files would be changed instead of changing them
    """
    testing = False

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument('option', nargs='+', type=str)

    def update(self):
        # look for the lines indicating this is our block and replace them with the current contents
        # otherwise throw an exception and print it as an error
        success_instructions = """
        Successfully updated cms.

        """
        # check that docroot app exists
        # NOTE: we will assume if there is a docroot dir then we already installed
        if not os.path.exists('docroot'):
            return 'docroot directory does not exist; can not update.  Did you mean to install it?'
        else:
            self.stdout.write(f'attempting to update docroot app and test files')
            # get the directory from docroot-cms/docroot
            module_path = self.get_module_path()
            # we have a module path so now lets try and copy the docroot_settings_append and docroot_urls_append
            # settings.py changes
            local_path = pathlib.Path()
            print(f'local path: {local_path}')
            settings_path = local_path / "docroot" / "settings.py"
            settings_append_path = module_path / "resources" / "docroot_settings_append.py"
            self.append_or_replace_content(settings_path, settings_append_path)
            # urls.py changes
            urls_path = local_path / "docroot" / "urls.py"
            urls_append_path = module_path / "resources" / "docroot_urls_append.py"
            self.append_or_replace_content(urls_path, urls_append_path)
            # create the resources folder if it doesn't exist and bring all the templates and append files over
            module_resources_path = module_path / 'resources'
            resources_path = local_path / 'docroot' / 'resources'
            if os.path.exists(resources_path):
                shutil.rmtree(resources_path)
                self.stdout.write(self.style.SUCCESS(f"Removed {resources_path}"))
            # copy the module resources to our resources (should contain various files like append index.dt and data.py
            shutil.copytree(module_resources_path, resources_path)
            self.stdout.write(self.style.SUCCESS(f"Copied {module_resources_path} to {resources_path}"))
            module_template_path = module_path / 'templates'
            shutil.copytree(module_template_path, resources_path / 'templates')
            self.stdout.write(self.style.SUCCESS(f"Copied {module_template_path} to {resources_path / 'templates'}"))
            module_test_path = module_path / 'docroot' / 'files' / 'test'
            shutil.copytree(module_test_path, resources_path, dirs_exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Copied {module_test_path} to {resources_path}"))

            return success_instructions

    def append_or_replace_content(self, old_path, new_path):
        if os.path.exists(new_path):
            # with open(new_path, 'r') as input_file:
            #     content_block = input_file.read()
            content_block = new_path.read_text()
            content_block = content_block.strip()
            # print(content_block)
            heading_substring = ""
            # look for a pattern match using the first line (heading)
            pos_end = content_block.find("\n")
            if pos_end != -1:
                heading_substring = content_block[0:pos_end]
            print(f'heading_substring: {heading_substring}')
            print("")
            print("")
            if heading_substring:
                print('we have substrings so searching new document.')
                # make sure we have a settings file to add it to (assumes docroot/settings.py)
                if os.path.exists(old_path):
                    current_content = old_path.read_text()
                    # with open(old_path, 'r') as output_file:
                    #     current_content = output_file.read()
                    start_pos = current_content.find(heading_substring)
                    end_pos = -1
                    new_content = None
                    if start_pos > -1:
                        end_pos = current_content.find(heading_substring, start_pos + len(heading_substring))
                        if end_pos > -1:
                            print('we found start and end positions so we are going to replace')
                            new_content = current_content[0:start_pos]
                            new_content += content_block
                            new_content += current_content[end_pos + len(heading_substring):]
                    # if we did not find a start or end pos so lets append
                    if start_pos <= -1 or end_pos <= -1:
                        print('we did not find start and or end so lets append')
                        new_content = current_content + "\n"
                        new_content += content_block + "\n"

                    # print("NEW CONTENT")
                    # print(new_content)

                    if new_content:
                        # backup the old file before we mess with it
                        datetime_ext = datetime.now().strftime("%Y%m%d-%H%M")
                        new_file_name = old_path.name + "." + datetime_ext
                        shutil.copy(old_path, old_path.parent / new_file_name)
                        # write the new_content to the current file
                        if self.testing:
                            test_file_name = old_path.stem + "_new.py"
                            test_file = old_path.parent / test_file_name
                            test_file.write_text(new_content)
                            self.stdout.write(self.style.SUCCESS(f'Successfully updated {new_path} to {test_file}'))
                        else:
                            old_path.write_text(new_content)
                            self.stdout.write(self.style.SUCCESS(f'Successfully updated {new_path} to {old_path}'))
                else:
                    self.stderr.write(self.style.ERROR(f'Settings file [{old_path}] was not found!'))
        else:
            self.stderr.write(self.style.ERROR(f'Settings append file [{new_path}] was not found!'))

    @staticmethod
    def get_module_path():
        # first try and get it from distutils (since pyenv symlinks to root version and site doesnt work for virtualenv)
        module_path = pathlib.Path(get_python_lib()) / 'docroot-cms'
        print(f'module path from DISTUTILS.SYSCONFIG: {module_path}')
        if not os.path.exists(module_path):
            module_path = pathlib.Path(os.__file__).parent / 'site-packages' / 'docroot-cms'
            print(f'module path from runtime: {module_path}')
        if not os.path.exists(module_path):
            # for debugging lets next try to find the app locally to copy from
            module_path = pathlib.Path('docroot-cms')
            print(f'module path from project: {module_path}')
        if not os.path.exists(module_path):
            raise ModuleNotFoundError(
                'Module docroot-cms was not installed.  Install using pip install django-docroot-cms and try again.')
        return module_path

    def install(self):
        success_instructions = """
        Successfully Installed cms.

        """
        # check that docroot app exists
        # NOTE: we will assume if there is a docroot dir then we already installed
        if not os.path.exists('docroot'):
            self.stderr.write(self.style.ERROR('docroot application directory not found!'))
            return 'Install docroot application according to instructions: https://github.com/sstacha/django-docroot-cms'
        else:
            self.stdout.write(f'installing docroot files...')
            # get the directory from docroot-cms/docroot/files
            module_path = self.get_module_path()
            module_docroot_files_path = module_path / 'docroot' / 'files'
            local_path = pathlib.Path()
            local_docroot_files_path = local_path / 'docroot' / 'files'
            print(f'local path: {local_path}')
            shutil.copytree(module_docroot_files_path, local_docroot_files_path)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully copied {module_docroot_files_path} to {local_docroot_files_path}'))
            # check that required directories exist
            if not os.path.exists(local_path / 'images'):
                os.makedirs(local_path / 'images')
                self.stdout.write(self.style.SUCCESS(f"Created {local_path / 'images'}"))
            if not os.path.exists(local_path / 'cache'):
                os.makedirs(local_path / 'cache')
                self.stdout.write(self.style.SUCCESS(f"Created {local_path / 'cache'}"))
            if not os.path.exists(local_path / 'data'):
                os.makedirs(local_path / 'data')
                self.stdout.write(self.style.SUCCESS(f"Created {local_path / 'data'}"))
            return success_instructions

    def develop(self):
        success_instructions = """
        Successfully Installed cms application for development.

        """
        # check that docroot-cms app doesn't already exist locally
        if os.path.exists('docroot-cms'):
            self.stderr.write(self.style.ERROR('docroot-cms application already exists locally for development!'))
            return 'Remove the existing directory to reload a newer version.'
        else:
            self.stdout.write(f'installing docroot-cms from virtual environment...')
            module_path = self.get_module_path()
            local_path = pathlib.Path() / 'docroot-cms'
            print(f'local path: {local_path}')
            shutil.copytree(module_path, local_path, dirs_exist_ok=True)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully copied {module_path} to {local_path}'))
            return success_instructions

    def handle(self, *args, **options):
        if "update" in options['option']:
            try:
                if "test" in options['option']:
                    self.testing = True
                self.stdout.write(self.style.WARNING(f'{self.update()}'))
            except ModuleNotFoundError as nfe:
                self.stderr.write(self.style.ERROR(f'Block not found.  This should not happen. {nfe}'))
        elif "install" in options['option']:
            try:
                if "test" in options['option']:
                    self.testing = True
                self.stdout.write(self.style.WARNING(f'{self.install()}'))
            except ModuleNotFoundError as nfe:
                self.stderr.write(self.style.ERROR(f'{nfe}'))
        elif "develop" in options['option']:
            self.stdout.write(self.style.WARNING(f'{self.develop()}'))
        else:
            self.stdout.write(self.style.SUCCESS(self.help))
