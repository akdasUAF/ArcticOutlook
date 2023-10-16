from flask import Flask, render_template, request, redirect
import subprocess, os, json
import pandas as pd
from scripts.community_profiles import main


# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True


def display_text_input(s):
    """Simple method to determine which text boxes should be displayed in the new form. Returns an error if something goes wrong."""
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
    """This function handles the display of the main page."""
    if request.method == 'POST':
        if 'select_task' in request.form:
            if request.form['SelectTask'] == 'static_scrapers':
                return redirect("/scrapers")
            else:
                return redirect("/dynamic")
        return render_template('index.html')   
    return render_template('index.html')   


@app.route("/scrapers", methods=['POST','GET'])
def run_static_scrapers():
    """This function handles the display and operation of the premade scrapers."""

    if request.method == 'POST':
        # User selected a script
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

            if request.form.get("download"):
                proc = subprocess.Popen(["scrapy", "crawl",
                                "-s", "MONGODB_URI="+uri, 
                                "-s", "MONGODB_DATABASE="+db, 
                                "-s", "MONGODB_COLLECTION="+op,
                                "-o", "operators.csv",
                                "operators"],
                                cwd=path)
                proc.wait()

            else:
                proc = subprocess.Popen(["scrapy", "crawl",
                                "-s", "MONGODB_URI="+uri, 
                                "-s", "MONGODB_DATABASE="+db, 
                                "-s", "MONGODB_COLLECTION="+op, 
                                "operators"],
                                cwd=path)
                proc.wait()

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

                # Split the json data into 2 different csv's
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
                
            else:
                proc = subprocess.Popen(["scrapy", "crawl",
                                "-s", "MONGODB_URI="+uri,
                                "-s", "MONGODB_DATABASE="+db,
                                "-s", "MONGODB_COLLECTION_SYSTEMS="+sys,
                                "-s", "MONGODB_COLLECTION_CONTACTS="+con,
                                "systems"],
                                cwd=path)
                proc.wait()

            return render_template(
                'static_scrapers.html',
                operation=False,
                msg="System spider finished."
            )
        
        # Community profile form submitted
        elif 'cc' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            comm = request.form['Community']
            con = request.form['CContact']
            if request.form.get("download"):
                main(['-uri', uri, '-db', db, '-comm', comm, '-con', con, '--download'])
            else:
                main(['-uri', uri, '-db', db, '-comm', comm, '-con', con])
            return render_template(
                'static_scrapers.html',
                operation=False,
                msg="community_profiles.py finished."
            )

    return render_template('static_scrapers.html')


if __name__ == "__main__":
    app.run(debug=True)