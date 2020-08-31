# django-docrootcms
Docroot CMS is a django application for developers who build, manage and maintain websites.  This app takes the simplicity of working with a PHP docroot, the fun of working with Python and fully leverages the power of Django for adding website application functionality.

[ubercode.io: docroot cms](https://www.ubercode/io/products/docrootcms)
> Because the code matters

## Dependencies
* Python >= 3.6
* django >= 2
* django-markdownx
* django-docrootcms-tagulous

NOTE: django-docrootcms-tagulous will only be required until the official django-tagulous supports django 3

## Install Instructions
### New Install
NOTE: this is only slightly modified from Django docs for easier website maintenance
[Djano: Writing your first Django application](https://docs.djangoproject.com/en/3.0/intro/tutorial01/)

cd to your start folder location (Ex: ~/websites/)
```shell script
mkdir example.com
cd example.com
```
***be sure to activate your virtual environment if necessary 
(Ex: pyenv local examplecom) or (Ex: source env/bin/activate)***
```shell script
pip install --upgrade pip
pip install django
django-admin startproject docroot .
pip install django-markdownx
pip install django-docrootcms-tagulous
pip install django-docrootcms
```
in docroot/settings.py add docrootcms to the beginning of the installed apps block
```shell script
python manage.py docrootcms install
python manage.py docrootcms update
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py runserver 0.0.0.0:8000
```

To test: open a browser to http://localhost:8000/test/

Tutorials & Guides: [ubercode.io: docroot cms tutorials](https://www.ubercode/io/products/docrootcms/tutorials)


### Existing Install
NOTE: manage.py commands modify the docroot settings.py and urls.py files.  If this is not the projects settings.py and urls.py you will have to manually merge these changes yourself every time you upgrade the django-docroot-cms app.  This is not recommended.

***be sure to activate your virtual environment if needed***

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
NOTE: THIS IS THE CONCEPT I THINK YOU SHOULD TAKE; UNTESTED SO FAR!

### Docker Install / New Code (Bound directory)

Install Docker [docs.docker.com: Get Docker](https://docs.docker.com/get-docker/) 

#### First time: To get a blank website to check into GIT repo

I recommend creating a websites directory inside your home directory (Ex: ~/websites/)

```shell script
cd ~/websites
mkdir example.com_install
cd example.com_install
```

NOTE: if you are on linux you will need to sudo chown -R <yourusername>:<yourgroupname> website/ or set the ownership variable to your user:group ids like the example below
    you can find your ids by executing cat /etc/passwd and looking for the line with your username; the first number after the x is the userid the second is the default groupid
    it will look something like this -> sstacha:x:1001:1001:Stephen Stacha,,,:/home/sstacha:/bin/bash.  If you want a different group use cat /etc/group and pick the group id you want.

```shell script
docker run --rm --name django-docrootcms -p 8000:8000 -v $(pwd):/usr/src/install -e DOCROOTCMS_OWNERSHIP=1001:128 sstacha/django-docrootcms "install.sh"
```
NOTE: if you are windows/mac you can omit the -e DOCROOTCMS_OWNERSHIP variable; it should not be needed
```shell scriptyou can find your groupid
docker run --rm --name django-docrootcms -p 8000:8000 -v $(pwd):/usr/src/install sstacha/django-docrootcms "install.sh"
```

Create a new repo on github like example_com (include python gitignore, others optional) and clone into the current folder.
Copy the files from install folder into the repo clone folder (not the install directory; just the files)
Push them up to your site repo
```shell script
cd ~/websites/
mkdir example_com # because pycharm only allows picking a project directory with numbers letters and underscores
git clone <your website project url> .
cp -a ../example.com_install/. .
git add .
git commit -m "initial blank website"
git push
```
Now we will remove the install folder and we should be good to go
```shell script
rm -rf ../example.com_install/
```
rerun docker command binding our website directory; you can run git commands locally or edit files from the shared directory

#### From now on: To run the container with our bound code directory managed by version control
```shell script
docker run --rm --name django-docrootcms -p 8000:8000 -v $(pwd):/usr/src/app sstacha/django-docrootcms
```

### Docker Install / Existing Code (Bound Directory)
```shell script
cd ~/websites/
mkdir example_com
git clone <your website project url> .
```

run docker command binding our website directory; you can run git commands locally or edit files from the shared directory
#### From now on: To run the container with our bound code directory managed by version control
```shell script
docker run --rm --name django-docrootcms -p 8000:8000 -v $(pwd):/usr/src/app sstacha/django-docrootcms
```


### Docker server deployment
For server deployments you will want docker to handle making sure your application stays up and running.  You will probably 
want to use docker-compose.  Paste the following in your site directory example.com as docker-compose.yml:

```yaml
version: '3.4'
services:
  example_com:
    # (to fix for development); do not use in production
    # container_name: example_com
    image: sstacha/django-docrootcms
    # restart: unless-stopped
    # command: /bin/bash
    env_file: 
    #  - local.env
    ports:
      - 8000:8000
    volumes:
      # - ./data:/usr/src/app/data/
      - type: bind
        source: $PWD
        target: /usr/src/app

```

Now you should be able to use docker-compose up and docker-compose down to start and stop the service

To test: open a browser to http://localhost:8000/test/

Tutorials & Guides: [ubercode.io: docroot cms tutorials](https://www.ubercode/io/products/docrootcms/tutorials)

