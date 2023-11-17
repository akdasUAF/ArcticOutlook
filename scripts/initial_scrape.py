import requests, argparse, json
from bs4 import BeautifulSoup

def main(raw_args=None):
    # Set arguments for the argparse to interpret.
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", help="The url link of the initial html scrape.")
    parser.add_argument("-v", "--values", default="{}")
    args = parser.parse_args(raw_args)

    # Set the scraper's user-agent.
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"}
    
    # Create variables to store passed in arguments.
    url = args.url
    vals = eval(args.values)

    iter = list(vals.keys())

    # Get html of provided webpage.
    response = requests.get(url, headers=user_agent)

    # Adjusted the parser to use html5lib. This allows it to parse broken html.
    soup = BeautifulSoup(response.content, "html5lib")

    # Create list to return each item
    data = []
    z = 0
    try:
        for i in iter:
            v = vals[i]
            selector = v['item']
            type = v['type']
            if type == 'href':
                item = soup.select_one(selector)
                links = item.find_all('a', href=True)
                l = {}
                if not links:
                    data.append(item['href'])
                else:
                    for h in links:
                        l['Link ' + str(z)] = h['href']
                        z=z+1
                    data.append(l)
                    z=0

            # If the user selects the entire table, the program should pull each item out of the table.
            # Special tables such as the System Table at DWW.
            elif type == 'left-table':
                table = soup.select_one(selector)
                cols = table.find_all(lambda tag: tag.name=='th')
                rows = table.find_all(lambda tag: tag.name=='td')
                t = {}
                for y in range(0, len(rows)):
                    t[cols[y].text] = rows[y].text
                data.append(t)

            # Regular tables with header on the top of the table.
            elif type == 'table':
                table = soup.select_one(selector)
                cols = table.find_all(lambda tag: tag.name=='th')
                rows = table.findChildren(['th', 'tr'])
                t = []
                for row in rows:
                    cells = row.findChildren('td')
                    scraped_row = {}
                    print(row.text)
                    for cell, x in zip(cells, range(0, len(cols))):
                        # print(cell.text)
                        value = cell.string
                        scraped_row[cols[x].text] = value
                    # Do not add dictionary to list if dictionary is empty
                    if len(scraped_row) > 0:
                        t.append(scraped_row)

                data.append(t)

            # If no specific tag is specified, it will default here. First will attempt to take the text, then the href.
            # If neither work, it will append the item to the list.
            else:
                item = soup.select_one(selector)
                if item.text:
                    data.append(item.text)
                elif item['href']:
                    data.append(item['href'])
                else:
                    data.append(item)
    except Exception as e:
        return "Exception thrown in initial_scrape: " + str(e)

    # Return list of generated items.
    return dict(zip(iter,data))


if __name__ == '__main__':
    # Add parser information for command line calls.
    main()