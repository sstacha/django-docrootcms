import os
import codecs
import logging
import importlib.util
from django.conf import settings
from django.template import Template as DjangoTemplate
from django.template import Origin, RequestContext
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect

log = logging.getLogger("docrootcms.cms")


class Template:
    # note: uri = request.path_info.strip() or '/home/index.html'
    # note: language_code = request.LANGUAGE_CODE or 'en' or 'fr'
    def __init__(self, uri, language_code):
        # setup our basic attributes for the meta-data we will use for validation and template creation
        self.is_found = False
        self.docroot_dir = getattr(settings, "DOCROOT_ROOT", "")
        log.debug("docroot dir: " + str(self.docroot_dir))
        self.original_path = uri.strip()
        self.path = self.original_path
        log.debug(f"path: {self.path}")
        if self.path.startswith("/"):
            self.path = self.path[1:]
        self.file_name = os.path.join(self.docroot_dir, self.path)
        log.debug("file: " + str(self.file_name))
        self.module_name = self.path
        self.template_name = self.path
        # try and modify urls for logic on how to pull the correct template
        self.find_template()

        # get our settings needed for processing defaulting if they are not there
        ignore_lanaguage_prefix = getattr(settings, 'IGNORE_LANGUAGE_PREFIX', False)
        append_slash = getattr(settings, 'APPEND_SLASH', False)

        if not ignore_lanaguage_prefix:
            # if not found lets try and make sure it is not because of language
            if not self.is_found and language_code:
                # new code to make us django language aware (strip language code when looking for a template)
                # print('request lang: ' + str(request.LANGUAGE_CODE))
                # print('settings lang: ' + str(settings.LANGUAGE_CODE))
                # print('languages: ' + str(settings.LANGUAGES))
                lang = f'/{language_code}/'
                if self.original_path.startswith(lang):
                    self.path = self.original_path[len(lang):]
                    self.file_name = os.path.join(self.docroot_dir, self.path)
                    log.debug("language stripped file: " + str(self.file_name))
                    self.module_name = self.path
                    self.template_name = self.path
                    # re-try and modify urls for logic on how to pull the correct template
                    self.find_template()

            # finally if we still don't have a template and ends with / and APPEND_SLASH is set and False strip it
            if not self.is_found and language_code and append_slash and self.original_path.endswith('/'):
                lang = f'/{language_code}/'
                if self.original_path.startswith(lang):
                    # same as above except now try to strip the last slash
                    self.path = self.original_path[len(lang):len(self.original_path) - 1]
                    self.file_name = os.path.join(self.docroot_dir, self.path)
                    log.debug("language stripped file: " + str(self.file_name))
                    self.module_name = self.path
                    self.template_name = self.path
                    # re-try and modify urls for logic on how to pull the correct template
                    self.find_template()

    # contains the logic for taking a request url and attempting to locate a page template for it
    def find_template(self):
        # if the url ends in .html then try to load a corresponding template from the docroot/files directory
        if self.file_name.endswith(".html"):
            # our url will request .html but we want to look for a .dt file (required for template processing)
            self.file_name = self.file_name[:-4]
            self.file_name += "dt"
            self.template_name = self.template_name[:-4]
            self.template_name += "dt"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.is_found = True

        elif self.file_name.endswith('/'):
            self.file_name += "index.dt"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.module_name += "index.html"
                self.template_name += "index.dt"
                self.is_found = True

        else:
            self.file_name += ".dt"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.module_name += ".html"
                self.template_name += ".dt"
                self.is_found = True

    def render(self):
        if self.is_found:
            log.debug("opening file: " + str(self.file_name))
            fp = codecs.open(self.file_name, "r", encoding='utf-8')
            log.debug("loading template...")
            # template = Template(fp.read().encode('utf-8'), Origin(self.file_name), self.template_name)
            # sas django 2.2 no longer reqiures bytes so we can go back to just reading it in
            # if this has problems with utf-8 content then do a decode afterwards instead
            template = DjangoTemplate(fp.read(), Origin(self.file_name), self.template_name)
            log.debug("closing file")
            fp.close()

            if template:
                log.debug("attempting to load context and render the template...")
                return self.render_page(self.request, template, self.module_name)
            else:
                return None

    def is_found(self):
        return self.is_found

    def __str__(self):
        return self.file_name

    @staticmethod
    @csrf_protect
    def render_page(request, template, module_name):
        """
        Internal interface to the dev page view.
        """
        context = {}
        log.debug("template name: " + template.name)
        log.debug("module_name: " + module_name)
        datafile_name = template.origin.name
        # strip off the html and try data.py
        if datafile_name.endswith('dt'):
            datafile_name = datafile_name[0:len(datafile_name) - 2]
            datafile_name += 'data.py'
            log.debug("datafilename: " + datafile_name)
        # else:
        #     datafile_name += '.data.py'
        # try to load a data file if it is there in order to get the context
        # all data files should support get_context() or a context property
        try:
            log.debug("attempting to load data_file...")
            spec = importlib.util.spec_from_file_location(module_name, datafile_name)
            data = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(data)

            # datafile = imp.load_source(module_name, datafile_name)
            # note changing datafile below to data
        except FileNotFoundError:
            data = None
        except Exception as ex:
            # logging.error(traceback.format_exc())
            data = None
            if settings.DEBUG:
                raise ex
        if data:
            try:
                initmethod = getattr(data, 'get_context')
            except AttributeError:
                initmethod = None
            if initmethod:
                # we may want to return something like a redirect so if is response then return it; else use for data!
                context = initmethod(request)
                if isinstance(context, HttpResponse):
                    return context
            else:
                try:
                    context = getattr(data, 'context')
                except AttributeError:
                    context = {}
        # print("context string: " + str(context))
        template_context = RequestContext(request)
        if context:
            template_context.push(context)
        response = HttpResponse(template.render(template_context))
        # add a canonical header if we are doing some fancy string replacement so analytics work properly with SEO
        if request.path != "/" + module_name and request.scheme and request.get_host():
            response['Link'] = f'< {request.scheme}://{request.get_host()}/{module_name} >; rel="canonical"'

        return response


