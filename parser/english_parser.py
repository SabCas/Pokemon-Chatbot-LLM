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


def main(bulbapedia_html):
    # Create Soup out of html
    soup = BeautifulSoup(bulbapedia_html, 'html.parser')

    # Extract Pokémon name
    pokemon_name = soup.find('h1', {'id': 'firstHeading'}).text.strip()

    # Extractr Pokemon id
    dex_number = soup.find_all('a', {'title': 'List of Pokémon by National Pokédex number'})[1].text.strip()[1:]

    # Category
    category = soup.find('a', {'title': 'Pokémon category'}).text

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

    # Physique
    # Height
    height_section = soup.find('a', {'title': 'List of Pokémon by height'}).parent
    # first element is in m and not feet
    height = height_section.find_next_sibling('table').find_all('td')[1].text

    # Weight
    weight_section = soup.find('a', {'title': 'Weight'}).parent
    # first element is in m and not feet
    weight = weight_section.find_next_sibling('table').find_all('td')[1].text
    physique = [height, weight]


    # Biology
    biology_section = soup.find(id='Biology')
    biology = []
    if biology_section:
        current_elem = biology_section.find_next()
        while current_elem and current_elem.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if current_elem.name in ['p']:
                biology.append(current_elem.text)
            current_elem = current_elem.find_next()

    # Evolution
    evolution_section = soup.find('span', id='Evolution')
    evolution_line = [] # TODO: decide if the evolution line should appear if its only 1 pokemon#[pokemon_name]
    if evolution_section:
        evolution_parent = evolution_section.parent
        evolution_table = evolution_parent.find_next('table')

        evolution_line = []
        for row in evolution_table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            for cell in cells:
                test = cell.find_all('a')
                if len(test) >= 2:
                    version = test[0].text.strip()
                    evolution_line.append(version)

        evolution_line = list(dict.fromkeys(evolution_line))
        if ('' in evolution_line):
            evolution_line.remove('')
        # print(evolution_line)

    # Forms
    unfiltered_forms = []
    forms = []
    form_section = soup.find('span', id='Forms')
    if form_section:
        form_parent = form_section.parent
        form_table = form_section.find_next('table')

        for row in form_table.find_all('tr'):  # Skip the header row
            cells = row.find_all('td')
            for cell in cells:
                if len(cell) > 0:
                    version = ""
                    for t in cell:
                        version = version + t.text.strip()
                    unfiltered_forms.append(version)

        for form in unfiltered_forms:
            j = form.replace(' ', '')
            forms.append(j)
        forms = list(dict.fromkeys(forms))
        if ('' in forms):
            forms.remove('')



    # Pokedex
    pokedex_entries_section = soup.find('span', {'id': 'Pok.C3.A9dex_entries'}).parent
    pokedex_table = pokedex_entries_section.find_next('table')

    # Extract the Pokédex entries
    pokedex_entries = []
    for row in pokedex_table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) >= 2:
            version = cells[0].text.strip()
            entry = cells[1].text.strip()
            pokedex_entries.append((version, entry))


    # Major Appearances
    # Find the "Major appearances" section
    major_appearances_header = soup.find(id="Major_appearances")

    # Collect the paragraphs under the "Major appearances" section
    major_appearances_title = []
    major_appearances_content = []
    if major_appearances_header:
        for sibling in major_appearances_header.parent.find_next_siblings():
            if sibling.name == "h2":
                break
            if sibling.name == "p":
                major_appearances_content.append(sibling.text.strip())
            if sibling.name == "h5":
                major_appearances_title.append(sibling.text.strip())
            if sibling.name == "h4" and sibling.text == "Minor appearances":
                break

    major_appearances = (major_appearances_title, major_appearances_content)

    # Pokemon Learn set
    # Level up moves
    level_up_moves_section = soup.find('span', {'id': 'By_leveling_up'}).parent
    level_up_moves_table = level_up_moves_section.find_next('table')

    # Extract the moves learned by level up
    level_up_moves = []
    for row in level_up_moves_table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) >= 7:
            level = cells[0].find('span').text.strip()
            #print(level)
            move_name = cells[1].text.strip()
            move_type = cells[2].text.strip()
            move_category = cells[3].text.strip()
            power = cells[4].find('span').text.strip()
            accuracy = cells[5].find('span').text.strip()
            if (accuracy == "00—"):
                accuracy = "—"
            pp = cells[6].text.strip()
            if(level== "" or move_name == "" or move_type == "" or move_category == "" or power == "" or accuracy == "" or pp == ""):
                continue
            level_up_moves.append((level, move_name, move_type, move_category, power, accuracy, pp))

    # TM moves
    tm_moves_section = soup.find('span', {'id': 'By_TM'})
    tm_moves = []
    if tm_moves_section:
        tm_moves_parent = tm_moves_section.parent
        tm_moves_table = tm_moves_parent.find_next('table')

        for row in tm_moves_table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            if len(cells) >= 6:
                tm_number = cells[1].text.strip()
                move_name = cells[2].text.strip()
                move_type = cells[3].text.strip()
                move_category = cells[4].text.strip()
                power = cells[5].find('span').text.strip()
                accuracy = cells[6].find('span').text.strip()[:-2]
                if (accuracy == "00—"):
                    accuracy = "—"
                pp = cells[7].text.strip() if len(cells) > 6 else 'N/A'  # Sometimes PP might be missing
                tm_moves.append((tm_number, move_name, move_type, category, power, accuracy, pp))

    learnset = [level_up_moves, tm_moves]

    # Trivia
    trivia_section = soup.find('span', {'id': 'Trivia'}).parent
    trivia_list = trivia_section.find_next('ul')

    # Extract the trivia items
    trivia = []
    for item in trivia_list.find_all('li'):
        trivia.append(item.text.strip())

    return {
        'name': pokemon_name,
        'dex_number': dex_number,
        'category': category,
        'type': types,
        'abilities': abilities,
        'stats': stats,
        'eggs' : eggs,
        'gender' : gender,
        'physique' : physique,
        'biology' : biology,
        'evolution_line': evolution_line,
        'forms': forms,
        'pokedex_entries':pokedex_entries,
        'major_appearances': major_appearances,
        'learnset': learnset,
        'trivias': trivia,
    }


