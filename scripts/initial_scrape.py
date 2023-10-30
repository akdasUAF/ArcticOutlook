import requests
from bs4 import BeautifulSoup
import argparse

def main(raw_args=None):
    # Set arguments for the argparse to interpret.
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", help="The url link of the initial html scrape.")
    parser.add_argument("-i", "--items", nargs='*')
    parser.add_argument("-a", nargs='*')
    args = parser.parse_args(raw_args)

    # Set the scraper's user-agent.
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"}
    
    # Create variables to store passed in arguments.
    url = args.url
    iter = args.items[0]
    type = args.a[0]

    # Get html of provided webpage.
    response = requests.get(url, headers=user_agent)

    # Adjusted the parser to use html5lib. This allows it to parse broken html.
    soup = BeautifulSoup(response.content, "html5lib")

    # Create list to return each item
    data = []
    x = 0
    try:
        for i in iter:
            if type[x] == 'text':
                data.append(soup.select_one(i).text)

            elif type[x] == 'href':
                item = soup.select_one(i)
                data.append(item['href'])

            # If the user selects the entire table, the program should pull each item out of the table.
            elif type[x] == 'table':
                table = soup.select_one(i)
                rows = table.find_all(lambda tag: tag.name=='td')
                for y in range(0, len(rows)):
                    rows[y] = rows[y].text
                data.append(rows)

            # If no specific tag is specified, it will default here. First will attempt to take the text, then the href.
            # If neither work, it will append the item to the list.
            else:
                item = soup.select_one(i)
                if item.text:
                    data.append(item.text)
                elif item['href']:
                    data.append(item['href'])
                else:
                    data.append(item)
            x=x+1
    except Exception as e:
        return "Exception thrown in initial_scrape: " + str(e)

    # Return list of generated items.
    return data


if __name__ == '__main__':
    # Add parser information for command line calls.
    main()