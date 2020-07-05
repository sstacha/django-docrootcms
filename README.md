# django-docrootcms
Docroot CMS is a django application for developers who build, manage and maintain websites.  This app takes the simplicity of working with a PHP docroot, the fun of working with Python and fully leverages the power of Django for adding website application functionality.

[ubercode.io: docroot cms](https://www.ubercode/io/products/docrootcms)
> Because the code matters

## Dependencies
* Python >= 3.6.6
* django > 2

## Install Instructions
### New Install
NOTE: this is only slightly modifed from Django docs for easier website maintenance
[Djano: Writing your first Django application](https://docs.djangoproject.com/en/3.0/intro/tutorial01/)

cd to your start folder location (Ex: ~/websites/)
```shell script
mkdir example.com
cd example.com
```
be sure to activate your virtual directory if necessary (Ex: pyenv local examplecom)
```shell script
pip install --upgrade pip
pip install django
django-admin startproject docroot .
pip install django-docrootcms
```
in docroot/settings.py add docrootcms to the installed apps block
```shell script
python manage.py docrootcms install
python manage.py docrootcms update
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

To test: open a browser to http://localhost:8000/test/

Tutorials & Guides: [ubercode.io: docroot cms tutorials](https://www.ubercode/io/products/docrootcms/tutorials)


### Existing Install
NOTE: manage.py commands modify the docroot settings.py and urls.py files.  If this is not the projects settings.py and urls.py you will have to manually merge these changes yourself every time you upgrade the django-docroot-cms app.  This is not recommended.

be sure to activate your virtual directory if needed

cd to your existing project directory (contains manage.py)
```shell script
pip install --upgrade pip
pip install --upgrade django-docrootcms
python manage.py startapp docroot
```

* copy the original settings.py from a django-admin startproject into the docroot app
* copy the original urls.py from a django-admin startproject into the docroot app

remove these lines from your existing settings.py file and add this to the top
```python
from docroot.settings import *
```
remove the url lines from your existing urls.py file and add this to the top
```python
from docroot.urls import *
```
in docroot/settings.py add docrootcms to the installed apps block
```shell script
python manage.py docrootcms install
python manage.py docrootcms update
python manage.py makemigrations
python manage.py migrate
```
