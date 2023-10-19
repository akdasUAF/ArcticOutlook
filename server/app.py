from flask import Flask, render_template, request, redirect
import subprocess, os, json
import pandas as pd
from scripts.community_profiles import main
from scripts.initial_scrape import main as init_scrape



# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True


def display_text_input(s):
    """Simple method to determine which text boxes should be displayed for the static scrapers in the new form. 
    Returns an error if something goes wrong."""
    # Display operator parameters
    if s == 'Operators':
        return render_template(
            'static_scrapers.html',
            operation=True,
            script=s
        )
    
    # Display systems parameters
    if s == 'Systems':
        return render_template(
            'static_scrapers.html',
            operation=True,
            script=s
        )
    
    # Display community_profiles parameters
    if s == 'Community_Profiles':
        return render_template(
            'static_scrapers.html',
            operation=True,
            script=s
        )
    
    # Something went wrong
    else:
        return render_template(
            'static_scrapers.html',
            operation=False,
            msg="Something went wrong."
        )


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
        if 'url_link' in request.form:
            url = request.form['url']
            sel = request.form['scrape_content']
            user_id = request.form['id']
            cla = request.form['class']
            css = request.form['css']

            # Call the beautiful soup test scraper
            output = init_scrape(['-url', url, '-sel', sel, '-id', user_id, '-cla', cla, '-css', css])
            return render_template('dynamic_scraper.html',
                                   link=True,
                                   url_text=url,
                                   iter=output)
        
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        return render_template('dynamic_scraper.html')


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
            uri = request.form['Connection']
            db = request.form['Database']
            op = request.form['Operators']

            # Change directory to operators directory
            os.chdir("../operators") 
            path = os.getcwd()

            # Check if the user wants to download the information as a csv.
            if request.form.get("download"):
                proc = subprocess.Popen(["scrapy", "crawl",
                                "-s", "MONGODB_URI="+uri, 
                                "-s", "MONGODB_DATABASE="+db, 
                                "-s", "MONGODB_COLLECTION="+op,
                                "-o", "operators.csv",
                                "operators"],
                                cwd=path)
                proc.wait()

            # Otherwise, only upload information to MongoDB.
            else:
                proc = subprocess.Popen(["scrapy", "crawl",
                                "-s", "MONGODB_URI="+uri, 
                                "-s", "MONGODB_DATABASE="+db, 
                                "-s", "MONGODB_COLLECTION="+op, 
                                "operators"],
                                cwd=path)
                proc.wait()

            # Return response to the user.
            return render_template(
                'static_scrapers.html',
                operation=False,
                msg="Operator spider finished."
            )
        
        # Systems form submitted
        elif 'sys' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            sys = request.form['Systems']
            con = request.form['SContact']

            # Change path to systems directory
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
                df_systems.to_csv("systems.csv")
                df_contacts.to_csv("contacts.csv")
                try:
                    os.remove("results.json")
                except OSError as e:
                    print(e)
                
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

            # Return response to the user.
            return render_template(
                'static_scrapers.html',
                operation=False,
                msg="System spider finished."
            )
        
        # Community profile form submitted.
        elif 'cc' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            comm = request.form['Community']
            con = request.form['CContact']

            # Check if the user wants to download the information as a csv.
            if request.form.get("download"):
                main(['-uri', uri, '-db', db, '-comm', comm, '-con', con, '--download'])
            
            # Otherwise, only upload information to MongoDB.
            else:
                main(['-uri', uri, '-db', db, '-comm', comm, '-con', con])
            
            # Return response to the user.
            return render_template(
                'static_scrapers.html',
                operation=False,
                msg="community_profiles.py finished."
            )
    
    # Otherwise, respond to the GET request by displaying the webpage.
    else:
        return render_template('static_scrapers.html')


if __name__ == "__main__":
    app.run(debug=True)