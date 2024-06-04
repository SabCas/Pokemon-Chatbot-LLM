import os
import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup


# Ensure the directories for storing data exist
os.makedirs('../data/pokewiki_data', exist_ok=True)
os.makedirs('../data/bisafans_data', exist_ok=True)
os.makedirs('../data/bulbapedia_data', exist_ok=True)


def get_pokewiki_data():
    """
    Fetches Pokémon names and their corresponding links from PokéWiki.
    """
    url = 'https://www.pokewiki.de/Pok%C3%A9mon-Liste'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    all_names = []
    all_links = []

    # Iterate over each row in the table, skipping the header
    for row in soup.find('tbody').find_all('tr')[1:]:
        name = row.find('a').text
        link = 'https://www.pokewiki.de' + row.find('a').get('href')
        all_names.append(name)
        all_links.append(link)

    return all_names, all_links


def get_bisafans_data():
    """
    Fetches Pokémon names and their corresponding links from Bisafans.
    """
    url = 'https://www.bisafans.de/pokedex/listen/numerisch.php'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    all_names = []
    all_links = []

    # Iterate over each row in the table
    for row in soup.find('tbody').find_all('tr'):
        name = row.find('a').text
        link = row.find('a').get('href')
        all_names.append(name)
        all_links.append(link)

    return all_names, all_links


def get_bulbapedia_data():
    """
    Fetches Pokémon names and their corresponding links from Bulbapedia.
    """
    url = 'https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number'
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')

    all_names = []
    all_links = []

    for tbody in soup.find_all('tbody')[1:-3]:
        for row in tbody.find_all('tr')[1:]:
            name = row.find_all('a')[1].text
            link = 'https://bulbapedia.bulbagarden.net' + row.find_all('a')[1].get('href')

            all_names.append(name)
            all_links.append(link)

    all_names = list(dict.fromkeys(all_names))
    all_links = list(dict.fromkeys(all_links))

    return all_names, all_links


async def fetch(session, url):
    """
    Asynchronously fetches the content of a URL.
    """
    try:
        async with session.get(url) as response:
            content = await response.text()
            print(f"Downloaded {url} with length {len(content)}")
            return content
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None


async def download_all_sites(urls):
    """
    Downloads content from a list of URLs asynchronously.
    """
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch(session, url)) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


def save_to_file(name, content, index, directory):
    """
    Saves the content to a file in the specified directory.
    """
    filename = str(index+10001)[-4:] + '_' + name + ".html"
    filepath = os.path.join(directory, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    """
    Main function to fetch data from PokéWiki and Bisafans, download their pages, and save them to files.
    """
    data_sources = [
        ('../data/pokewiki_data', get_pokewiki_data),
        ('../data/bisafans_data', get_bisafans_data),
        ('../data/bulbapedia_data', get_bulbapedia_data)
    ]

    for storing_dir, data_func in data_sources:
        names, urls = data_func()
        results = asyncio.run(download_all_sites(urls))

        for index, (name, content) in enumerate(zip(names, results)):
            if content:
                save_to_file(name, content, index, storing_dir)


if __name__ == "__main__":
    main()
