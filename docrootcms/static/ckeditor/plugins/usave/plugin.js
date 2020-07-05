function u_getRelativeUrlId() {
    var rel_url = window.location.pathname;
    // may need to strip off the hash
    var pos = -1;
    if (window.location.anchor)
        pos = rel_url.lastIndexOf(window.location.anchor);
    if (pos > -1)
        rel_url = rel_url.substring(0, pos);
    // may need to strip off the query string stuff
    if (window.location.search)
        pos = rel_url.lastIndexOf(window.location.search);
    if (pos > -1)
        rel_url = rel_url.substring(0, pos);
    // may need to strip off the index.html
    pos = rel_url.lastIndexOf("index.html");
    if (pos > -1)
        rel_url = rel_url.substring(0, pos);
    return rel_url;
}
function u_getId(editor) {
    var element = editor.element;
    var id = element.getAttribute("id");
    if (id == undefined || id == '')
        id = editor.id;
    return id;
}
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// get the crsf token to be able to submit to the server
var csrftoken = getCookie('csrftoken');
// alert(csrftoken);
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain && csrftoken) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

CKEDITOR.plugins.add( 'usave', {
    icons: 'usave',
    init: function( editor ) {
        console.log('testing init...');
        var element = editor.element;
        // some basic global settings that we want for all editors; NOTE: can be overridden at page level
        if ( element.is( 'h1', 'h2', 'h3' ) || element.getAttribute( 'id' ) == 'taglist' ) {
            // Customize the editor configuration on "configLoaded" event,
            // which is fired after the configuration file loading and
            // execution. This makes it possible to change the
            // configuration before the editor initialization takes place.
            editor.on( 'configLoaded', function () {
                // Remove redundant plugins to make the editor simpler.
                editor.config.removePlugins = 'colorbutton,find,flash,font,' +
                    'forms,iframe,image,newpage,removeformat,' +
                    'smiley,specialchar,stylescombo,templates';
                // Rearrange the toolbar layout.
                editor.config.toolbarGroups = [
                    { name: 'editing', groups: [ 'basicstyles', 'links' ] },
                    { name: 'undo' },
                    { name: 'clipboard', groups: [ 'selection', 'clipboard' ] },
                    { name: 'about' }
                ];
                // Try to insert the browseurl
                editor.config.filebrowserBrowseUrl = '/browser/browse.php?type=files';
                editor.config.filebrowserImageBrowseUrl = '/browser/browse.php?type=images';
                //editor.config.saveSubmitURL = '';
            } );
        }
        else {
            // customize all the other ones
            editor.on( 'configLoaded', function () {
                // Try to insert the browseurl
                editor.config.filebrowserBrowseUrl = '/browser/browse.php?type=files';
                editor.config.filebrowserImageBrowseUrl = '/browser/browse.php?type=images';
                //editor.config.saveSubmitURL = '';
            } );
        }

        editor.on('instanceReady', function() {
            console.log('insance is ready...');
            //var _loadurl = editor.config.usaveLoadURL
            // get our data and replace the ckeditor data with the results
            // initially replace the data from database if we have some (don't forget global)
            var loadUrl = editor.config.usaveLoadURL;
            console.log('load url: ' + loadUrl);
            if (loadUrl) {
                $.ajax({
                    method: "GET",
                    dataType: "json",
                    url: loadUrl, // "/content",
                    data: {"uri": u_getRelativeUrlId()}
                }).done(function (msg) {
                    console.log('------------ loading editor data from server -------------');
                    console.log('ready: asking server for all content with this url...');
                    console.log("ready: server response: " + JSON.stringify(msg));
                    // determine if there is a editor with this id and replace the value
                    for(var instanceName in CKEDITOR.instances) {
                        console.log("ready: instaceName -> " + instanceName);
                        var editor = CKEDITOR.instances[instanceName];
                        var id = u_getId(editor);
                        console.log("ready: id: " + id);
                        msg.forEach(function(entry) {
                            if (entry.element_id == id) {
                                editor.setData(entry.content, {noSnapshot: true});
                                editor.resetDirty();
                                console.log("ready: set data for id: " + id);
                            }
                        });
                    }
                    console.log('------------ loading editor data from server -------------');
                }).fail(function (jqXHR, textStatus) {
                    console.log("ready: server read failed: " + JSON.stringify(textStatus));
                    console.log('------------ loading editor data from server -------------');
                });

            }
            else
                console.log("usave load url not found skipping data read for page...");
        });

        console.log('saveSubmitURL: ' + editor.config.usaveSubmitURL);
        if (editor.config.usaveSubmitURL == undefined || editor.config.usaveSubmitURL == '') {
            console.log('save configuration not found.  Skipping the initialization and building of button...');
        } else {
            editor.addCommand('usave', {
                exec: function (editor) {
                    // only save and stuff if we are dirty
                    if (editor.checkDirty() == true) {
                        // disable the button so we can't click while processing again (multiple causes problems like icons shifting)
                        var usave_button = $('.cke_button__usave_icon');
                        usave_button.prop("disabled", true);
                        //get the text from ckeditor you want to save
                        var data = editor.getData();
                        var element = editor.element;
                        //get the current url (optional)
                        var rel_url = u_getRelativeUrlId();
                        var id = u_getId(editor);
                        //path to the ajaxloader gif
                        loading_icon = CKEDITOR.basePath + 'plugins/usave/icons/loader.gif';

                        //css style for setting the standard save icon.
                        //We need this when the request is completed.
                        normal_icon = usave_button.css('background-image');

                        //replace the standard save icon with the ajaxloader icon.
                        //We do this with css.
                        usave_button.css("background-image", "url(" + loading_icon + ")");

                        console.log('url: ' + editor.config.usaveSubmitURL);
                        //Now we are ready to post to the server...
                        $.ajax({
                            url: editor.config.usaveSubmitURL,//the url to post at... configured in config.js
                            type: 'POST',
                            contentType: "application/json",
                            dataType: "json",
                            data: JSON.stringify({"element_id": id, "uri": rel_url, "content": data})
                            //data: {content: data, id: editor.name, url: page}
                        })
                            .done(function (data, textStatus, jqXHR) {
                                // console.log(jqXHR.status);
                                // console.log(textStatus);
                                console.log("done: " + data);
                                if (jqXHR.status && (jqXHR.status == 200 || jqXHR.status == 201)) {
                                    alert("Edits were saved.");
                                    //console.log('id: ' + id + ' \nurl: ' + rel_url + ' \ncontent: ' + data);
                                    console.log('[' + id + '] ' + rel_url + ' saved.');
                                    editor.resetDirty();
                                }
                                else
                                    console.log('[' + jqXHR.status + '] ' + textStatus)
                            })
                            .fail(function (jqXHR, textStatus) {
                                console.log("server save error: " + JSON.stringify(textStatus));
                            })
                            .always(function () {
                                console.log("complete");
                                //set the button icon back to the original
                                usave_button.css("background-image", normal_icon);
                                usave_button.prop("disabled", false);
                            });
                    } else {
                        console.log('No edits were made.  Skipping save...');
                    }
                }
            });

            editor.ui.addButton('uSave', {
                label: 'Save Changes',
                command: 'usave',
                toolbar: 'editing'
            });
        }
        // tutorial example to load the dynamic portion of the ckeditor dialog framework
        //CKEDITOR.dialog.add( 'usaveDialog', this.path + 'dialogs/usave.js' );
    }
});