from flask import Flask, render_template, request, redirect, send_file
import subprocess, os, json, zipfile
import pandas as pd
from scripts.community_profiles import main
from scripts.initial_scrape import main as init_scrape


# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True

class ScrapeItems():
    def __init__(self):
        self.scrape_items = {}
        self.url = ""
        self.args = []
        self.url_count = 0

    def clear(self):
        self.scrape_items = {}
        self.url = ""
        self.args = []

si = ScrapeItems()
def split_json(cwd):
    """This function handles the split of the water systems json file."""
    # Split the json data into 2 different csv's.
    contacts, systems = [], []
    with open('results.json') as f:
        data = json.load(f)
    for item in data:
        k = list(item.keys())[0]
        if k == "name":
            contacts.append(item)
        else:
            systems.append(item)

    df_systems = pd.DataFrame(systems)
    df_contacts = pd.DataFrame(contacts)

    # Output the 2 dfs to 2 separate files, delete the json file
    df_systems.dropna().to_csv("systems.csv")
    df_contacts.dropna().drop_duplicates().to_csv("contacts.csv")
    try:
        os.remove("results.json")
    except OSError as e:
        print(e)
    os.chdir(cwd)

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

    # Check if the user wants to download the information as a csv.
    if request.form.get("download"):
        proc = subprocess.Popen(["scrapy", "crawl",
                        "-s", "MONGODB_URI="+uri, 
                        "-s", "MONGODB_DATABASE="+db, 
                        "-s", "MONGODB_COLLECTION="+op,
                        "-o", os.path.join(root, "files", "operators.csv"),
                        "operators"],
                        cwd=path)
        proc.wait()
        return redirect("/scrapers/download-op")

    # Otherwise, only upload information to MongoDB.
    else:
        proc = subprocess.Popen(["scrapy", "crawl",
                        "-s", "MONGODB_URI="+uri, 
                        "-s", "MONGODB_DATABASE="+db, 
                        "-s", "MONGODB_COLLECTION="+op, 
                        "operators"],
                        cwd=path)
        proc.wait()
    os.chdir(root)
    # Return response to the user.
    return render_template(
        'static_scrapers.html',
        operation=False,
        msg="Operator spider finished."
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

    # Check if the user wants to download the information as a csv.
    if request.form.get("download"):
        proc = subprocess.Popen(["scrapy", "crawl",
                        "-s", "MONGODB_URI="+uri,
                        "-s", "MONGODB_DATABASE="+db,
                        "-s", "MONGODB_COLLECTION_SYSTEMS="+sys,
                        "-s", "MONGODB_COLLECTION_CONTACTS="+con,
                        "-o", "results.json",
                        "systems"],
                        cwd=path)
        proc.wait()
        split_json(root)
        return redirect("/scrapers/download-sys")
        
    # Otherwise, only upload information to MongoDB.
    else:
        proc = subprocess.Popen(["scrapy", "crawl",
                        "-s", "MONGODB_URI="+uri,
                        "-s", "MONGODB_DATABASE="+db,
                        "-s", "MONGODB_COLLECTION_SYSTEMS="+sys,
                        "-s", "MONGODB_COLLECTION_CONTACTS="+con,
                        "systems"],
                        cwd=path)
        proc.wait()
        os.chdir(root) 
    # Return response to the user.
    return render_template(
        'static_scrapers.html',
        operation=False,
        msg="System spider finished."
    )

def run_community_profiles_script(request):
    """This function handles the call to the community profiles script located in /scripts."""
    uri = request.form['Connection']
    db = request.form['Database']
    comm = request.form['Community']
    con = request.form['CContact']

    # Check if the user wants to download the information as a csv.
    if request.form.get("download"):
        main(['-uri', uri, '-db', db, '-comm', comm, '-con', con, '--download'])
        return redirect("/scrapers/download-cc")
    
    # Otherwise, only upload information to MongoDB.
    else:
        main(['-uri', uri, '-db', db, '-comm', comm, '-con', con])
    
    # Return response to the user.
    return render_template(
        'static_scrapers.html',
        operation=False,
        msg="community_profiles.py finished."
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
            si.url_count = si.url_count + 1
            si.scrape_items['Link ' + str(si.url_count)] = {'url': si.url, 'scraped items': {}}
            if si.url == '':
                return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url.",
                                        url_needed=True)
       
            return redirect("/dynamic-add-item")
        if 'add_item' in request.form and si.url_count == 0:
            return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url before trying to add items.",
                                        url_needed=True)
        
        if 'scrape' in request.form and si.url_count == 0:
            return render_template('dynamic_scraper.html',
                                        error="Please submit a valid url and items before trying to run a scrape.",
                                        url_needed=True)
        
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        si.clear()
        return render_template('dynamic_scraper.html', url_needed=True)

