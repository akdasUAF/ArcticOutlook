import subprocess, os, json, zipfile, math, re
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, redirect, send_file, flash, url_for, jsonify
from werkzeug.utils import secure_filename
from pymongo import MongoClient
from scripts.community_profiles import main
from scripts.initial_scrape import main as init_scrape
from dynamic_v2.Extract import main as dynamic_v2
from dynamic_v2.view_instruction import main as get_url
from dynamic_v2.ScraperInstructionType import ScraperInstructionType
from server.node import Node
import server.node as node
from server.query_manager import QueryManager
from server.file_upload import FileUpload
from server.scrape_items import ScrapeItems

# Name of the module initializing / running the program
app = Flask(__name__)
app.secret_key = b'secret_key_testing'
app.debug = True
app.config['UPLOAD_FOLDER'] = './files'
app.config['TEMPLATE_FOLDER'] = './template_info'

si = ScrapeItems()
file_upload = FileUpload()
qm = QueryManager()

def output_csv(uri, db, col, file):
    """A simple function that pulls a collection from MongoDB without the index and stores it into the specified file."""
    client = MongoClient(uri)
    database = client[db]
    collection = database[col]

    df = pd.DataFrame(list(collection.find({}, {'_id': False})))
    df.to_csv(file)

def display_text_input(s):
    """Simple method to determine which text boxes should be displayed for the static scrapers in the new form. 
    Returns an error if something goes wrong."""
    # Display operator parameters based on user input.
    with open('./files/settings.json','r') as f :
        file=json.load(f)

    if s == "Dynamic_Scraper_Upload":
        return list(file[s].values())
    
    elif s in ('Operators', 'Systems', 'Community_Profiles'):
        defaults = list(file[s].values())
        return render_template(
            'static_scrapers.html',
            operation=True,
            val=s,
            default=defaults)
    
    # Something went wrong
    else:
        return render_template(
            'static_scrapers.html',
            operation=False,
            msg="Something went wrong."
        )

"""Scraper Subprocess Calls"""
def run_operators_spider(request):
    """This method launches a subprocesses that will run the operators spider in /operators."""
    uri = request.form['Connection']
    db = request.form['Database']
    op = request.form['Operators']

    # Change directory to operators directory
    root = os.getcwd()
    os.chdir("../operators") 
    path = os.getcwd()

    # Run the scrapy subprocess
    proc = subprocess.Popen(["scrapy", "crawl",
                        "-s", "MONGODB_URI="+uri, 
                        "-s", "MONGODB_DATABASE="+db, 
                        "-s", "MONGODB_COLLECTION="+op, 
                        "operators"],
                        cwd=path)
    proc.wait()
    os.chdir(root)

    if request.form.get("download"):
        return static_download_op(uri, db, op)

    return render_template(
        'static_scrapers.html',
        operation=False,
        msg="Operator spider finished uploading to MongoDB."
    )

def run_systems_spider(request):
    """This method launches a subprocesses that will run the water systems spider in /systems."""
    uri = request.form['Connection']
    db = request.form['Database']
    sys = request.form['Systems']
    con = request.form['SContact']

    # Change path to systems directory
    root = os.getcwd()
    os.chdir("../systems") 
    path = os.getcwd()

    # Run the scrapy subprocess
    proc = subprocess.Popen(["scrapy", "crawl",
                        "-s", "MONGODB_URI="+uri,
                        "-s", "MONGODB_DATABASE="+db,
                        "-s", "MONGODB_COLLECTION_SYSTEMS="+sys,
                        "-s", "MONGODB_COLLECTION_CONTACTS="+con,
                        "systems"],
                        cwd=path)
    proc.wait()
    os.chdir(root)

    # Check if the user wants to download the information as a csv.
    if request.form.get("download"):
        return static_download_sys(uri, db, sys, con)

    # Return response to the user.
    return render_template(
        'static_scrapers.html',
        operation=False,
        msg="System spider finished uploading to MongoDB."
    )

def run_community_profiles_script(request):
    """This function handles the call to the community profiles script located in /scripts."""
    uri = request.form['Connection']
    db = request.form['Database']
    comm = request.form['Community']
    con = request.form['CContact']

    main(['-uri', uri, '-db', db, '-comm', comm, '-con', con])

    # Check if the user wants to download the information as a csv.
    if request.form.get("download"):
        return static_download_cc(uri, db, comm, con)
    
    # Return response to the user.
    return render_template(
        'static_scrapers.html',
        operation=False,
        msg="Finished uploading community information to MongoDB."
    )

# Home page
@app.route("/", methods=['POST', 'GET'])
@app.route("/home", methods=['POST', 'GET'])
@app.route("/index", methods=['POST', 'GET'])
def index():
    """This function handles the display of the main page and redirects the user to the proper webpage."""
    if request.method == 'POST':
        if 'select_task' in request.form:
            if request.form['SelectTask'] == 'static_scrapers':
                return redirect("/scrapers")
            elif request.form['SelectTask'] == 'dynamic_v2':
                return redirect("/dynamic_v2")
            elif request.form['SelectTask'] == 'upload_file':
                return redirect("/upload_csv")
            elif request.form['SelectTask'] == 'query_manager':
                return redirect("/query_manager")
            else:
                return redirect("/dynamic")
        return render_template('index.html')   
    return render_template('index.html')   

def add_link(url, s):
    si.url = url
    si.url_count = si.url_count + 1
    si.scrape_items['Link ' + str(si.url_count)] = {'url': si.url, 'scraped items': {}, 'follow': s}

"""
Dynamic Scraper v1
"""
@app.route("/dynamic", methods=['POST', 'GET'])
def run_dynamic_scraper():
    """This function handles the display and operation of the WIP 'dynamic' scraper interface."""
    # If the user hits the submit button, send the information to the server.
    if request.method == 'POST':
        if 'url_submit' in request.form:
            url = request.form['url'].strip()
            if url == '':
                return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url.",
                                        url_needed=True)
            add_link(url, "no")
            si.base_url = url
            return redirect("/dynamic-add-item")
        if 'add_item' or 'scrape' in request.form:
            return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url before trying to add/scrape items.",
                                        url_needed=True)
        
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        si.clear()
        return render_template('dynamic_scraper.html', url_needed=True)

@app.route("/dynamic-add-item", methods=['POST', 'GET'])
def dynamic_add():
    if request.method == 'POST':
        if 'url_submit' in request.form:
            url = request.form['url'].strip()
            if url == '':
                return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url.",
                                        url_needed=True)
            add_link(url, "no")
            return render_template('dynamic_scraper.html',
                                items_submitted=True,
                                url_needed=False,
                                dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())))
        
        if 'add_item' in request.form:
            # Pull all items from the form
            name = request.form['name'].strip()
            item = request.form['item'].strip()
            arg_select = request.form['arg_select']
            if name == '' or item == '':
                return render_template('dynamic_scraper.html',
                                items_submitted=True,
                                url_needed=False,
                                dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())),
                                error="Input string was empty. Please resubmit item with proper name and selector values.")
            # If the item is valid, add it to the dictionary and return the new list of items.
            si.scrape_items['Link ' + str(si.url_count)]['scraped items'][name] = {'item':item, 'type':arg_select}
            if request.form['follow'] == 'yes':
                add_link(item, "yes")
            return render_template('dynamic_scraper.html',
                                items_submitted=True,
                                url_needed=False,
                                dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())))
        
        if 'scrape' in request.form:
            return redirect("/dynamic-scrape")
    
    return render_template('dynamic_scraper.html',
                            items_submitted=True,
                            url_needed=False,
                            dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())))

