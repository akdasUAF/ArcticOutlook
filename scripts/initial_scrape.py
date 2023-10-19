import requests
from bs4 import BeautifulSoup
import argparse

def main(raw_args=None):
    # Set arguments for the argparse to interpret.
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", help="The url link of the initial html scrape.")
    parser.add_argument("-sel")
    parser.add_argument("-id")
    parser.add_argument("-cla")
    parser.add_argument("-css")
    args = parser.parse_args(raw_args)

    # Set the scraper's user-agent.
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"}
    
    # Create variables to store passed in arguments.
    url = args.url
    sel = args.sel
    sel_id = args.id
    cla = args.cla
    css = args.css

    # Get html of provided webpage.
    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.content, "lxml")

    # Create list to return each item
    items = []

    # If the user selected a drop down item, return all appearances of that selected item.
    if sel != 'none':
        if sel == 'text':
            items.append(soup.get_text())

        elif sel == 'href':
            for link in soup.find_all('a'):
                items.append(link.get('href'))

        elif sel == 'html':
            items.append(soup.find('html'))

        elif sel == 'select':
            for s in soup.find_all('select'):
                items.append(s)

        else:
            for s in soup.find_all(sel):
                items.append(s)

    # If the user inputted an ID, retrieve that item.
    if sel_id:
        sel_id = "#"+sel_id
        items.append(soup.select(sel_id))

    # If the user inputted a class, retrieve all appearances of that class.
    if cla:
        for i in soup.find_all(class_=cla):
            items.append(i)

    # If the user inputted a css-selector, retrieve that item.
    if css:
        items.append(soup.select(css))

    # Return list of generated items.
    return items


if __name__ == '__main__':
    # Add parser information for command line calls.
    main()