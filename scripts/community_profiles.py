"""This program retrieves an excel sheet filled with community water and contact information. This script then inserts the
information into the specified mongodb collections."""

"""Update script to be dynamic to any xl"""

from pymongo import MongoClient, ASCENDING, DESCENDING, WriteConcern
import pandas as pd
import argparse
import ssl

# If the program throws an error about an unverified user, uncomment the following line and the import ssl.
ssl._create_default_https_context = ssl._create_unverified_context

def main(raw_args=None):
    parser = argparse.ArgumentParser(description="""This program retrieves an excel sheet filled with community water and contact information. This script then inserts the information into the specified mongodb collections.""")
    parser.add_argument("-uri", help="Specifies the connection string to mongoDB.")
    parser.add_argument("-db", help="Specifies the database name in MongoDB.")
    parser.add_argument("-comm", help="Specifies the collection where the community information should be stored.")
    parser.add_argument("-con", help="Specifies the collection where the contact information should be stored.")
    parser.add_argument("-dl", help="Specifies if the contents should be downloaded as csv files.")
    args = parser.parse_args(raw_args)
    # Adjust MongoDB connection settings.
    MONGODB_URI = args.uri
    MONGODB_DATABASE = args.db
    COMMUNITY_TABLE = args.comm
    CONTACT_TABLE = args.con
    download = args.dl


    # MONGODB_URI = "Your MongoDB Connection String"
    # MONGODB_DATABASE = "Your Database Name"
    # COMMUNITY_TABLE = "Your Community Collection Name"
    # CONTACT_TABLE = "Your Contacts Collection Name"
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"}

    url = "https://dec.alaska.gov/Applications/Water/OpCert/community-water-sewer-improvement-contact-list.xlsx"
    df = pd.read_excel(url, storage_options=user_agent, engine='openpyxl')
    df.columns = ["Community", "3 Letter Airport Code", "Project Agency Lead", "Primary Project Engineer", 
                                            "PPE Phone Number", "RMW Region", "Remote Maintenance Worker", "RMW Phone Number", "RMW Supervisor", 
                                            "RMWS Phone Number", "RUBA Contact", "RUBA Phone Number", "Operator Certification Contact", 
                                            "OCC Phone Number", "Drinking Water Staff", "DWS Phone Number", "Solid Waste Contact",  
                                            "SWC Phone Number"]

    # Create a new dataframe for inserting the contacts into the database.
    names = ["Primary Project Engineer", "Remote Maintenance Worker", "RMW Supervisor", "RUBA Contact", 
                    "Operator Certification Contact", "Drinking Water Staff", "Solid Waste Contact"]
    numbers = ["PPE Phone Number", "RMW Phone Number", "RMWS Phone Number", "RUBA Phone Number", "OCC Phone Number",
                        "DWS Phone Number", "SWC Phone Number"]
    l,l2=[],[]
    for x in names:
            for i in df[x]:
                l.append(i)
    for x in numbers:
            for i in df[x]:
                l2.append(i)
    d = {'Name': l, 'Phone Number': l2}
    df_contacts = pd.DataFrame(data=d)

    # Remove unneeded columns in the community table.
    df.drop(columns = ["PPE Phone Number", "RMW Phone Number", "RMWS Phone Number", "RUBA Phone Number", "OCC Phone Number",
                    "DWS Phone Number", "SWC Phone Number"], inplace=True)

    # Create a connection to the database.
    mongoClient = MongoClient(MONGODB_URI)
    db = mongoClient[MONGODB_DATABASE]
    community = db[COMMUNITY_TABLE]
    contacts = db[CONTACT_TABLE]

    # Clears the community table and uploads new information for the purpose of the demonstration.
    community.delete_many({}) 
    community.insert_many(df.to_dict('records'), ordered=False)

    # Update the contacts table with new contacts in the excel sheet.
    index = contacts.create_index([('Name', ASCENDING), ('Phone Number', DESCENDING)], unique=True)
    contacts.with_options(write_concern=WriteConcern(w=0)).insert_many(df_contacts.to_dict('records'), ordered=False)

    mongoClient.close()

    if download == "True":
        df.drop_duplicates().to_csv("communities.csv")
        df_contacts.drop_duplicates().to_csv("community_contacts.csv")
         


if __name__ == '__main__':
    # Add parser information for command line calls.
    main()