def create_pokemon_xml(pokemon_data):
    root = ET.Element('pokemon')

    # Names in different Languages
    name_elem = ET.SubElement(root, 'name')
    name_elem.text = pokemon_data['name']

    # dex number
    id_elem = ET.SubElement(root, 'id')
    id_elem.text = pokemon_data['dex_number']

    # Category
    category_elem = ET.SubElement(root, 'category')
    category_elem.text = pokemon_data['category']

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

     # Pokemon Gender Information
    gender_elem = ET.SubElement(game_elem, 'gender')
    for entry in pokemon_data['gender']:
        gender = ET.SubElement(gender_elem, 'ratio')
        gender.text = entry

    # Physique
    physique_elem = ET.SubElement(game_elem, 'physique')
    height_elem = ET.SubElement(physique_elem, 'height')
    height_elem.text = pokemon_data['physique'][0]
    weight_elem = ET.SubElement(physique_elem, 'weight')
    weight_elem.text = pokemon_data['physique'][1]

    # Learn set
    # LevelUp Moves
    learnset_elem = ET.SubElement(game_elem, 'learnset')
    for entry in pokemon_data['learnset'][0]:
        level_up_elem = ET.SubElement(learnset_elem, 'level_move')
        for move in entry:
            move_elem = ET.SubElement(level_up_elem, 'move')
            move_elem.text = move
    for entry in pokemon_data['learnset'][0]:
        level_up_elem = ET.SubElement(learnset_elem, 'tm_move')
        for move in entry:
            move_elem = ET.SubElement(level_up_elem, 'move')
            move_elem.text = move

    # Evolution line
    evolution_elem = ET.SubElement(game_elem, 'evolution_line')
    for entry in pokemon_data['evolution_line']:
        evo_elem = ET.SubElement(evolution_elem, 'pokemon name')
        evo_elem.text = entry

    # Forms
    forms_elem = ET.SubElement(game_elem, 'forms')
    for entry in pokemon_data['forms']:
        form_elem = ET.SubElement(forms_elem, 'pokemon name')
        form_elem.text = entry

    # New Anime section
    anime_elem = ET.SubElement(root, 'anime')

    # Biology
    biology_elem = ET.SubElement(anime_elem, 'biology')
    for entry in pokemon_data['biology']:
        biology = ET.SubElement(biology_elem, 'p')
        biology.text = entry


    # Pokedex Entrys of the various games
    pokedex_elem = ET.SubElement(anime_elem, 'pokedex')
    for entry in pokemon_data['pokedex_entries']:
        dex_elem = ET.SubElement(pokedex_elem, entry[0])
        dex_elem.text = entry[1]

    # Major Appearances
    appearance_elem = ET.SubElement(anime_elem, 'appearances')
    for i in range(len(pokemon_data['major_appearances'])):
        if len(pokemon_data['major_appearances'][0]) -1 <= i:
            app_elem = ET.SubElement(appearance_elem, entry[1])
        else:
            app_elem = ET.SubElement(appearance_elem, 'info')
        app_elem.text = entry[1]
    #for entry in pokemon_data['major_appearances']:
    #    print(entry)
    #    if len(entry[1]) != 0:
    #        app_elem = ET.SubElement(appearance_elem, entry[1])
    #    else:
    #        app_elem = ET.SubElement(appearance_elem, 'info')


    # Trivia
    trivia_elem = ET.SubElement(anime_elem, 'trivia')
    for entry in pokemon_data['trivia']:
        triv_elem = ET.SubElement(trivia_elem, 'info')
        triv_elem.text = entry

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

    #file = "../data/bulbapedia_data/0025_Pikachu.html"
    #test = parse_bulbapedia_html(file)
    #save_pokemon_xml(test, "", "test")