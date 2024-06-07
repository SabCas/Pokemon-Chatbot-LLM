import requests
import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from tqdm import tqdm


def fetch_pokemon_data(pokemon_name):
    url = f"https://bulbapedia.bulbagarden.net/wiki/{pokemon_name}_(Pokémon)"
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def parse_bulbapedia_html(file):
    f = open(file, encoding="utf8")
    soup = BeautifulSoup(f, 'html.parser')
    f.close()

    # Extract Pokémon name
    name = soup.find('h1', {'id': 'firstHeading'}).text.strip()

    # Extract Pokémon type(s)
    #types = [type_tag.text for type_tag in soup.find_all('a', {'href': lambda x: x and 'Type' in x})]
    types_section = soup.find('a', {'title': 'Type'}).parent
    types_list = types_section.find_next_sibling('table').find_all('b')
    types = [type.text for type in types_list if 'Unknown' != type.text]

    # Extract Pokémon abilities
    abilities_section = soup.find('a', {'title': 'Ability'}).parent
    abilities_list = abilities_section.find_next_sibling('table').find_all('a')
    # Add all abilities except of placeholder abilities
    abilities = [ability.text for ability in abilities_list if '(Ability)' in ability['href'] and ability.text != 'Cacophony'] #TODO: mark hidden abilities
    # TODO: rewrite to for loop and add hidden ability: abilities_section.find_next_sibling('table').find_all('small')
    # Remove duplicates
    abilities = list(dict.fromkeys(abilities))

    # Extract Pokémon stats (assuming they are in the first table with class 'roundy')
    stats_section = soup.findAll('th', {'style': 'padding-left: 0.2em; padding-right: 0.2em; display: flex; justify-content: space-between;'})
    # TODO: add stats for every gen
    # Only keep the stats of the newest Version
    while len(stats_section) > 6:
        stats_section.pop(0)
    stats = {}
    for row in stats_section:
        stat = row.text.split(':')
        stat_name = stat[0].replace(' ', '') # Remove white spaces for Sp. Attack and Sp. Defense
        stats[stat_name] = stat[1]

    # Egg Data
    eggs = {}
    egg_section = soup.find('a', {'href': '/wiki/Egg_Group'}).parent

    egg_list = egg_section.find_next_sibling('table').find_all('a')
    egg_group = [egg.text for egg in egg_list if egg.text not in ['Cap', 'Cosplay']]
    eggs["EggGroup"] = egg_group

    hatch_section= soup.find('a', {'href': '/wiki/Egg_cycle'}).parent.parent
    hatch = hatch_section.find('td').text.replace('\xa0', ' ').replace('\n', ' ')
    eggs["HatchTime"] = [hatch]

    # Gender
    gender_section = soup.find('a', {'title': 'List of Pokémon by gender ratio'}).parent
    gender_list = gender_section.find_next_sibling('table').find_all('td')
    gender = []
    for entry in gender_list:
        if('male' in entry.text or 'female' in entry.text or "unknown" in entry.text):
            gender.append(entry.text)


    # Height
    height_section = soup.find('a', {'title': 'List of Pokémon by height'}).parent
    # first element is in m and not feet
    height = height_section.find_next_sibling('table').find_all('td')[1].text

    # Weight
    weight_section = soup.find('a', {'title': 'Weight'}).parent
    # first element is in m and not feet
    weight = weight_section.find_next_sibling('table').find_all('td')[1].text
    bmi = [height, weight]


    # Biology
    biology_section = soup.find(id='Biology')
    biology = []
    if biology_section:
        current_elem = biology_section.find_next()
        while current_elem and current_elem.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if current_elem.name in ['p']:
                biology.append(current_elem.text)
            current_elem = current_elem.find_next()
    # Category
    category = soup.find('a', {'title' : 'Pokémon category'}).text


    return {
        'name': name,
        'types': types,
        'abilities': abilities,
        'stats': stats,
        'eggs' : eggs,
        'gender' : gender,
        'bmi' : bmi,
        'category' : category,
        'biology' : biology,
    }