@app.route("/dynamic-scrape", methods=['POST', 'GET'])
def dynamic_scrape():
    if request.method =='POST':
        if 'url_submit' in request.form:
            return redirect("/dynamic-add-item")
        
        if 'download' in request.form:
            return redirect("/dynamic/download")

    # try:
        # Pass the dictionary to the scraper
    vals = si.scrape_items
    url = si.base_url
    result = init_scrape(['-url', url,'-v', str(vals)])
    if isinstance(result, str):
            return render_template('dynamic_scraper.html',
                            error="Error encountered during scrape: " + result,
                            url_needed=True)
    
    file = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
    final = json.dumps(result, indent=2)
    output = open(file, "w") 
    json.dump(result, output, indent=2)
    output.close()
    si.clear()

    return render_template('dynamic_scraper_output.html',
                        scrape=True,
                        output=final)   

@app.route("/dynamic-delete/<string:link>&<string:key>")
def dynamic_delete(link, key):
    i = si.scrape_items[link]['scraped items']
    i.pop(key)
    return redirect("/dynamic-add-item")

@app.route("/dynamic-update/<string:link>&<string:key>", methods=['POST','GET'])
def dynamic_update(link, key):
    # If the user submits an update request, update the item.
    if 'update_item' in request.form:
        name = request.form['name'].strip()
        item = request.form['item'].strip()
        arg_select = request.form['arg_select']
        i = si.scrape_items[link]['scraped items']
        i[name] = {'item':item, 'type':arg_select}
        return redirect("/dynamic-add-item")
    
    # Otherwise, find the item the user is requesting to delete and display it.
    name = key
    i = si.scrape_items[link]['scraped items']
    selector = i[key]['item']
    select_type = i[key]['type']
    i.pop(key)
    return render_template('dynamic_update.html',
                           name=name,
                           css_selector=selector,
                           select_type=select_type)

"""
Original Static Scrapers
"""
@app.route("/scrapers", methods=['POST','GET'])
def run_static_scrapers():
    """This function handles the display and operation of the pre-made scrapers."""
    if request.method == 'POST':
        # User has selected a scraper to run.
        if 'script' in request.form:
            script = request.form['SelectScript']
            return display_text_input(script)
        
        # Operator form submitted
        elif 'op' in request.form:
            return run_operators_spider(request)
        
        # Systems form submitted
        elif 'sys' in request.form:
            return run_systems_spider(request)
        
        # Community profile form submitted.
        elif 'cc' in request.form:
            return run_community_profiles_script(request)
    
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        return render_template('static_scrapers.html')

@app.route("/dynamic/download")
def dynamic_download():
    file = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
    return send_file(
            file,
            mimetype='text/csv',
            download_name='output.json',
            as_attachment=True
        )

@app.route("/dynamic/upload")
def dynamic_upload(mongo_uri, mongo_db, mongo_col):
    # Upload file to MongoDB
    mongoClient = MongoClient(mongo_uri)
    db = mongoClient[mongo_db]
    col = db[mongo_col]
    file = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
    with open(file) as f:
        data = json.load(f)
    col.insert_many(data)
    return redirect("dynamic_v2")

def static_download_op(uri, db, col):
    # Create file paths.
    file = os.path.join(app.config['UPLOAD_FOLDER'], "operators.csv")

    # Pull information from MongoDB
    output_csv(uri, db, col, file)

    # Return file to the user.
    return send_file(
            file,
            mimetype='text/csv',
            download_name='output_operators.csv',
            as_attachment=True
        )

def static_download_sys(uri, db, sys, con):
    # Create file paths
    sys_file = os.path.join(app.config['UPLOAD_FOLDER'], "systems.csv")
    con_file = os.path.join(app.config['UPLOAD_FOLDER'], "contacts.csv")
    archive = os.path.join(app.config['UPLOAD_FOLDER'], "systems.zip")

    # Pull information from MongoDB
    output_csv(uri, db, sys, sys_file)
    output_csv(uri, db, con, con_file)

    # Create archive for returning necessary files to the user.
    zipf = zipfile.ZipFile(archive,'w', zipfile.ZIP_DEFLATED)
    zipf.write(sys_file)
    zipf.write(con_file)
    zipf.close()
    return send_file(
            archive,
            download_name='output_systems.zip',
            as_attachment=True
        )

def static_download_cc(uri, db, comm, con):
    # Create file paths
    communities = os.path.join(app.config['UPLOAD_FOLDER'], "communities.csv")
    contacts = os.path.join(app.config['UPLOAD_FOLDER'], "community_contacts.csv")
    archive = os.path.join(app.config['UPLOAD_FOLDER'], "community.zip")
    
    # Pull information from MongoDB
    output_csv(uri, db, comm, communities)
    output_csv(uri, db, con, contacts)

    # Create archive for returning necessary files to the user.
    zipf = zipfile.ZipFile(archive,'w', zipfile.ZIP_DEFLATED)
    zipf.write(communities)
    zipf.write(contacts)
    zipf.close()
    # Create archive for returning necessary files to the user.
    return send_file(
            archive,
            download_name='output_community.zip',
            as_attachment=True
        )

def clean_files():
    """A simple function that removes all files found in the upload folder except for settings.json."""
    try:
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file != 'settings.json':
                path = os.path.join(app.config['UPLOAD_FOLDER'], file)
                print("Removing: ", path)
                os.remove(os.path.join(path)) 
    except Exception as e:
        return "Error thrown will attempting to remove user generated files: " + str(e)

# Clean misc files from upload folder when the server is restarted.
clean_files()

"""
Dynamic Scraper v2
"""
@app.route("/dynamic_v2", methods=['POST', 'GET'])
def run_dynamic_scraper_v2():
    """This function handles the display and operation of the WIP 'dynamic' scraper interface."""
    # If the user hits the submit button, send the information to the server.
    if request.method == 'POST':
        if 'url_submit' in request.form:
            url = request.form['url'].strip()
            if url == '':
                return render_template('dynamic_scraper_v2.html',
                                        error="Please submit a valid url.",
                                        url_needed=True)
            si.base_url = url
            return redirect("/dynamic-v2-add-item")
        if 'add_item' or 'scrape' in request.form:
            return render_template('dynamic_scraper_v2.html',
                                        error="Please submit a valid url before trying to add/scrape items.",
                                        url_needed=True,
                                        json_data = si.instruct_list)
        
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        si.clear()
        return render_template('dynamic_scraper_v2.html', url_needed=True, json_data = si.instruct_list)
    