@app.route("/dynamic-add-item", methods=['POST', 'GET'])
def dynamic_add():
    if 'url_submit' in request.form:
        si.url = request.form['url'].strip()
        si.url_count = si.url_count + 1
        si.scrape_items['Link ' + str(si.url_count)] = {'url': si.url, 'scraped items': {}}
        if si.url == '':
            return render_template('dynamic_scraper.html',
                                    error="Please submit a valid url.",
                                    url_needed=True)
        return render_template('dynamic_scraper.html',
                            items_submitted=True,
                            result=si.scrape_items,
                            url_needed=False,
                            dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())))
       
    if 'add_item' in request.form:
        # Pull all items from the form
        name = request.form['name'].strip()
        item = request.form['item'].strip()
        arg_select = request.form['arg_select']
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
        
        # If the item is valid, add it to the dictionary and return the new list of items.
        si.scrape_items['Link ' + str(si.url_count)]['scraped items'][name] = {'item':item, 'type':arg_select}
        return render_template('dynamic_scraper.html',
                            items_submitted=True,
                            result=si.scrape_items,
                            url_needed=False,
                            dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())))
    
    if 'scrape' in request.form:
        return redirect("/dynamic-scrape")
    
    return render_template('dynamic_scraper.html',
                            items_submitted=True,
                            result=si.scrape_items,
                            url_needed=False,
                            dict=zip(list(si.scrape_items.values()),list(si.scrape_items.keys())))

@app.route("/dynamic-scrape", methods=['POST', 'GET'])
def dynamic_scrape():
    if request.method =='POST':
        if 'url_submit' in request.form:
            return redirect("/dynamic-add-item")
        
        if 'download' in request.form:
            return redirect("/dynamic/download")

    try:
        # For each link, run the scraper.
        vals = list(si.scrape_items.values())
        result = []
        for v in vals:
            url = v['url']
            scraped = v['scraped items']
            output = init_scrape(['-url', url, '-v', str(scraped)])
            if isinstance(output, str):
                return render_template('dynamic_scraper.html',
                                error="Error encountered during scrape: " + output,
                                url_needed=True) 
            result.append(output)
        
        # Add the scraped items to a dictionary
        data = {}
        for r in result:
            data.update(r)

        # Create a dataframe and a csv file containing the scraped contents.
        df = pd.DataFrame([data])
        df.to_csv('output.csv', index=False)
        si.clear()
        return render_template('dynamic_scraper.html',
                            scrape=True,
                            output=df)
    except Exception as e:
        si.clear()
        return render_template('dynamic_scraper.html',
                            error="Error encountered during scrape: " + str(e),
                            url_needed=True)

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
    return send_file(
            'output.csv',
            mimetype='text/csv',
            download_name='output.csv',
            as_attachment=True
        )

@app.route("/scrapers/download-op")
def static_download_op():
    return send_file(
            '../operators/operators.csv',
            mimetype='text/csv',
            download_name='output_operators.csv',
            as_attachment=True
        )

@app.route("/scrapers/download-sys")
def static_download_sys():
    zipf = zipfile.ZipFile('systems.zip','w', zipfile.ZIP_DEFLATED)
    zipf.write("../systems/contacts.csv")
    zipf.write("../systems/systems.csv")
    zipf.close()
    os.remove("../systems/contacts.csv")
    os.remove("../systems/systems.csv")
    return send_file(
            'systems.zip',
            download_name='output_systems.zip',
            as_attachment=True
        )

@app.route("/scrapers/download-cc")
def static_download_cc():
    zipf = zipfile.ZipFile('community.zip','w', zipfile.ZIP_DEFLATED)
    zipf.write("./communities.csv")
    zipf.write("./community_contacts.csv")
    zipf.close()
    os.remove("./communities.csv")
    os.remove("./community_contacts.csv")
    return send_file(
            'community.zip',
            download_name='output_community.zip',
            as_attachment=True
        )

if __name__ == "__main__":
    app.run(debug=True)