import requests, argparse, json
from bs4 import BeautifulSoup
from urllib.request import urljoin


def get_left_header(soup, selector):
    table = soup.select_one(selector)
    if table:
        cols = table.find_all(lambda tag: tag.name=='th')
        rows = table.find_all(lambda tag: tag.name=='td')
        t = {}
        for y in range(0, len(rows)):
            t[cols[y].text] = rows[y].text
        return t
    else:
        return None

def get_top_header(soup, selector):
    table = soup.select_one(selector)
    if table:
        cols = table.find_all(lambda tag: tag.name=='th')
        rows = table.findChildren(['th', 'tr'])
        t = []
        for row in rows:
            cells = row.findChildren('td')
            scraped_row = {}
            for cell, x in zip(cells, range(0, len(cols))):
                value = cell.text.strip()
                scraped_row[cols[x].text] = value
            # Do not add dictionary to list if dictionary is empty
            if len(scraped_row) > 0:
                t.append(scraped_row)
        return t
    else:
        return None

def check_path(link, url):
    if not link.startswith('http'):
        link = urljoin(url, link)
        return link

def get_href(soup, selector, url):
    item = soup.select_one(selector)
    if item:
        links = item.find_all('a', href=True)
        l = []
        l_dict = {}
        z=0
        if not links:
            path = check_path(item['href'], url)
            return [path]
        else:
            for h in links:
                path = check_path(h['href'], url)
                l.append(path)
                l_dict['Link ' + str(z)] = path
                z=z+1
            return [l_dict, l]
    else:
        return None

def get_data(soup, selector, url):
    item = soup.select_one(selector)
    if item:
        if item.text:
            return item.text
        elif item['href']:
            path = check_path(item['href'], url)
            return path
        else:
            return item
    else:
        return None

def scrape_items(url, iter, vals):
    # Set the scraper's user-agent.
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"}
    # Get html of provided webpage.
    response = requests.get(url, headers=user_agent)
    print(response)
    # Adjusted the parser to use html5lib. This allows it to parse broken html.
    soup = BeautifulSoup(response.content, "html5lib")

    data = []
    for i in iter:
        try:
            v = vals[i]
            selector = v['item']
            type = v['type']
            if type == 'href':
                links = get_href(soup, selector, url)[0]
                data.append(links)

            # If the user selects the entire table, the program should pull each item out of the table.
            # Special tables such as the System Table at DWW.
            elif type == 'left-table':
                data.append(get_left_header(soup, selector))

            # Regular tables with header on the top of the table.
            elif type == 'table':
                d = get_top_header(soup, selector)
                print(d)
                data.append(get_top_header(soup, selector))

            # If no specific tag is specified, it will default here. First will attempt to take the text, then the href.
            # If neither work, it will append the item to the list.
            else:
                data.append(get_data(soup, selector, url))
        except AttributeError:
            # data.append(None)
            continue
        #     except Exception as e:
        # return "Exception thrown in initial_scrape: " + str(e)
    return dict(zip(iter,data))

def main(raw_args=None):
    # Set arguments for the argparse to interpret.
    parser = argparse.ArgumentParser()
    parser.add_argument("-url", help="The url link of the initial html scrape.")
    parser.add_argument("-v", "--values", default="{}")
    args = parser.parse_args(raw_args)

    # Set the scraper's user-agent.
    user_agent = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"}
    
    # Create variables to store passed in arguments.
    start_url = args.url
    scraping_items = eval(args.values)

    # Get html of provided webpage.
    response = requests.get(start_url, headers=user_agent)

    # Adjusted the parser to use html5lib. This allows it to parse broken html.
    soup = BeautifulSoup(response.content, "html5lib")

    vals = list(scraping_items.values())
    result = []
    for v in vals:
        url = v['url']
        scraped = v['scraped items']
        iter = list(scraped.keys())
        if v['follow'] == 'yes':
            link = get_href(soup, url, start_url)
            if len(link) > 1:
                url = link[1] # Set equal to the list of links returned
            else:
                url = link

        # if url is a list, loop through list and call scrape_items on every scraped with new url
        if isinstance(url, list):
            for u in url:
                print('scrape item call')
                output = scrape_items(u, iter, scraped)
                output['url'] = u
                result.append(output)
        else:
            output = scrape_items(url, iter, scraped)
            result.append(output)
    print('loop complete')
    return result

if __name__ == '__main__':
    # Add parser information for command line calls.
    main()