@app.route("/dynamic-v2-add-item", methods=['POST', 'GET'])
def dynamic_v2_add():
    """Function that adds an instruction to the instruction list."""
    if request.method == 'POST':
        if 'url_submit' in request.form:
            url = request.form['url'].strip()
            if url == '':
                return render_template('dynamic_scraper_v2.html',
                                        error="Please submit a valid url.",
                                        url_needed=True,
                                        json_data = si.instruct_list)
            return render_template('dynamic_scraper_v2.html',
                                items_submitted=True,
                                url_needed=False,
                                url=si.base_url,
                                instructions=si.instructions,
                                json_data = si.instruct_list)
        
        if 'add_item' in request.form:
            # Pull all items from the form
            i = request.form['instruction_select']
            param = request.form['param'].strip()
            tag = request.form['tag'].strip()
            attribute = request.form['attribute'].strip()
            value = request.form['value'].strip()
            function_name = request.form['function_name'].strip()
            params = [param, tag, attribute, value, function_name]
            si.instruct_num += 1

            instruct_name = request.form['instruct_name'].strip()
            if instruct_name == "":
                instruct_name = str(ScraperInstructionType(int(i)))
            notes = request.form['notes']

            # TODO: Update Node logic / bring more in line with the query manager for ease-of-us/updating.
            temp = Node(instruct_name, si.instruct_num)
            curr_node = si.nodes_list[-1]
            if i[0] == '7':
                si.num = math.floor(si.num + 1.0)
                temp.nodes = []
                curr_node.insert_node(temp)
                si.nodes_list.append(temp)
            elif i[0] == '8':
                si.num = math.floor(si.num - 1.0)
                curr_node.insert_node(temp)
                si.nodes_list.pop()
            else:
                si.num = round(si.num + 0.1, 1)
                curr_node.insert_node(temp)

            si.instructions.append((ScraperInstructionType(int(i)).name, params, si.num, instruct_name, notes))
            si.instruct_list = si.head.convert_to_dict()["nodes"]
            
            return render_template('dynamic_scraper_v2.html',
                                items_submitted=True,
                                url_needed=False,
                                url=si.base_url,
                                instructions=si.instructions,
                                json_data = si.instruct_list)
        
        if 'scrape' in request.form:
            return redirect("/dynamic-v2-scrape")
        
        if 'num_submit' in request.form: 
            return dynamic_update_v2(int(request.form['update_num']))
    
    elif si.base_url == '':
        return redirect("/dynamic_v2")

    return render_template('dynamic_scraper_v2.html',
                            items_submitted=True,
                            url_needed=False,
                            url=si.base_url,
                            instructions=si.instructions,
                            json_data = si.instruct_list)

@app.route("/dynamic-v2-scrape", methods=['POST', 'GET'])
def dynamic_v2_scrape():
    """Function that runs the dynamic scraper."""
    if request.method =='POST':
        if 'url_submit' in request.form:
            return redirect("/dynamic-v2-add-item")
        
        if 'download' in request.form:
            return redirect("/dynamic/download")
        
        if 'upload' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            col = request.form['Collection']
            if (uri == '' or db == '' or col == ''):
                flash('MongoDB Connection details were not inputted. Please try again.', 'error')
            else:
                try:
                    return dynamic_upload(uri, db, col)
                except:
                    flash('Error in trying to upload contents to MongoDB. Please make sure inputted connection details are correct.', 'error')
    # Replace False with si.auto once implemented
    else:
        if not si.scraped:
            try:
                result = dynamic_v2(si.base_url, si.instructions)
            except Exception as e:
                flash('An error occurred while attempting to run the dynamic scraper. Currently there is a webdriver issue preventing selenium from running on the server.\n'+str(e), 'error')
                return redirect("/dynamic-v2-add-item")
            if isinstance(result, str):
                    si.scraped = True
                    return render_template('dynamic_scraper.html',
                                    error="Error encountered during scrape: " + result,
                                    url_needed=True)
        
        file = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
        final = json.dumps(result, indent=2)
        output = open(file, "w") 
        json.dump(result, output, indent=2)
        output.close()
        si.clear()
        default_values = display_text_input("Dynamic_Scraper_Upload")

        return render_template('dynamic_scraper_v2_output.html',
                            scrape=True,
                            output=final,
                            default=default_values)
    
    file = os.path.join(app.config['UPLOAD_FOLDER'], "output.json")
    with open(file) as f:
        result = json.load(f)
    final = json.dumps(result, indent=2)
    default_values = display_text_input("Dynamic_Scraper_Upload")
    return render_template('dynamic_scraper_v2_output.html',
                            scrape=True,
                            output=final,
                            default=default_values)

@app.route("/dynamic-v2-delete/<key>")
def dynamic_delete_v2(key):
    """Function that deletes a specific instruction based on the key value."""
    key = int(key)
    instructs = si.instructions
    node_list = si.head.nodes
    i = instructs[key]

    # Option 2: If i[key] == click element, pop each instruction up + including 'go back previous page'
    # Update list to linked list
    if i[0] == ScraperInstructionType(7).name:
        new_instructs = instructs[0:key]
        finished = False
        l = len(instructs)
        for x in range(key, l):
            if finished:
                new_instructs.append(instructs[x])
            else:
                name = instructs[x][0]
                if name == ScraperInstructionType(8).name or finished:
                    finished = True
        si.instructions = new_instructs
    # Else, pop one instruction
    else:
        instructs.pop(key)
    
    # Call function to update tree
    si.head = node.delete_node(si.head, key+1)

    if si.head.nodes:
        si.instruct_list = si.head.convert_to_dict()["nodes"]
    else:
        si.instruct_list = []
    update_list()
    si.instruct_num -= 1
    return redirect("/dynamic-v2-add-item")

def update_list():
    """Helper function that updates the instruction list when a command gets added/removed."""
    instructs = []
    num = 1.0
    for i in si.instructions:
        if i[0] == ScraperInstructionType(7).name:
            num = math.floor(num + 1.0)
        elif i[0] == ScraperInstructionType(8).name:
            num = math.floor(num - 1.0)
        else:
            num = round(num + 0.1, 1)
        instructs.append((i[0], i[1], num, i[3], i[4]))
    si.instructions = instructs
    si.num = num

@app.route('/get-item/<index>', methods=['POST'])
def get_item(index):
    """Function that returns a specific scraper step's values."""
    if request.method == "POST":
        i = int(index)-1 # Front end index starts at 1, not 0
        item = si.instructions[i]
        name = item[0]
        params = item[1]
        num = item[2]
        instruct_name = item[3]
        notes = item[4]

        response = f'''<div id=details>'''
        response += f'''<h4>{instruct_name}</h4>''' 
        response += f'''<ul id="selected_item" name={i}>'''
        response += f'''<li>Name: {name}</li>''' 
        response += f'''<li>Parameters: {params}</li>''' 
        response += f'''<li>Number: {num}</li>''' 
        response += f'''<li>Notes: {notes}</li>''' 
        response += '''</div>'''
        return response

@app.route("/dynamic-v2-update/<key>", methods=['POST','GET'])
def dynamic_update_v2(key):
    """Function that allows the user to update a specific scraper step."""
    key = int(key)
    # If the user submits an update request, update the item.
    if 'update_item' in request.form:
        si.instructions.pop(key)
        i = request.form['instruction_select']
        num = request.form['num']
        param = request.form['param'].strip()
        tag = request.form['tag'].strip()
        attribute = request.form['attribute'].strip()
        value = request.form['value'].strip()
        function_name = request.form['function_name'].strip()
        params = [param, tag, attribute, value, function_name]
        instruct_name = request.form['instruct_name'].strip()
        notes = request.form['notes']
        if instruct_name == "":
            instruct_name == ScraperInstructionType(int(i)).name
        si.instructions.insert(key, (ScraperInstructionType(int(i)).name, params, num, instruct_name, notes))
        update_node(key+1, instruct_name, si.head.nodes)
        si.instruct_list = si.head.convert_to_dict()["nodes"]
        return redirect("/dynamic-v2-add-item")
    
    # Otherwise, find the item the user is requesting to delete and display it.
    i = si.instructions[key]
    instruct = i[0]
    params = i[1]
    num = i[2]
    name = i[3]
    notes = i[4]
    return render_template('dynamic_update_v2.html',
                           instruct=instruct,
                           params=params,
                           num=num,
                           instruct_name = name,
                           notes=notes)

