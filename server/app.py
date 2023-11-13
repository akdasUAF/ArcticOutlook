from flask import Flask, render_template, request, redirect, send_file
import subprocess, os, json, zipfile, pymongo
import pandas as pd
from scripts.community_profiles import main
from scripts.initial_scrape import main as init_scrape


# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True
app.config['UPLOAD_FOLDER'] = './files'

class ScrapeItems():
    def __init__(self):
        self.scrape_items = {}
        self.url = ""
        self.args = []

    def clear(self):
        self.scrape_items = {}
        self.url = ""
        self.args = []

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
            else:
                return redirect("/dynamic")
        return render_template('index.html')   
    return render_template('index.html')   

@app.route("/dynamic", methods=['POST', 'GET'])
def run_dynamic_scraper():
    """This function handles the display and operation of the WIP 'dynamic' scraper interface."""
    # If the user hits the submit button, send the information to the server.
    if request.method == 'POST':
        if 'url_submit' in request.form:
            si.url = request.form['url'].strip()
            if si.url == '':
                return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url.",
                                        url_needed=True)
       
            return render_template('dynamic_scraper.html',
                                    url_needed=False,
                                    url=si.url)
        
        if 'add_item' in request.form:
            name = request.form['name'].strip()
            item = request.form['item'].strip()
            if name == '':
                return render_template('dynamic_scraper.html',
                                items_submitted=True,
                                result=si.scrape_items,
                                url_needed=False,
                                url=si.url,
                                error="Name string was empty. Please resubmit item with proper name.")
            if item == '':
                return render_template('dynamic_scraper.html',
                                items_submitted=True,
                                result=si.scrape_items,
                                url_needed=False,
                                url=si.url,
                                error="Selector string was empty. Please resubmit item with proper selector.")
            si.scrape_items[name] = item
            si.args.append(request.form['arg_select'])
            return render_template('dynamic_scraper.html',
                                items_submitted=True,
                                result=si.scrape_items,
                                url_needed=False,
                                url=si.url)
        
        if 'scrape' in request.form:
            # If no scrape_items, scrape whole html and return that
            try:
                keys = list(si.scrape_items.keys())
                items = list(si.scrape_items.values())
                output = init_scrape(['-url', si.url, '-i', items, '-a', si.args])
                if isinstance(output, str):
                    return render_template('dynamic_scraper.html',
                                    error="Error encountered during scrape: " + output,
                                    url_needed=True)
                result = {keys[i]: [output[i]] for i in range(len(keys))}
                pd.DataFrame(result).to_csv('output.csv', index=False)
                items=si.scrape_items
                url=si.url
                si.clear()
                return render_template('dynamic_scraper.html',
                                    scrape=True,
                                    result=items,
                                    url_needed=True,
                                    url=url,
                                    iter=result)
            except Exception as e:
                si.clear()
                return render_template('dynamic_scraper.html',
                                    error="Error encountered during scrape: " + str(e),
                                    url_needed=True)
    
        if 'download' in request.form:
            return redirect("/dynamic/download")
        
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        si.clear()
        return render_template('dynamic_scraper.html', url_needed=True)

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
    return send_file(
            'output.csv',
            mimetype='text/csv',
            download_name='output.csv',
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

if __name__ == "__main__":
    app.run(debug=True)