from flask import Flask, render_template, request, url_for
import subprocess
from scripts.community_profiles import main


# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True


def display_text_input(s):
    """Simple method to determine which text boxes should be displayed in the new form. Returns an error if something goes wrong."""
    # Display operator parameters
    if s == 'Operators':
        return render_template(
            'index.html',
            operation=True,
            script=s
        )
    
    # Display systems parameters
    if s == 'Systems':
        return render_template(
            'index.html',
            operation=True,
            script=s
        )
    
    # Display community_profiles parameters
    if s == 'Community_Profiles':
        return render_template(
            'index.html',
            operation=True,
            script=s
        )
    
    # Something went wrong
    else:
        return render_template(
            'index.html',
            operation=False,
            msg="Something went wrong."
        )


@app.route("/", methods=['POST','GET'])
def index():
    """Handles index page navigation and form display."""
    if request.method == 'POST':
        # User selected a script
        if 'script' in request.form:
            script = request.form['SelectScript']
            return display_text_input(script)
        
        # Operator form submitted
        if 'op' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            op = request.form['Operators']
            path = ""

            subprocess.Popen(["scrapy", "crawl",
                            "-s", "MONGODB_URI="+uri, 
                            "-s", "MONGODB_DATABASE="+db, 
                            "-s", "MONGODB_COLLECTION="+op, 
                            "operators"],
                            cwd=path)

            return render_template(
                'index.html',
                operation=False,
                msg="Operator spider started."
            )
        
        # Systems form submitted
        if 'sys' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            sys = request.form['Systems']
            con = request.form['SContact']
            path = ""

            subprocess.Popen(["scrapy", "crawl",
                              "-s", "MONGODB_URI="+uri,
                              "-s", "MONGODB_DATABASE="+db,
                              "-s", "MONGODB_COLLECTION_SYSTEMS="+sys,
                              "-s", "MONGODB_COLLECTION_CONTACTS="+con,
                              "systems"],
                              cwd=path)

            return render_template(
                'index.html',
                operation=False,
                msg="System spider started."
            )
        
        # Community profile form submitted
        if 'cc' in request.form:
            uri = request.form['Connection']
            db = request.form['Database']
            comm = request.form['Community']
            con = request.form['CContact']
            main(['-uri', uri, '-db', db, '-comm', comm, '-con', con])
            return render_template(
                'index.html',
                operation=False,
                msg="community_profiles.py started."
            )

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)