def update_node(key, text, node_list):
    """Function to update the node as things change/update in the instruction list."""
    for n in node_list:
        if n.index == key:
            n.text = text
            break
        if n.nodes:
            update_node(key, text, n.nodes)

@app.route("/dynamic-v2/<key>")
def view_instruction(key):
    """Function to view a specific instruction on the webpage. It will run the scraper until it reaches the given instruction."""
    instructs = si.instructions[0:int(key)+1]
    # Load all of the instructions into Selenium
    # Run scraper up until given instruction
    url = get_url(si.base_url, instructs)
    return url

@app.route("/dynamic-v2-popup/<int:key>", methods=['POST','GET'])
def instruction_info(key):
    """Function to return information on an instruction."""
    i = si.instructions[key]
    return render_template('popup_info.html',
                           info=[i[3], i[1][0], i[4]])

"""
File Upload and Query Manager Functions
"""
def add_template(name, filename, notes, rows, cols, header):
    """Helper function to create a new user defined template for the file upload / query manager features."""
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    with open(file_temp, 'r') as f:
        temp = json.load(f)
    index = len(temp)
    template = {"Index": str(index), "Name": name, "Filename": filename, "Header": header, "Rows": rows, "Columns": cols, "Notes": notes, "Queries": []}
    temp.append(template)
    with open(file_temp, 'w') as f:
        json.dump(temp, f, indent=4)
    flash(f'Template {template["Name"]} has been added.', 'success')

def update_template(template, index=None):
    """Helper function to update a user defined template for the file upload / query manager features."""
    if not index:
        index = template["Index"]
        # If new and empty template, report an error.
        if index == "":
            flash('Attempted to update an empty template.', 'error')
            return ""
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    with open(file_temp, 'r') as f:
        temp = json.load(f)
    for t in temp:
        if t["Index"] == index:
            t["Rows"] = template["Rows"]
            t["Columns"] = template["Columns"]
            t["Notes"] = template["Notes"]
            if t["Filename"] != template['Filename']:
                old_file = os.path.join(app.config['TEMPLATE_FOLDER'], t["Filename"])
                new_file = os.path.join(app.config['TEMPLATE_FOLDER'], template["Filename"])
                os.rename(old_file, new_file)
                t["Filename"] = template["Filename"]
            t["Header"] = template["Header"]
            t["Name"] = template["Name"]
            break
    with open(file_temp, 'w') as f:
        json.dump(temp, f, indent=4)
    
    flash(f'Template {template["Name"]} has been updated.', 'success')
    return temp

def delete_template(index, temp):
    """Helper function to delete a specific user defined template."""
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    # If the template is empty, report an error
    if (index == "" or temp == ""):
        flash("No template selected for delete.", 'error')
        return ""
    # Loop through template file for specific template index. 
    for x in range(0, len(temp)):
        if temp[x]["Index"] == index:
            filename = temp[x]["Filename"]
            name = temp[x]["Name"]
            os.remove(os.path.join(app.config['TEMPLATE_FOLDER'], filename))
            temp.remove(temp[x])
            break

    # Update template indexing
    for x in range(0, len(temp)):
        temp[x]["Index"] = str(x)

    with open(file_temp, 'w') as f:
        json.dump(temp, f, indent=4)
    
    flash(f"Template {name} with file {filename} has been delete.", 'success')
    return temp
    
@app.route('/get-template-info/<index>', methods=['POST'])
def get_template_info(index):
    """Function used by an ajax call to retrieve template information."""
    if request.method == "POST":
        name, file_name, notes = "", "", ""
        response = [""] * 6
        file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
        with open(file_temp) as f:
            temp = json.load(f)
        
        # Loop through the file contents to find the specific template.
        for t in temp:
            if index == t["Index"]:
                template = t
                name = template["Name"]
                file_name = template["Filename"]
                notes = template["Notes"]
                rows = template["Rows"]
                columns = template["Columns"]
                header = template["Header"]
                response = [name, file_name, header, rows, columns, notes]
                break
        return jsonify(response=response)

@app.route('/reset')
def reset_upload():
    file_upload.clear()
    return redirect("/upload_csv")

def create_upload_dict():
    file_upload.form_dict = {}
    file_upload.form_dict["template"] = "unsure"

@app.route("/upload_csv", methods=['POST','GET'])
def upload_csv():
    """Main page for uploading a csv/excel file and creating templates."""
    if not file_upload.form_dict or file_upload.form_dict == "":
        create_upload_dict()
    
    # Load template file
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    with open(file_temp) as f:
        temp = json.load(f)

    if request.method =='POST':
        if 'submit_csv' not in request.form and 'create_template' not in request.form:
            btn = list(request.form.keys())[-1]

            # Update a specific template based on the provided index and user input.
            if 'update_template' in btn:
                index = btn.strip('update_template_')
                temp_name = request.form['temp_name'].strip()
                temp_filename = request.form['temp_filename'].strip()
                temp_notes = request.form['temp_notes']
                temp_rows = request.form['temp_rows'].strip()
                temp_cols = request.form['temp_cols'].strip()
                temp_header = request.form['temp_header'].lower()
                if temp_header != 'yes' and temp_header != 'no':
                    temp_header = 'unsure'
                template = {"Index": index, "Name": temp_name, "Filename": temp_filename,
                            "Header": temp_header, "Rows": temp_rows, "Columns": temp_cols, "Notes": temp_notes, "Queries": []}
                temp = update_template(template, index)
            
            # Delete a specified template.
            elif 'delete_template' in btn:
                index = btn.strip('delete_template_')
                temp = delete_template(index, temp)
            return render_template("upload_csv.html", templates=temp, form_dict = file_upload.form_dict, compare=file_upload.compared)
        
        else:
            # Uploading a file
            try:
                file = request.files['file']

                # Check to make sure the file exists and save it.
                if file.filename == '':
                    flash('No selected file.', 'error')
                    return redirect("upload_csv")
                if file:
                    try:
                        filename = secure_filename(file.filename)
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(filepath)
                    except:
                        flash('Failed to save file. Please try again.', 'error')
            except:

                try:
                    if file_upload.form_dict["filename"]:
                        filename = file_upload.form_dict["filename"]
                        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                except:
                    flash('Failed to open file. Please reset form.', 'error')
                    return redirect("upload_csv")
            
            # Determine header
            try:
                header_option = request.form['header']
                file_upload.form_dict["header"] = header_option 
                need_cols = False
                if header_option == "yes":
                    header = 0

                # If no or unsure, assume no header
                else:
                    header = None
                    need_cols = True

                # Determine is user is uploading CSV or EXCEL
                if request.form.get('check_excel'):
                    file_upload.df = pd.read_excel(filepath, header=header)
                    file_upload.form_dict["excel"] = True
                else:
                    file_upload.df = pd.read_csv(filepath, header=header)
                    file_upload.form_dict["excel"] = False
                file_upload.form_dict["filename"] = filename
            except Exception as e:
                flash("Failed to read file properly. Please ensure that the format is correct. The given error is: " + str(e), 'error')
                return render_template("upload_csv.html", templates=temp, form_dict = file_upload.form_dict, compare=file_upload.compared)
            
            if need_cols:
                file_upload.df.columns = [f'Column_{n+1}' for n in range(file_upload.df.shape[1])]

            # Remove special characters from df column names
            file_upload.df = clean_columns(file_upload.df)

            # Save a copy of the original dataframe/file incase the user edits it.
            file_upload.og_df = file_upload.df.copy(deep=True)
            file_csv = os.path.join(app.config['UPLOAD_FOLDER'], "output_table.json")
            final = file_upload.df.to_json(file_csv, orient='records')

            if 'submit_csv' in request.form:
                if request.form.get('temp_checkbox'):
                    template = request.form['template_select']
                    if template not in ('Template Format', 'No Template'):
                        # Locate non-default template.
                        for t in temp:
                            if t["Index"] == template:
                                file_upload.template = t
                                file_upload.form_dict["template"] = t
                                file_upload.form_dict["compare"] = "yes"
                                break
                        # file_upload.template = temp[template]
                        file_upload.compared = True
                        return redirect("display_csv")
                file_upload.form_dict["compare"] = "no"
                return redirect("csv_mongodb")
            
            elif 'create_template' in request.form:
                return redirect(url_for("create_template", filename=filename, header=header_option))
    return render_template("upload_csv.html", templates=temp, form_dict = file_upload.form_dict, compare=file_upload.compared)