class Data:
    pass


class TemplateMeta:
    """
        encapsulates the core atts and methods to get a valid template
    """

    def __init__(self, request):
        # setup our basic attributes for the meta-data we will use for validation and template creation
        self.is_found = False
        self.request = request
        self.docroot_dir = getattr(settings, "DOCROOT_ROOT", "")
        log.debug("docroot dir: " + str(self.docroot_dir))
        self.original_path = request.path_info.strip()
        self.path = self.original_path
        if self.path.startswith("/"):
            self.path = self.path[1:]
        self.file_name = os.path.join(self.docroot_dir, self.path)
        log.debug("file: " + str(self.file_name))
        self.module_name = self.path
        self.template_name = self.path
        # try and modify urls for logic on how to pull the correct template
        self.find_template()

        # get our settings needed for processing defaulting if they are not there
        ignore_lanaguage_prefix = getattr(settings, 'IGNORE_LANGUAGE_PREFIX', False)
        append_slash = getattr(settings, 'APPEND_SLASH', False)

        if not ignore_lanaguage_prefix:
            # if not found lets try and make sure it is not because of language
            if not self.is_found and request.LANGUAGE_CODE:
                # new code to make us django language aware (strip language code when looking for a template)
                # print('request lang: ' + str(request.LANGUAGE_CODE))
                # print('settings lang: ' + str(settings.LANGUAGE_CODE))
                # print('languages: ' + str(settings.LANGUAGES))
                lang = '/' + request.LANGUAGE_CODE + "/"
                if self.original_path.startswith(lang):
                    self.path = self.original_path[len(lang):]
                    self.file_name = os.path.join(self.docroot_dir, self.path)
                    log.debug("language stripped file: " + str(self.file_name))
                    self.module_name = self.path
                    self.template_name = self.path
                    # re-try and modify urls for logic on how to pull the correct template
                    self.find_template()

            # finally if we still don't have a template and ends with / and APPEND_SLASH is set and False strip it
            if not self.is_found and request.LANGUAGE_CODE and append_slash and self.original_path.endswith('/'):
                lang = '/' + request.LANGUAGE_CODE + "/"
                if self.original_path.startswith(lang):
                    # same as above except now try to strip the last slash
                    self.path = self.original_path[len(lang):len(self.original_path) - 1]
                    self.file_name = os.path.join(self.docroot_dir, self.path)
                    log.debug("language stripped file: " + str(self.file_name))
                    self.module_name = self.path
                    self.template_name = self.path

                    # re-try and modify urls for logic on how to pull the correct template
                    self.find_template()

    # contains the logic for taking a request url and attempting to locate a page template for it
    def find_template(self):
        # if the url ends in .html then try to load a corresponding template from the docroot/files directory
        if self.file_name.endswith(".html"):
            # our url will request .html but we want to look for a .dt file (required for template processing)
            self.file_name = self.file_name[:-4]
            self.file_name += "dt"
            self.template_name = self.template_name[:-4]
            self.template_name += "dt"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.is_found = True

        elif self.file_name.endswith('/'):
            self.file_name += "index.dt"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.module_name += "index.html"
                self.template_name += "index.dt"
                self.is_found = True

        else:
            self.file_name += ".dt"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.module_name += ".html"
                self.template_name += ".dt"
                self.is_found = True

    def render(self):
        if self.is_found:
            log.debug("opening file: " + str(self.file_name))
            fp = codecs.open(self.file_name, "r", encoding='utf-8')
            log.debug("loading template...")
            # template = Template(fp.read().encode('utf-8'), Origin(self.file_name), self.template_name)
            # sas django 2.2 no longer reqiures bytes so we can go back to just reading it in
            # if this has problems with utf-8 content then do a decode afterwards instead
            template = DjangoTemplate(fp.read(), Origin(self.file_name), self.template_name)
            log.debug("closing file")
            fp.close()

            if template:
                log.debug("attempting to load context and render the template...")
                return self.render_page(self.request, template, self.module_name)
            else:
                return None

    def is_found(self):
        return self.is_found

    def __str__(self):
        return self.file_name

    @staticmethod
    @csrf_protect
    def render_page(request, template, module_name):
        """
        Internal interface to the dev page view.
        """
        context = {}
        log.debug("template name: " + template.name)
        log.debug("module_name: " + module_name)
        datafile_name = template.origin.name
        # strip off the html and try data.py
        if datafile_name.endswith('dt'):
            datafile_name = datafile_name[0:len(datafile_name) - 2]
            datafile_name += 'data.py'
            log.debug("datafilename: " + datafile_name)
        # else:
        #     datafile_name += '.data.py'
        # try to load a data file if it is there in order to get the context
        # all data files should support get_context() or a context property
        try:
            log.debug("attempting to load data_file...")
            spec = importlib.util.spec_from_file_location(module_name, datafile_name)
            data = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(data)

            # datafile = imp.load_source(module_name, datafile_name)
            # note changing datafile below to data
        except FileNotFoundError:
            data = None
        except Exception as ex:
            # logging.error(traceback.format_exc())
            data = None
            if settings.DEBUG:
                raise ex
        if data:
            try:
                initmethod = getattr(data, 'get_context')
            except AttributeError:
                initmethod = None
            if initmethod:
                # we may want to return something like a redirect so if is response then return it; else use for data!
                context = initmethod(request)
                if isinstance(context, HttpResponse):
                    return context
            else:
                try:
                    context = getattr(data, 'context')
                except AttributeError:
                    context = {}
        # print("context string: " + str(context))
        template_context = RequestContext(request)
        if context:
            template_context.push(context)
        response = HttpResponse(template.render(template_context))
        # add a canonical header if we are doing some fancy string replacement so analytics work properly with SEO
        if request.path != "/" + module_name and request.scheme and request.get_host():
            response['Link'] = f'< {request.scheme}://{request.get_host()}/{module_name} >; rel="canonical"'

        return response


