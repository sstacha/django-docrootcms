# docrootCMS docker file for building deployment environment
#
FROM python:3.8
MAINTAINER Stephen Stacha (sstacha@gmail.com)

# add our database client libraries so we can plug them in later with docker-compose
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client default-libmysqlclient-dev

WORKDIR /usr/src/app
COPY requirements.txt ./
COPY entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN ln -s /usr/local/bin/docker-entrypoint.sh / \
    && pip install -r requirements.txt

# run the same thing as a new install
RUN django-admin startproject docroot .
COPY docrootcms ./docrootcms
# todo: change above to env so it can be managed by pip instead of overriden?
# instead of adding manually, we need to append a line to add the docrootcms to the installed apps
RUN echo 'INSTALLED_APPS.append("docrootcms")' >> docroot/settings.py \
    && echo '' >> docroot/settings.py \
    && python manage.py docrootcms install \
    && python manage.py docrootcms update

EXPOSE 8000

# entrypoint will setup our dns for linux, copy files from git if DOCROOTCMS_GIT_URL is passed, makemigrations,
#   migrate, and collect static
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
## Uncomment to run a bash shell
# CMD ["/bin/bash"]

# BUILD
# docker build -t django-docrootcms .
# RUN
# docker run --rm -it --name django-docrootcms -p 8000:8000 django-docrootcms
# w/dir mount
# docker run -it --env-file=.env --name django-docrootcms -p 8000:8000 -v $(pwd)/data:/usr/src/app/data django-docrootcms
# w/container named mount
# docker run -it --env-file=.env --name django-docrootcms -p 8000:8000 -v django-docrootcms-data:/usr/src/app/data django-docrootcms
# TO PUSH TO REPO
# docker tag django-docrootcms sasonline/django-docrootcms
# docker tag django-docrootcms sasonline/django-docrootcms:p3.8.3d3.0.7b2
# docker login
# docker push sasonline/django-docrootcms
# docker push sasonline/django-docrootcms:p3.8.3d3.0.7b2

# ----- OLD STUFF ------
## add our environment vars
#ENV UWEB_ROOT /uweb
#ENV UWEB_WEBSITE $UWEB_ROOT/website
#ENV UWEB_INSTALL $UWEB_ROOT/install
#ENV UWEB_BIN $UWEB_ROOT/bin
#
## add our directories
#RUN mkdir -p $UWEB_ROOT && \
#mkdir -p $UWEB_BIN && \
#mkdir -p $UWEB_INSTALL && \
#mkdir -p $UWEB_WEBSITE && \
#mkdir -p $UWEB_WEBSITE/data
#
## copy the deploy script and init script to the bin directory for use in console
#COPY ./bin $UWEB_BIN
#
## ENV GIT_WEBSITE_URL "testing/some/url"
#
#RUN git clone https://github.com/sstacha/uweb-install.git $UWEB_INSTALL && \
#mkdir -p $UWEB_INSTALL/website
#
#RUN echo "installing cms dependencies" && \
#pip install --upgrade pip && \
#pip install --no-cache-dir -r $UWEB_INSTALL/requirements.txt
#
#WORKDIR $UWEB_WEBSITE
#
#RUN echo "installing cms..." && \
#django-admin startproject docroot . && \
#echo 'STATIC_ROOT = os.path.join(BASE_DIR, "static/")' >> docroot/settings.py && \
#echo '' >> docroot/settings.py && \
#cat $UWEB_INSTALL/docroot_files/cms_settings.py >> docroot/settings.py && \
#cat $UWEB_INSTALL/docroot_files/cms_urls.py >> docroot/urls.py && \
#mkdir -p docroot/files && \
#cp -Rf $UWEB_INSTALL/docroot_files/files/* docroot/files/ && \
#mkdir -p uweb && \
#cp -Rf $UWEB_INSTALL/cms_files/* uweb/ && \
#cp $UWEB_INSTALL/.gitignore .gitignore  && \
#cp $UWEB_INSTALL/requirements.txt . && \
#python $UWEB_WEBSITE/manage.py migrate && \
#echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin@example.com', 'admin', 'admin')" | python $UWEB_WEBSITE/manage.py shell && \
#mkdir -p images && \
#mkdir -p cache && \
#cp -Rf $UWEB_INSTALL/example_files/files/* docroot/files/ && \
#cp -pR * "/uweb/install/website/"
#
### Make port 8000 to the world outside this container
#EXPOSE 8000
#
### Run gunicorn container launches (testing)
## CMD ["/home/uweb/.pyenv/versions/uweb/bin/gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "docroot.wsgi"]
#
### Uncomment to run a bash shell
#CMD ["/bin/bash"]

# HOW TO PUSH TO REPO
# docker build -t uweb .
# docker tag uweb sasonline/uweb
# docker login
# docker push sasonline/speweb
# docker push sasonline/speweb:<version#> ?use date for vnum?