@app.route("/create_template/<filename>&<header>", methods=['POST','GET'])
def create_template(filename, header):
    """Helper function to create a user defined template for the file upload / query manager features."""
    name, extension = os.path.splitext(filename)
    if request.method == 'POST':
        temp_name = request.form['temp_name'].strip()
        temp_filename = request.form['temp_filename'].strip()
        temp_notes = request.form['temp_notes']
        temp_rows = request.form['temp_rows'].strip()
        temp_cols = request.form['temp_cols'].strip()
        temp_header = request.form['temp_header']
        if temp_header == '':
            temp_header = 'unsure'
        try:
            # Move the file to the template directory
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.rename(filepath, os.path.join(app.config['TEMPLATE_FOLDER'], temp_filename+extension))
        except OSError:
            # If the file already exists there, raise an error to the user.
            flash("A file with this name already has a template associated with it.", 'error')
            return render_template("create_template.html", filename=temp_name, extension=extension, header_opt=header)
        add_template(temp_name, temp_filename+extension, temp_notes, temp_rows, temp_cols, temp_header)
        # Redirect to next step. There is no file to compare to with this upload, so we continue as normal.
        return redirect(url_for("csv_mongodb"),code=307)
    return render_template("create_template.html", filename=name, extension=extension, header_opt=header)

def clean_columns(df):
    """Helper function to clean up column names of special characters."""
    df.columns = [re.sub("[ ,-]", "_", re.sub("[\.,`,\$,\n]", "", c)) for c in df.columns]
    df.columns = df.columns.str.strip()
    return df

@app.route("/csv_mongodb", methods=['POST','GET'])
def csv_mongodb():
    """Display contents of uploaded file to user without an attached template."""
    # Redirect to the first step if no file is found.
    if file_upload.df is None:
        flash("Uploaded file not found. Please upload a file.", 'error')
        return redirect("/upload_csv")
    
    if request.method =='POST':
        # Enable the user to download the table in multiple different file types.
        if 'download_table' in request.form:
            dl_type = request.form['download_type']
            if dl_type == 'JSON':
                dl_name = 'output_table.json'
                file = os.path.join(app.config['UPLOAD_FOLDER'], dl_name)
                file_upload.df.to_json(file, orient='records')
                mtype = 'text/csv'

            elif dl_type == 'CSV':
                dl_name = 'output_table.csv'
                file = os.path.join(app.config['UPLOAD_FOLDER'], dl_name)
                file_upload.df.to_csv(file)
                mtype = 'text/csv'

            elif dl_type == 'Excel':
                dl_name = 'output_table.xlsx'
                file = os.path.join(app.config['UPLOAD_FOLDER'], dl_name)
                file_upload.df.to_excel(file)
                mtype = 'application/vnd.ms-excel'

            return send_file(
                file,
                mimetype=mtype,
                download_name=dl_name,
                as_attachment=True
            )
        
        # Generate MongoDB connection based on user input
        if 'upload' in request.form:
            file_upload.mongo_uri = request.form['Connection']
            file_upload.mongo_db = request.form['Database']
            file_upload.mongo_col = request.form['Collection']

            # Setup MongoDB connection
            mongoClient = MongoClient(file_upload.mongo_uri)
            db = mongoClient[file_upload.mongo_db]
            col = db[file_upload.mongo_col]

            # Set up Query Manager mongodb connection
            qm.set_mongodb(file_upload.mongo_uri, file_upload.mongo_col, file_upload.mongo_uri)

            # Open, load, and insert file contents to MongoDB
            file = os.path.join(app.config['UPLOAD_FOLDER'], "output_table.json")
            with open(file) as f:
                data = json.load(f)
            col.insert_many(data)
            flash(f'File has been uploaded to MongoDB.', 'success')
            return redirect("query_manager")

        # Update table based on user input
        if 'update_table' in request.form:
            usecols = request.form['usecols']
            skiprows = request.form['skiprows']
            toggle = request.form["visualize_rowcol"]
            try:
                display, rows, cols = highlight_edits(skiprows, usecols, toggle)
                return render_template("csv_mongodb.html", tables=display, row=rows, col=cols)
            except:
                flash("Issue with highlighting the table. Please double check the row/col format.", 'error')

    
    # Style table based on user input
    styler = file_upload.df.style.map(color_isnull)
    styler.set_table_attributes("class='table table-bordered'")
    uploaded_table = styler.to_html(header="true", table_uuid='uploaded_file')

    # Display file_upload.df as table in html
    return render_template("csv_mongodb.html", tables=[uploaded_table])

def update_row_col_str(row, col):
    """Helper function to convert user input (excel format) of row / column selection into something usable for pandas dataframes."""
    cols, rows = [], []
    # Determine if user wishes to skip any columns
    if col == '':
        cols = None
    else:
        col = col.split(";")
        for c in col:
            if ':' in c:
                r = c.split(':')
                for i in range(int(r[0])-1, int(r[1])-1):
                    cols.append(i)
            else:
                cols.append(int(c)-1)
    
    # Determine if user wishes to skip any rows
    if row == '':
        rows = None
    else:
        row = row.split(";")
        for c in row:
            if ':' in c:
                r = c.split(':')
                for i in range(int(r[0])-1, int(r[1])-1):
                    rows.append(i)
            else:
                rows.append(int(c)-1)
    return rows, cols

