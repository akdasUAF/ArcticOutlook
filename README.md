# ArcticOutlooc
Water Information in Alaska

## Getting Started
### Dependencies
This project is built on Python 3.11.x. It is recommended that this project is used with a [virtual environment](https://docs.python.org/3/library/venv.html) to prevent any issues with the dependencies. 
This project utilizes the following Python libraries:
* [PyMongo](https://pymongo.readthedocs.io/en/stable/)
* [Scrapy](https://docs.scrapy.org/en/latest/)
* [pandas](https://pandas.pydata.org/docs/)
* [openpyxl](https://openpyxl.readthedocs.io/en/stable/)

### Set up
Prior to running any of the scripts in this project, ensure that the following updates are made to the files.

**Operator Spider**
In the `operators` directory, navigate to `settings.py`. Change the final three lines of code to your MongoDB database information:
```
MONGODB_URI = "Your MongoDB Connection String"
MONGODB_DATABASE = "Your Database Name"
MONGODB_COLLECTION = "Your Collection Name"
```
>Optional: You may also change the `USER_AGENT` to any other desired user agent.

**Community Profiles**
Navigate to `community_profiles.py`. Located near the top of this file are the MongoDB connection settings that need to be adjusted for this project to run.
```
MONGODB_URI = "Your MongoDB Connection String"
MONGODB_DATABASE = "Your Database Name"
COMMUNITY_TABLE = "Your Community Collection Name"
CONTACT_TABLE = "Your Contact Collection Name"
```
>Optional: You may also change the `USER_AGENT` to any other desired user agent.


### Executing Program
**Operator Spider**
* On the command line, navigate to the top level operators directory. 
    - For Mac: `cd operators`
    - For Windows:
* Activate the spider
    - For Mac: `scrapy crawl operators`
    - For Windows:

**Community Profiles**
* Navigate to the directory that houses `community_profiles.py`. The default for this is the top level of this repository.
* Run the Python script
    - For Mac: `python3 community_profiles.py`
    - For Windows: