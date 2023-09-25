from flask import Flask, render_template, request, url_for

# Name of the module initializing / running the program
app = Flask(__name__)
app.debug = True


@app.route("/", methods=['POST','GET'])
def index():
    if request.method == 'POST':
        if 'script' in request.form:
            script = request.form['SelectScript']

            # Display operator parameters
            if script == 'Operators':
                return render_template(
                    'index.html',
                    operation=True,
                    script=script
                )
            
            # Display systems parameters
            if script == 'Systems':
                return render_template(
                    'index.html',
                    operation=True,
                    script=script
                )
            
            # Display community_profiles parameters
            if script == 'Community_Profiles':
                return render_template(
                    'index.html',
                    operation=True,
                    script=script
                )
            
            # Something went wrong
            else:
                return render_template(
                    'index.html',
                    operation=False,
                    error="Something went wrong."
                )
        
        if 'params' in request.form:
            pass

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)