def highlight_edits(row, col, toggle):
    """Helper function for highlighting specific columns/rows."""
    # Determine user specified columns
    rowstr = row
    colstr = col
    rows, cols = update_row_col_str(row, col)
    
    # Update DF displayed on front-end
    if toggle == '1':
        file_upload.df = file_upload.og_df.copy(deep=True)
        if cols:
            file_upload.df.drop(file_upload.df.columns[cols], axis=1, inplace=True)
        if rows:
            file_upload.df.drop(index=rows, inplace=True)
        return [file_upload.df.to_html(classes='table table-bordered', header="true", table_id="uploaded_file")], rowstr, colstr

    # https://getbootstrap.com/docs/5.0/content/tables/
    # <tr class='table-primary'></tr>
    elif toggle == '2':
        file_upload.df = file_upload.og_df.copy(deep=True)
        styler = file_upload.df.style
        if cols:
            styler.set_properties(subset=file_upload.df.columns[cols].tolist(), **{"background-color": "lightblue"})
        if rows:
            styler.applymap(lambda _: "background-color: lightblue", subset=(file_upload.df.index[rows],))
        styler.set_table_attributes("class='table table-bordered'")
        return [styler.to_html(classes='table table-bordered', header="true", table_uuid="uploaded_file")], rowstr, colstr

    # Return file_upload.df to original dataset
    elif toggle == '3':
        file_upload.df = file_upload.og_df.copy(deep=True)
        return [file_upload.df.to_html(classes='table table-bordered', header="true", table_id="uploaded_file")], rowstr, colstr

    elif toggle=='4':
        file_upload.template["Rows"] = rowstr
        file_upload.template["Columns"] = colstr
        temp = update_template(file_upload.template)
        return [file_upload.df.to_html(classes='table table-bordered', header="true", table_id="uploaded_file")], rowstr, colstr

@app.route("/display_csv", methods=['POST','GET'])
def display_csv():
    """Page to display the contents of the uploaded file if a user also selects a template."""
    if file_upload.df is None:
        flash("Uploaded file not found. Please upload a file.", 'error')
        return redirect("/upload_csv")
    
    # Allow the user to download the table in a specific file type.
    if request.method =='POST':
        if 'download_table' in request.form:
            dl_type = request.form['download_type']
            if dl_type == 'JSON':
                dl_name = 'output_table.json'
                file = os.path.join(app.config['UPLOAD_FOLDER'], dl_name)
                file_upload.df.to_json(file, orient='records')
                mtype = 'text/csv'

            elif dl_type == 'CSV':
                dl_name = 'output_table.csv'
                file = os.path.join(app.config['UPLOAD_FOLDER'], dl_name)
                file_upload.df.to_csv(file)
                mtype = 'text/csv'

            elif dl_type == 'Excel':
                dl_name = 'output_table.xlsx'
                file = os.path.join(app.config['UPLOAD_FOLDER'], dl_name)
                file_upload.df.to_excel(file)
                mtype = 'application/vnd.ms-excel'

            return send_file(
                file,
                mimetype=mtype,
                download_name=dl_name,
                as_attachment=True
            )
        
        # Redirect the user to the next step.
        if 'upload' in request.form:
            file_upload.form_dict["columns"] = ""
            return redirect("/comparison_setup")

        # Allow the user to update the styling of the table
        if 'update_table' in request.form:
            usecols = request.form['usecols']
            skiprows = request.form['skiprows']
            toggle = request.form["visualize_rowcol"]
            try:
                display, rows, cols = highlight_edits(skiprows, usecols, toggle)
                return render_template("display_csv.html", tables=display, row=rows, col=cols)
            except:
                flash("Issue with highlighting the table. Please double check the row/col format.", 'error')

        # Logic for if the user chooses to update the template
        if 'update_template' in request.form:
            usecols = request.form['usecols']
            skiprows = request.form['skiprows']
            file_upload.template["Rows"] = skiprows
            file_upload.template["Columns"] = usecols
            temp = update_template(file_upload.template)
    
    # Display file_upload.df as table in html
    rows = file_upload.template["Rows"]
    cols = file_upload.template["Columns"]
    return render_template("display_csv.html", tables=[file_upload.df.to_html(classes='table table-bordered', header="true", table_id="uploaded_file")], row=rows, col=cols)

def compare_dataframes(data, other, index):
    """Helper function that returns highlighted dataframes to showcase changes between the files."""
    merged_df = other.merge(data, indicator=True, how='outer')
    changed_rows_df = merged_df[merged_df['_merge'] == 'right_only']
    filtered = changed_rows_df.drop('_merge', axis=1)

    # Set indexes equal to user specified index
    data = data.set_index(file_upload.indexes[0])
    filtered = filtered.set_index(file_upload.indexes[0])
    other = other.set_index(file_upload.indexes[1])

    # Determine new rows
    rows = list(set(list(data.index.values))-set(list(other.index.values)))
    new_rows = data[data.index.isin(rows)]

    # Determine new columns
    new_cols = list(set(list(data.columns))-set(list(other.columns)))
    # If column exists in new_cols, it should maintain its 'new column' highlighting vs 'unmatched' highlighting
    file_upload.cols1 = list(set(file_upload.cols1) - set(new_cols))

    # Filter new rows out of the filtered df
    filtered = filtered[~filtered.index.isin(rows)]

    return data.loc[filtered.index], new_rows, new_cols

def color_diff(s, data, other):
    """Helper function that highlights all differences in the dataframe."""
    color = 'LightCoral'
    attr = 'background-color: %s' % color

    # Create a slice from the original dataframe that matches the filtered (changed) dataframe
    compare_slice = other[other.index.isin(list(data.index.values))]
    common_cols = [col for col in set(data.columns).intersection(other.columns)]
    other_compare = compare_slice[common_cols]
    data_compare = data[common_cols]

    # Return a dataframe that specifically colors any changes between old and new
    return pd.DataFrame(np.where(data_compare.ne(other_compare, level=0), attr, ''),
                        index=data.index, columns=common_cols)

def color_isnull(s):
    """Helper function that highlights all null values in the dataframe."""
    if not pd.notna(s):
        color = 'LightGreen'
        return 'background-color: %s' % color
    else:
        return ''

def color_col(s):
    """Helper function that highlights new columns in the dataframe."""
    color = 'Plum'
    return 'background-color: %s' % color

def color_row(s):
    """Helper function that highlights new rows in the dataframe."""
    color = 'SandyBrown'
    return 'background-color: %s' % color

def color_noncompare(s):
    """Any columns not being compared are highlighted light blue."""
    color = 'LightBlue'
    return 'background-color: %s' % color

