from flask import Flask, render_template, request, redirect, send_file
import subprocess, os, json, zipfile, pymongo
import pandas as pd
from scripts.community_profiles import main
from scripts.initial_scrape import main as init_scrape
from dynamic_v2.Extract import main as dynamic_v2
from dynamic_v2.view_instruction import main as get_url


# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = './files'

class ScrapeItems():
    def __init__(self):
        self.scrape_items = {}
        self.url = ""
        self.base_url = ""
        self.args = []
        self.url_count = 0
        self.instructions = []
        self.jsp = False

    def clear(self):
        self.scrape_items = {}
        self.url, self.base_url = "", ""
        self.args = []
        self.url_count = 0
        self.jsp = False
        self.instructions = []

si = ScrapeItems()

def output_csv(uri, db, col, file):
    """A simple function that pulls a collection from MongoDB without the index and stores it into the specified file."""
    client = pymongo.MongoClient(uri)
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

    if s == 'Operators' or 'Systems' or 'Community_Profiles':
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

"""App Routing Functions"""
@app.route("/", methods=['POST', 'GET'])
def index():
    """This function handles the display of the main page and redirects the user to the proper webpage."""
    if request.method == 'POST':
        if 'select_task' in request.form:
            if request.form['SelectTask'] == 'static_scrapers':
                return redirect("/scrapers")
            elif request.form['SelectTask'] == 'dynamic_v2':
                return redirect("/dynamic_v2")
            else:
                return redirect("/dynamic")
        return render_template('index.html')   
    return render_template('index.html')   

def add_link(url, s):
    si.url = url
    si.url_count = si.url_count + 1
    si.scrape_items['Link ' + str(si.url_count)] = {'url': si.url, 'scraped items': {}, 'follow': s}

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
            jsp = request.form['jsp']
            if jsp == "jsp_true":
                si.jsp = True
            return redirect("/dynamic-v2-add-item")
        if 'add_item' or 'scrape' in request.form:
            return render_template('dynamic_scraper_v2.html',
                                        error="Please submit a valid url before trying to add/scrape items.",
                                        url_needed=True)
        
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        si.clear()
        return render_template('dynamic_scraper_v2.html', url_needed=True)
    
@app.route("/dynamic-v2-add-item", methods=['POST', 'GET'])
def dynamic_v2_add():
    if request.method == 'POST':
        if 'url_submit' in request.form:
            url = request.form['url'].strip()
            if url == '':
                return render_template('dynamic_scraper_v2.html',
                                        error="Please submit a valid url.",
                                        url_needed=True)
            return render_template('dynamic_scraper_v2.html',
                                items_submitted=True,
                                url_needed=False,
                                url=si.base_url,
                                instructions=si.instructions)
        
        if 'add_item' in request.form:
            # Pull all items from the form
            i = request.form['instruction_select']
            param = request.form['param'].strip()
            tag = request.form['tag'].strip()
            attribute = request.form['attribute'].strip()
            value = request.form['value'].strip()
            function_name = request.form['function_name'].strip()
            params = [param, tag, attribute, value, function_name]
            si.instructions.append((i, params))

            return render_template('dynamic_scraper_v2.html',
                                items_submitted=True,
                                url_needed=False,
                                url=si.base_url,
                                instructions=si.instructions)
        
        if 'scrape' in request.form:
            return redirect("/dynamic-v2-scrape")
    
    return render_template('dynamic_scraper_v2.html',
                            items_submitted=True,
                            url_needed=False,
                            url=si.base_url,
                            instructions=si.instructions)

@app.route("/dynamic-v2-scrape", methods=['POST', 'GET'])
def dynamic_v2_scrape():
    if request.method =='POST':
        if 'url_submit' in request.form:
            return redirect("/dynamic-v2-add-item")
        
        if 'download' in request.form:
            return redirect("/dynamic/download")

    # try:
        # Pass the dictionary to the scraper
    result = dynamic_v2(si.base_url, si.instructions, si.jsp)
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

    return render_template('dynamic_scraper_v2_output.html',
                        scrape=True,
                        output=final)

@app.route("/dynamic-v2-delete/<int:key>")
def dynamic_delete_v2(key):
    instructs = si.instructions
    i = instructs[key]

    # Option 2: If i[key] == click element, pop each instruction up + including 'go back previous page'
    # Update list to linked list
    if int(i[0]) == 7:
        new_instructs = instructs[0:key]
        finished = False
        l = len(instructs)
        for x in range(key, l):
            if finished:
                new_instructs.append(instructs[x])
            else:
                num = instructs[x][0]
                if int(num) == 8 or finished:
                    finished = True
        si.instructions = new_instructs

    # Else, pop one instruction
    else:
        instructs.pop(key)

    return redirect("/dynamic-v2-add-item")

@app.route("/dynamic-v2-update/<int:key>", methods=['POST','GET'])
def dynamic_update_v2(key):
    # If the user submits an update request, update the item.
    if 'update_item' in request.form:
        i = request.form['instruction_select']
        param = request.form['param'].strip()
        tag = request.form['tag'].strip()
        attribute = request.form['attribute'].strip()
        value = request.form['value'].strip()
        function_name = request.form['function_name'].strip()
        params = [param, tag, attribute, value, function_name]
        si.instructions.insert(key, (i, params))
        return redirect("/dynamic-v2-add-item")
    
    # Otherwise, find the item the user is requesting to delete and display it.
    i = si.instructions[key]
    instruct = i[0]
    params = i[1]
    si.instructions.pop(key)
    return render_template('dynamic_update_v2.html',
                           instruct=instruct,
                           params=params)

@app.route("/dynamic-v2/<int:key>")
def view_instruction(key):
    instructs = si.instructions[0:key+1]
    # Load all of the instructions into Selenium
    # Run scraper up until given instruction
    url = get_url(si.base_url, instructs, si.jsp)
    return redirect(url)

if __name__ == "__main__":
    app.run(debug=True)