class ApiMeta:
    """
        encapsulates the core atts and methods to get a valid api data file and process it
    """

    def __init__(self, request):
        self.ALL_OPTIONS = ['GET', 'POST', 'PUT', 'TRACE', 'DELETE', 'HEAD', 'PATCH']
        self.options = []
        # setup our basic attributes for the meta-data we will use for validation and api creation
        self.is_found = False
        self.request = request
        self.docroot_dir = getattr(settings, "DOCROOT_ROOT", "")
        log.debug("docroot dir: " + str(self.docroot_dir))
        self.original_path = request.path_info.strip()
        self.path = self.original_path
        if self.path.startswith("/"):
            self.path = self.path[1:]
        self.file_name = os.path.join(self.docroot_dir, self.path)
        log.debug("file: " + str(self.file_name))
        self.api_name = self.path
        # try and modify urls for logic on how to pull the correct template
        self.find_api()

        # get our settings needed for processing defaulting if they are not there
        ignore_lanaguage_prefix = getattr(settings, 'IGNORE_LANGUAGE_PREFIX', False)
        append_slash = getattr(settings, 'APPEND_SLASH', False)

        if not ignore_lanaguage_prefix:
            # if not found lets try and make sure it is not because of language
            if not self.is_found and request.LANGUAGE_CODE:
                # new code to make us django language aware (strip language code when looking for a template)
                # print('request lang: ' + str(request.LANGUAGE_CODE))
                # print('settings lang: ' + str(settings.LANGUAGE_CODE))
                # print('languages: ' + str(settings.LANGUAGES))
                lang = '/' + request.LANGUAGE_CODE + "/"
                if self.original_path.startswith(lang):
                    self.path = self.original_path[len(lang):]
                    self.file_name = os.path.join(self.docroot_dir, self.path)
                    log.debug("language stripped file: " + str(self.file_name))
                    self.api_name = self.path
                    # re-try and modify urls for logic on how to pull the correct template
                    self.find_api()

            # finally if we still don't have an api and ends with / and APPEND_SLASH is set try without language prefix
            # NOTE: this is needed because if APPEND_SLASH is set when django is finished processing we can have a
            #   unexpected slash EX: request-> /test/index.json | after django -> /test/index.json/
            if not self.is_found and request.LANGUAGE_CODE and append_slash and self.original_path.endswith('/'):
                lang = '/' + request.LANGUAGE_CODE + "/"
                if self.original_path.startswith(lang):
                    # same as above except now try to strip the last slash
                    self.path = self.original_path[len(lang):len(self.original_path) - 1]
                    self.file_name = os.path.join(self.docroot_dir, self.path)
                    log.debug("language stripped file: " + str(self.file_name))
                    self.api_name = self.path
                    # re-try without the language code
                    self.find_api()

    # contains the logic for taking a request url and attempting to locate an api for it
    def find_api(self):
        # if the url ends in .json then try to load a corresponding api from the docroot/files directory
        if self.file_name.endswith(".json"):
            # our url will request .json but we want to look for a .data.py file
            self.file_name = self.file_name[:-4]
            self.file_name += "data.py"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + self.file_name)
                self.is_found = True
        elif self.file_name.endswith('/'):
            self.file_name += "index.data.py"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.api_name += "index.json"
                self.is_found = True
        else:
            self.file_name += ".data.py"
            if os.path.isfile(self.file_name):
                log.debug("found file: " + str(self.file_name))
                self.api_name += ".json"
                self.is_found = True

    def render(self):
        # return none if not found
        if self.is_found:
            # try to load a data file if it is there in order to get the context
            # all data files should support get_context() or a context property
            try:
                log.debug("attempting to load data_file...")
                spec = importlib.util.spec_from_file_location(self.api_name, self.file_name)
                data = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(data)
                # datafile = imp.load_source(module_name, datafile_name)
                # note changing datafile below to data
            except FileNotFoundError:
                return None
            except Exception as ex:
                data = None
                logging.error(str(ex))
                if settings.DEBUG:
                    raise ex

            if data:
                methods = dir(data)
                for method in methods:
                    if method in self.ALL_OPTIONS:
                        self.options.append(method)
                # figure out the proper method to call (get, post trace etc) return method not supported if not there
                request_method = self.request.method
                # adding method overriding; very useful for testing or getting around proxies
                # look for a GET or POST "_method" parameter and change the method we are looking for if found
                override = self.request.GET.get('_method')
                if not override:
                    override = self.request.POST.get('_method')
                if override:
                    request_method = override.upper().strip()
                    log.debug(f"Overriding method [{self.request.method}] with parameter value [{request_method}]")
                try:
                    initmethod = getattr(data, request_method)
                except AttributeError:
                    initmethod = None
                if initmethod:
                    # we may want to return something like a redirect so if is response then return it; else use for
                    # data!
                    content = initmethod(self.request)
                    if isinstance(content, HttpResponse):
                        return content
                    else:
                        response = HttpResponse(content)
                        response['Allow'] = ",".join(self.options)
                        # response['Content-Type'] = "application/json"
                        return response
                else:
                    log.error(
                        "Found datafile [" + self.file_name + "] but didn't find method [" + request_method + "]!")
                    # if we don't support any methods lets return a not found instead of method not supported
                    #   since there is no way to adjust the call to get it to work
                    if not self.options:
                        return None
                    response = HttpResponse("Method Not Supported [" + request_method + "]!", status=405)
                    response['Allow'] = ",".join(self.options)
                    # response['Content-Type'] = "text/plain"
                    return response

    def is_found(self):
        return self.is_found

    def __str__(self):
        return self.file_name
