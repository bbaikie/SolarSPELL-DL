import os
import errno
import json
from flask import Flask, render_template, request, redirect,send_from_directory
app = Flask(__name__, static_folder='static',static_url_path="/static/")

BASE_PATH=u'/var/www/new_flask_site/new_solarspell_site/static/content/'
TOP_NAV_JSON={}
app = Flask(__name__, static_folder='static',static_url_path="/static/")
reference_tool_links={"1":{"name":"Wikipedia","link":"1", "redirect": "http://10.10.10.10:82/Wikipedia/"},
                      "2": {"name": "PHET Simulations", "link": "2", "redirect": "http://10.10.10.10:82/phet/index.html"},
                      "3": {"name": "KA Lite", "link": "3" , "redirect": "http://10.10.10.10:8008"},
                      "4": {"name": "Medical Encyclopedia", "link": "4" , "redirect": "http://10.10.10.10:82/en-medline_plus/"},
                      "5": {"name": "ODK Kit", "link": "5" , "redirect": "http://10.10.10.10:82/en-odkkit/"},
                      "6": {"name": "Virtual Field Trip", "link": "6" , "redirect": "http://10.10.10.10:82/VR/"},

                          }



def get_json_titles():
    global TOP_NAV_JSON
    if(TOP_NAV_JSON=={}):
        title_div = json_folder_hierarchy(BASE_PATH, 2)
        TOP_NAV_JSON=title_div["children"]
        return TOP_NAV_JSON
    else:
        return TOP_NAV_JSON
def folder_hierarchy(path, index):
    hierarchy = {
        'type': 'folder',
        'name': os.path.basename(path),
        'path': path,
    }
    if(index==0):

        ## Checking for Traversal
        try:
            for contents in os.listdir(path):
                pass
        except OSError as e:
            if e.errno != errno.ENOTDIR:
                raise
            hierarchy['type'] = 'file'

        return hierarchy
    index=index-1

    ## Actual Traversal
    try:
        hierarchy['children'] = [
            folder_hierarchy(os.path.join(path, contents ), index)
            for contents in os.listdir(path)
        ]
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        hierarchy['type'] = 'file'

    return hierarchy

def json_folder_hierarchy(path, index):
    hierarchy = {
        'type': 'folder',
        'name': os.path.basename(path),
        'path': path,
    }
    if(index==0):

        ## Checking for Traversal
        try:
            for contents in os.listdir(path):
                pass
        except OSError as e:
            if e.errno != errno.ENOTDIR:
                raise
            hierarchy['type'] = 'file'

        return hierarchy
    index=index-1

    ## Actual Traversal
    try:
        hierarchy['children'] = {
            contents:json_folder_hierarchy(os.path.join(path, contents ), index)
            for contents in os.listdir(path)
        }
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        hierarchy['type'] = 'file'

    return hierarchy


@app.route('/path/<path:path>')
def send_path_content(path):
    folder_list = json_folder_hierarchy(path,1)
    print(folder_list)

    return  json.dumps(folder_list)

@app.route('/spellmodules/<path:path_request>')
def send_content_for_path(path_request):

    info_div={}

    folder_list = json_folder_hierarchy("/"+path_request, 1)
    title_div=get_json_titles()

    current_subject = path_request

    current_subject =current_subject.replace("\\","/")
    current_subject = current_subject.replace("//", "/")
    print("current_subject:"+current_subject)
    subject_start=current_subject.find("content/")+8
    subject_end=current_subject.find("/",subject_start)
    if(subject_end!=-1):
        subject= current_subject[subject_start:subject_end]
    else:
        subject = current_subject[subject_start:]
    subject = subject.replace("%20", " ")
    subject.strip()
    print("subject:"+subject)

    try:
        print(title_div[subject]  )
    except:
        return redirect("/", code=302)


    print(request.referrer)

    info_div["back_link"]=request.referrer
    info_div["current_link"] = path_request
    info_div["current_subject"] = subject
    base_link={"base_link":BASE_PATH}

    return render_template('ajax_json_check.html', file_structure=json.dumps(folder_list),base_link=json.dumps(base_link),
                           menu_titles=json.dumps(title_div),info_div=json.dumps(info_div),
                           reference_tool_links=json.dumps(reference_tool_links))

def path_hierarchy(path):
    hierarchy = {
        'type': 'folder',
        'name': os.path.basename(path),
        'path': path,
    }

    try:
        hierarchy['children'] = {
            contents:path_hierarchy(os.path.join(path, contents))
            for contents in os.listdir(path)
        }
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        hierarchy['type'] = 'file'

    return hierarchy



@app.route('/')
def homepage_control():
    info_div = {}
    base_link={"base_link":BASE_PATH}
    directory = os.path.expanduser(BASE_PATH)
    file_structure =json_folder_hierarchy(directory,1)
    print(file_structure)
    title_div = get_json_titles()
    print(title_div)
    info_div["back_link"]="/"
    info_div["current_link"] = "/"
    info_div["current_subject"] = ""

    return render_template('homepage.html', file_structure=json.dumps(file_structure), menu_titles=json.dumps(title_div),
                           info_div=json.dumps(info_div),base_link=json.dumps(base_link),
                           reference_tool_links=json.dumps(reference_tool_links))


@app.route('/aboutus/')
def about_us_control():
    info_div = {}
    directory = os.path.expanduser(BASE_PATH)
    file_structure =json_folder_hierarchy(directory,1)
    print(file_structure)
    title_div = get_json_titles()
    print(title_div)
    info_div["back_link"]="/"
    info_div["current_link"] = "/"
    info_div["current_subject"] = ""
    return render_template('about_us.html', file_structure=json.dumps(file_structure), menu_titles=json.dumps(title_div),
                           info_div=json.dumps(info_div),reference_tool_links=json.dumps(reference_tool_links))


@app.route('/static/<path:path>')
def send_static(path):
    print(path)

    return send_from_directory(app.static_folder, path)


@app.route('/reference_tools/<link>')
def reference_tools_redirect(link):
    link=link.replace("%20", " ")
    if link in reference_tool_links.keys():
       return  redirect(reference_tool_links[link]["redirect"] )
    else:
       return  redirect(link)

@app.route('/pdftest/')
def pdf_test():
    return  render_template('pdfjstest.html')

if __name__ == "__main__":
        app.run(host='localhost', port=8888, debug=True)
        directory = BASE_PATH