def create_pokemon_xml(pokemon_data):
    root = ET.Element('pokemon')

    # Names in different Languages
    name_elem = ET.SubElement(root, 'name')
    name_elem.text = pokemon_data['name']

    # Pokemon Types
    types_elem = ET.SubElement(root, 'types')
    for type_ in pokemon_data['types']:
        type_elem = ET.SubElement(types_elem, 'type')
        type_elem.text = type_

    # Game related Information
    game_elem = ET.SubElement(root, 'game')

    # Pokemon Abilities
    abilities_elem = ET.SubElement(game_elem, 'abilities')
    for ability in pokemon_data['abilities']:
        ability_elem = ET.SubElement(abilities_elem, 'ability')
        ability_name_elem = ET.SubElement(ability_elem, 'name')
        ability_name_elem.text = ability

        ability_hidden_elem = ET.SubElement(ability_elem, 'hidden')
        ability_hidden_elem.text = False
        # TODO: add true false boolean for hidden

    # Pokemon Stats
    stats_elem = ET.SubElement(game_elem, 'stats')
    for stat_name, stat_value in pokemon_data['stats'].items():
        stat_elem = ET.SubElement(stats_elem, stat_name)
        stat_elem.text = stat_value

    # Pokemon Egg Information
    eggs_elem = ET.SubElement(game_elem, 'egg')
    for entry in pokemon_data['eggs']:
        for elem in pokemon_data['eggs'][entry]:
            egg_elem = ET.SubElement(eggs_elem, entry)
            egg_elem.text = elem

    # Pokemon Level Information

    # Pokemon Moveset

    # BMI
    bmi_elem = ET.SubElement(game_elem, 'bmi')
    height_elem = ET.SubElement(bmi_elem, 'height')
    height_elem.text = pokemon_data['bmi'][0]
    weight_elem = ET.SubElement(bmi_elem, 'weight')
    weight_elem.text = pokemon_data['bmi'][1]

    # Pokemon Gender Information
    gender_elem = ET.SubElement(game_elem, 'gender')
    for entry in pokemon_data['gender']:
        gender = ET.SubElement(gender_elem, 'ratio')
        gender.text = entry

    # Forms

    # Evolution

    # New Anime section
    anime_elem = ET.SubElement(root, 'anime')

    # Biology
    biology_elem = ET.SubElement(anime_elem, 'biology')
    for entry in pokemon_data['biology']:
        biology = ET.SubElement(biology_elem, 'p')
        biology.text = entry


    # Category
    category_elem = ET.SubElement(anime_elem, 'category')
    category_elem.text = pokemon_data['category']

    # Pokedex Entrys of the various games

    # Anime only moves

    # Major Appearances

    # Trivia

    return ET.ElementTree(root)


def save_pokemon_xml(pokemon_data, storing_dir, name):
    filename = name + '.xml'
    filepath = storing_dir + filename
    xml_tree = create_pokemon_xml(pokemon_data)
    xml_tree.write(filepath, encoding='utf-8', xml_declaration=True)


if __name__ == "__main__":
    data_sources = [
        ('../xml_data/bulbapedia_data/', '../data/bulbapedia_data', parse_bulbapedia_html),
    ]
    for source in data_sources:
        if not os.path.exists(source[0]):
            os.makedirs(source[0])
            print(f"Directory '{source[0]}' created.")
        else:
            print(f"Directory '{source[0]}' already exists.")

    for storing_dir, data_source, data_func in data_sources:
        i = 1
        for file in tqdm(os.listdir(data_source)):
            print("Parsing file " + file + "...")
            f = os.path.join(data_source, file)
            name = file.split('.')[0]
            if os.path.isfile(f) and i != 772:
                pokemon_data = data_func(f)
                save_pokemon_xml(pokemon_data, storing_dir, name)
            i += 1