@app.route("/comparison_setup", methods=["POST", "GET"])
def comparison_setup():
    """Webpage that handles the column comparison selection."""
    if file_upload.df is None:
        flash("Uploaded file not found. Please upload a file.", 'error')
        return redirect("/upload_csv")
    if not file_upload.template:
        flash("No template selected. Please upload the file and select a template.", 'error')
        return redirect("/upload_csv")

    if request.method == 'POST':
        # Set indexes for each dataframe
        if 'set_index' in request.form:
            # Retrieve the index from the user.
            df1_index = request.form["index"]
            # Set the global index for later assignment
            file_upload.indexes = df1_index
            # Alert the user to their choice
            flash(f'Index set to {df1_index}', 'success')

        # Continue to next step
        if 'continue' in request.form:
            # Loop through the form and extract every drop down match
            if file_upload.indexes == "":
                flash('Set an index before continuing.', 'error')
                return render_template("comparison_setup.html", original_columns=file_upload.cols2, uploaded_columns=file_upload.cols1, matched_columns=file_upload.compare_cols, indexes=file_upload.indexes, form_dict=file_upload.form_dict)
            else:
                file_upload.compare_cols = []
                columns = {}
                for f in request.form:
                    # If 'continue' is found, we've reached the end of the form and exit
                    if 'continue' in f:
                        break
                    # If the user has designated a column as one that should not be compared, it should be highlighted as such.
                    # Otherwise, match the column names.
                    if 'no_compare' not in request.form[f]:
                        if f in file_upload.cols1:
                            file_upload.cols1.remove(f)
                            file_upload.compare_cols.append((f, request.form[f]))
                            columns[f] = request.form[f]
                        else:
                            flash("""An error occurred while matching columns for comparison. Make sure that the column selected as the index 
                            does not match with any other columns. Also, ensure that each column only matches with each other / a column that is 
                            able to be compared!""", 'error')
                            return redirect("comparison_setup")
                file_upload.form_dict["columns"] = columns
                file_upload.form_dict["Compared"] = False
                return redirect("/compare_csv")

    else:
        # Load the file saved for the template.
        if os.path.exists(os.path.join(app.config['TEMPLATE_FOLDER'], file_upload.template["Filename"])):
            file_upload.df1 = file_upload.df.copy(deep=True)
            header = file_upload.template["Header"]
            if header == "yes":
                header = 0
                file_upload.header2 = True
            else:
                header = None
                file_upload.header2 = False
            try:
                if file_upload.form_dict["excel"]:
                    file_upload.df2 = pd.read_excel(os.path.join(app.config['TEMPLATE_FOLDER'], file_upload.template["Filename"]), header=header)
                else:
                    file_upload.df2 = pd.read_csv(os.path.join(app.config['TEMPLATE_FOLDER'], file_upload.template["Filename"]), header=header)
                if file_upload.header2:
                    file_upload.df2 = clean_columns(file_upload.df2)
            except:
                flash("Unable to locate file saved to template. Please try again or recreate the template.", 'error')
                return redirect("comparison_setup")

            # Save the columns for the future.
            file_upload.cols1 = list(file_upload.df1.columns)
            file_upload.cols2 = list(file_upload.df2.columns)
            
    return render_template("comparison_setup.html", original_columns=file_upload.cols2, uploaded_columns=file_upload.cols1, matched_columns=file_upload.compare_cols, indexes=file_upload.indexes, form_dict=file_upload.form_dict, test=json.dumps(file_upload.cols1))

@app.route("/compare_csv", methods=['POST', 'GET'])
def compare_csv():
    """Webpage that displays the compared tables. This will highlight any differences on the new table in a specific order.
        1. is null
        2. different values
        3. new rows
        4. new columns
        5. not compared"""
    if file_upload.df is None:
        flash("Uploaded file not found. Please upload a file.", 'error')
        return redirect("/upload_csv")
    
    # Generate MongoDB connection based on user input
    if 'upload' in request.form:
        file_upload.mongo_uri = request.form['Connection']
        file_upload.mongo_db = request.form['Database']
        file_upload.mongo_col = request.form['Collection']
        mongoClient = MongoClient(file_upload.mongo_uri)
        db = mongoClient[file_upload.mongo_db]
        col = db[file_upload.mongo_col]

        # Generate mongodb information for query manager.
        qm.set_mongodb(file_upload.mongo_uri, file_upload.mongo_col, file_upload.mongo_uri)

        # Upload file to mongodb
        file = os.path.join(app.config['UPLOAD_FOLDER'], "output_table.json")
        with open(file) as f:
            data = json.load(f)
        col.insert_many(data)
        return redirect("/query_manager")
    else:
        if file_upload.form_dict:
            if file_upload.form_dict["Compared"] == False:
                if os.path.exists(os.path.join(app.config['TEMPLATE_FOLDER'], file_upload.template["Filename"])):
                    if file_upload.indexes not in file_upload.df2.columns.tolist() and file_upload.indexes[1] not in file_upload.df2.columns.tolist():
                        flash("An issue occurred with the index. Please resubmit the index to a column with unique items.", 'error')
                        file_upload.indexes = ""
                        return redirect("comparison_setup")
                    
                    header1 = []
                    header2 = []
                    h1, h2 = [], []
                    col_num=0
                    
                    # Make sure the indexes are the same and other cols dont match the index
                    for r in file_upload.compare_cols:
                        if r[0] == file_upload.indexes or r[0] == file_upload.indexes[0]:
                            file_upload.indexes = (r[0], r[0])
                        else:
                            h1.append(r[0]) # df1 col matches
                            h2.append(r[1]) # df2 col matches
                            header1.append(f"Column {col_num}")
                            header2.append(f"Column {col_num}")
                            col_num +=1
                
                    # Collect any column names that are not being compared.
                    non_compared1 = set(file_upload.df1.columns.values.tolist()) - set(h1)
                    non_compared2 = set(file_upload.df1.columns.values.tolist()) - set(h2)
                    
                    non_compared1 = list(non_compared1)
                    non_compared2 = list(non_compared2)

                    if file_upload.indexes[1] in non_compared2:
                        non_compared1.remove(file_upload.indexes[0])
                    if file_upload.indexes[1] in non_compared2:
                        non_compared2.remove(file_upload.indexes[1])
                    
                    # Assign temp col names to dataframes for comparison
                    col_rename_dict1 = {i:j for i,j in zip(h2,header2)}
                    file_upload.df1.rename(columns=col_rename_dict1, inplace=True)
                    col_rename_dict2 = {i:j for i,j in zip(h1,header1)}
                    file_upload.df2.rename(columns=col_rename_dict2, inplace=True)

                    for c in non_compared1:
                        h1.append(c)
                        header1.append(c)

                    for c in non_compared2:
                        h2.append(c)
                        header2.append(c)

                    # Create mappers to rename columns after comparison
                    original_col_dict1 = {i:j for i,j in zip(header2,h2)}
                    original_col_dict2 = {i:j for i,j in zip(header1,h1)}
                    
                    # Set indexes for dataframes
                    try:
                        compare=True
                        diff, new_rows, new_cols = compare_dataframes(file_upload.df1, file_upload.df2, file_upload.indexes)
                        file_upload.df1 = file_upload.df1.set_index(file_upload.indexes[0])
                        file_upload.df2 = file_upload.df2.set_index(file_upload.indexes[1])
                        
                        # Apply color changes to the new df / df1
                        styler = file_upload.df1.style.map(color_isnull) \
                        .apply(color_diff, axis=None, data=diff, other=file_upload.df2) \
                        .apply(lambda x: new_rows.map(color_row), axis=None) \
                        .map(color_col, subset=pd.IndexSlice[:, new_cols]) \
                        .map(color_noncompare, subset=pd.IndexSlice[:, file_upload.cols1]) \
                        .format_index(original_col_dict1.get, axis=1) \
                        .set_table_attributes("class='table table-bordered'")

                        # Apply minor styling to original df / df2
                        styler2 = file_upload.df2.style.format_index(original_col_dict2.get, axis=1) \
                        .set_table_attributes("class='table table-bordered'")

                        # Generate html string for both files
                        file_upload.form_dict["uploaded_table"] = styler.to_html(header="true", table_uuid='uploaded_file')
                        file_upload.form_dict["saved_table"] = styler2.to_html(header="true", table_uuid='saved_file')
                        file_upload.form_dict["Compared"] = True
                    except:
                        flash("""An error occurred while trying to style/color the compared tables. Please make sure that each column is only compared 
                        once and that the index column is matching itself (e.g., Community and Community).""", 'error')
                        return redirect('comparison_setup')
                else:
                    # This shouldn't be possible. If we reach this point we should redirect back to display_csv 
                    # with a flash error saying that the template file doesn't exist / couldn't be found.
                    flash('The file saved to the template could not be found. You may need to recreate this template.', 'error')
                    saved_table = ""
                    uploaded_table = file_upload.df.to_html(classes='table table-bordered', header="true")
                    compare=False
                return render_template("compare_csv.html", uploaded_table=[file_upload.form_dict["uploaded_table"]], saved_table=[file_upload.form_dict["saved_table"]], compare=compare)
            else:
                return render_template("compare_csv.html", uploaded_table=[file_upload.form_dict["uploaded_table"]], saved_table=[file_upload.form_dict["saved_table"]], compare=True)
        else:
            return redirect("/comparison_setup")

