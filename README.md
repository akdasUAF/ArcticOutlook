# ArcticOutlook
Water Information in Alaska

## Getting Started
### Dependencies
This project is built on Python 3.11.x. It is recommended that this project is used with a [Python virtual environment](https://docs.python.org/3/library/venv.html) or another package manager, such as [Anaconda](https://anaconda.org/), to prevent any issues with the dependencies. 

This project utilizes the following Python libraries:
* [PyMongo](https://pymongo.readthedocs.io/en/stable/)
* [Scrapy](https://docs.scrapy.org/en/latest/)
* [pandas](https://pandas.pydata.org/docs/)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
* [Python Flask](https://flask.palletsprojects.com/en/3.0.x/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
* [html5lib](https://pypi.org/project/html5lib/)
* [Selenium](https://www.selenium.dev/documentation/webdriver/)
* [dnspython](https://www.dnspython.org/)

In addition to ensuring Python and the required libraries are installed, this project also requires a [MongoDB](https://www.mongodb.com/) database for storing the collected information. When using a cluster provided by [MongoDB Atlas](https://www.mongodb.com/atlas/database), be sure to record the appropriate [connection string](https://www.mongodb.com/basics/mongodb-connection-string), database name(s), and collection name(s) for each script. There is also a [GUI interface](https://www.mongodb.com/products/compass) available that allows users to view database information.

### Set up
Prior to running any of the scripts in this project, ensure that the following updates are made to the files.

**Operator Spider**
In the `operators` directory, navigate to `settings.py`. Change the final three lines of code to your MongoDB database information:
```Python
MONGODB_URI = "Your MongoDB Connection String"
MONGODB_DATABASE = "Your Database Name"
MONGODB_COLLECTION = "Your Collection Name"
```

For Example:
```Python
MONGODB_URI = "mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test"
MONGODB_DATABASE = "Outlook"
MONGODB_COLLECTION = "Operators"
```
>Optional: You may also change the `USER_AGENT` to any other desired user agent.

Alternatively, you may call the spider as follows to avoid changing anything in settings.py:
```bash
scrapy crawl -s MONGODB_URI="mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test" -s MONGODB_DATABASE="Outlook" -s MONGODB_COLLECTION="Operators"`
```

In the `systems` directory, navigate to `settings.py`. Change the final three lines of code to your MongoDB database information:
```Python
MONGODB_URI = "Your MongoDB Connection String"
MONGODB_DATABASE = "Your Database Name"
MONGODB_COLLECTION_SYSTEMS = "Your Systems Collection Name"
MONGODB_COLLECTION_CONTACTS = "Your Contacts Collection Name"
```

For Example:
```Python
MONGODB_URI = "mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test"
MONGODB_DATABASE = "Outlook"
MONGODB_COLLECTION_SYSTEMS = "Systems"
MONGODB_COLLECTION_CONTACTS = "SystemContacts"
```

Alternatively, you may call the spider as follows to avoid changing anything in settings.py:
```bash
scrapy crawl -s MONGODB_URI="mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test" -s MONGODB_DATABASE="Outlook" -s MONGODB_COLLECTION_SYSTEMS="Systems" -s MONGODB_COLLECTION_CONTACTS=SystemContacts
```
>Optional: You may also change the `USER_AGENT` to any other desired user agent.


### Executing Program
**Operator Spider**
* On the command line, navigate to the repository. From there, navigate to the top level operators directory: `cd operators`
* Activate the spider (default): `scrapy crawl operators`
* Activate the spider with mongoDB settings in command line (using example values given above): 
  ```bash
  scrapy crawl -s MONGODB_URI="mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test" -s MONGODB_DATABASE="Outlook" -s MONGODB_COLLECTION="Operators" operators
  ```

**System Spider**
* On the command line, navigate to the repository. From there, navigate to the top level systems directory: `cd systems`
* Activate the spider (default): `scrapy crawl systems`
* Activate the spider with MongoDB settings in command line (using example values given above): 
  ```bash
  scrapy crawl -s MONGODB_URI="mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test" -s MONGODB_DATABASE="Outlook" -s MONGODB_COLLECTION_SYSTEMS="Systems" -s MONGODB_COLLECTION_CONTACTS=SystemContacts systems
  ```

**Community Profiles**
* Navigate to the directory that houses `community_profiles.py`. The default for this is the scripts directory of this repository.
* Run the Python script:
    - For Mac: 
    ```bash
    python3 community_profiles.py -uri mongodb+srv://<username>:<password>@beyondthebasics.abcde.mongodb.net/test -db Database_Name -comm Community_Collection_Name -con Contact_Collection_Name
    ```

    - For Windows (select one): 
    ```bash
    py community_profiles.py
    python.exe community_profiles.py
    ```

    - Flags:
      - `-uri`:         Sets the MongoDB connection string
      - `-db`:          Sets the MongoDB database name
      - `-comm`:        Sets the MongoDB communities collection name
      - `-con`:         Sets the MongoDB community contacts collection name
      - `--download`:   (Optional) Boolean flag to download the scraped information as 2 csv files.
      - `-h`:           Help flag, explains each of the above commands

## Flask Server
An alternative way of launching this project may be done through a simple [Python Flask](https://flask.palletsprojects.com/en/3.0.x/) server. When launched, this will allow the user to open a webpage located at 127.0.0.1:5000 (by default) to run each of the scrapers defined in this project. Additionally, there is the option for the user to download the output of the scrapers immediately as a csv file after the process has completed.

This server is currently the only way to access the Dynamic Scraper, File Upload, and Query Manager features of this project.

### Executing Program
* On the command line, navigate to the repository. From there, navigate to the server directory: `cd server`
* Activate the Flask server: `flask run`
  * `--host`: Changes the hostname (default: `127.0.0.1`)
  * `--port`: Changes the port number (default: `5000`)
  * `--debug`: Launches the server in debug mode
* Open a web browser and type `127.0.0.1:5000` in the search bar. This should open up the simple server for running each scraper.