@app.route("/query_manager/query_info/<query_name>",  methods=['POST'])
def get_query_info(query_name):
    """Function that returns a specific saved query."""
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    with open(file_temp) as f:
        temp = json.load(f)
    data = temp[1]
    queries = data['Queries']
    for q in queries:
        if q['Query'] == query_name:
            return [q['Query'], q['Pipeline']]
        
@app.route("/query_manager/query_jsarray/<query_name>",  methods=['POST'])
def get_jsarray(query_name):
    """Function that returns the html information/jsarray saved to a specific query."""
    if query_name != 'No Query':
        data = file_upload.template
        queries = data['Queries']
        for q in queries:
            if q['Query'] == query_name:
                return [query_name, q['JSArray'], q['Div']]
    return []
        
@app.route("/query_manager/command_info/<command>",  methods=['POST'])
def get_command_info(command):
    """Function to return information relating to a specific command."""
    info = qm.queries[command].replace("\n", "")
    syntax = qm.syntaxes[command]
    return [info, syntax]

@app.route("/query_manager/command_infoBtn/<command>",  methods=['POST'])
def get_command_infoBtn(command):
    """Function to return information relating to a specific gui command."""
    cmd = command.split("_")
    info = qm.queries[cmd[0]].replace("\n", "")
    syntax = qm.syntaxes[cmd[0]]
    return [info, syntax]

@app.route("/query_manager/run_query_order/<query_list>",  methods=['POST'])
def run_query_order(query_list):
    """Function that enables the user to submit a list of queries to run in order."""
    if query_list and file_upload.template:
        try:
            query_list = json.loads(query_list)
            current_query = ""
            for query in query_list:
                current_query = query
                # For each query found in the list, run the saved pipeline.
                for q in file_upload.template["Queries"]:
                    if q["Query"] == query:
                        qm.aggre_pipeline(q["Pipeline"])
            return "Pipeline successful."
        except Exception as e:
            print(e)
            return "An error occurred while running "+ current_query + ". Stopping pipeline."
    else:
        return "No queries in list."

@app.route("/query_manager/delete_query/<query>",  methods=['POST'])
def delete_query(query):
    for x in range(0, len(file_upload.template["Queries"])):
        q = file_upload.template["Queries"][x]
        if q["Query"] == query:
            file_upload.template["Queries"].remove(q)
            break
    
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    with open(file_temp) as f:
        temp = json.load(f)

    for t in temp:
        if t["Name"] == file_upload.template["Name"]:
            t["Queries"] = file_upload.template["Queries"]

    with open(file_temp, 'w') as f:
        json.dump(temp, f, indent=4)

    return query


@app.route("/query_manager", methods=['POST', 'GET'])
def query_manager():
    """Webpage that handles the query_manager."""

    # Get template information
    file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
    with open(file_temp) as f:
        temp = json.load(f)
    
    if file_upload.template:
        name = file_upload.template["Name"]
        queries = file_upload.template["Queries"]
    else:
        queries = []
        name = "No Template"
    data = file_upload.template
    queries = []
    if data:
        queries = data['Queries']
    
    # Allow the user to select a template.
    if 'select_template' in request.form:
        index = request.form['template_select']
        if index == 'No Template':
            file_upload.template = ""
            queries = []
            name = 'No Template'
        else:
            for t in temp:
                if t["Index"] == index:
                    if t["Name"] == 'Template Format':
                        file_upload.template = t
                        queries = []
                        name = file_upload.template["Name"]
                        break
                    else:
                        file_upload.template = t
                        name = file_upload.template["Name"]
                        if file_upload.template["Queries"]:
                            queries = file_upload.template["Queries"]
    
    # Set the mongodb information for the query manager.
    elif 'set_mongodb_info' in request.form:
        file_upload.mongo_uri = request.form['Connection']
        file_upload.mongo_db = request.form['Database']
        file_upload.mongo_col = request.form['Collection']
        qm.set_mongodb(file_upload.mongo_db, file_upload.mongo_col, file_upload.mongo_uri)

    info = [file_upload.mongo_uri, file_upload.mongo_db , file_upload.mongo_col]
    return render_template("query_manager.html", query_list=queries, commands=qm.queries, templates=temp, template_name=name, mongodb_info=info, compared=file_upload.compared)

@app.route('/query_manager/submit', methods=['GET', 'POST'])
def submit_gui_query():
    """Function that enables the submission of queries from the gui."""
    if request.method == 'POST':
        result = request.json
        try:
            # Attempt to create a query pipeline based on user input.
            pipeline, query_name = qm.accept_json(result[0])
            if query_name == "":
                msg = 'Please name your query and try again.'
                return [msg]
            if pipeline:
                # Attempt to submit the pipeline to mongodb.
                response = qm.aggre_pipeline(pipeline)
        except Exception as e:
            msg = 'An error occurred with the query. Please review submission and try again.\n' + str(e)
            return [msg]

        msg = 'Query successfully submitted.'
        if file_upload.template:
            # add query to query_list
            file_temp = os.path.join(app.config['TEMPLATE_FOLDER'], "templates.json")
            with open(file_temp) as f:
                temp = json.load(f)
            name = file_upload.template["Name"]
            if name != 'Template Format':
                for t in temp:
                    if t["Name"] == name:
                        file_upload.template = t
                        queries = t["Queries"]
                        queries.append({"Query": query_name, "Pipeline": pipeline, "JSArray": json.loads(result[0]), "Div": result[1]})
                with open(file_temp, 'w') as f:
                    json.dump(temp, f, indent=4)
        return [msg]
    return redirect('/query_manager')

@app.route("/csv_download")
def csv_download():
    file = os.path.join(app.config['UPLOAD_FOLDER'], "output_table.json")
    return send_file(
            file,
            mimetype='text/csv',
            download_name='output_table.json',
            as_attachment=True
        )
@app.route("/scraper_ui")
def scraper_ui():
    return render_template("scraper_ui.html")

if __name__ == "__main__":
    app.run(debug=True)