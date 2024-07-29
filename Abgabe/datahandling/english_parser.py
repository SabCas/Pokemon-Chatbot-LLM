import requests
import re
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET


def fetch_pokemon_data(pokemon_name):
    url = f"https://bulbapedia.bulbagarden.net/wiki/{pokemon_name}_(Pokémon)"
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_p_text_between_tags(start_tag, end_tag, listlike=False):
    """
    Extracts text from <p> tags between start_tag and end_tag.
    """
    if not start_tag or not end_tag:
        return "One or both tags not found."

    current_tag = start_tag
    p_texts = []

    while current_tag and current_tag != end_tag:
        if current_tag.name == 'p':
            p_texts.append(current_tag.get_text())
        current_tag = current_tag.find_next()

    if listlike:
        clean_list = [re.sub(r'[\d+]', '', element.strip().replace('\u2060', ''))
                      for element in p_texts if len(element.strip()) > 0]
        return clean_list

    info_text = ' '.join(p_texts)
    info_text = ' '.join(info_text.split()).replace('\u2060', '')
    cleaned_biology = re.sub(r'[\d+]', '', info_text)

    return cleaned_biology

def get_name(soup):
    return soup.find('h1', {'id': 'firstHeading'}).text.strip()[:-10]


def get_dex_number(soup):
    return soup.find_all('a', {'title': 'List of Pokémon by National Pokédex number'})[1].text.strip()[1:]

def get_category(soup):
    return soup.find('a', {'title': 'Pokémon category'}).text.strip()

def get_type(soup):
    type_section = soup.find('a', {'title': 'Type'}).parent
    # Only get the first two types as the other types are for different forms
    type_list = type_section.find_next_sibling('table').find_all('b')[0:2]
    pokemon_type = [type.text.strip() for type in type_list if 'Unknown' != type.text.strip()]
    return pokemon_type

def get_introduction(soup):
    intro_first_tag = soup.find('a', {'title': 'List of Pokémon by base friendship'})
    intro_end_tag = soup.find('a', {'href': '#Biology'})
    introduction = extract_p_text_between_tags(intro_first_tag, intro_end_tag)
    return introduction

def get_ability(soup, name):
    abilities_section = soup.find('a', {'title': 'Ability'}).parent
    abilities_list_parent = abilities_section.find_next_sibling('table').find_all('td')
    # The found section is more encapsuled as usual so we call parent ones more.
    if abilities_list_parent is None:
        abilities_list_parent = abilities_section.parent.find_next_sibling('table').find_all('td')

    normal_abilities = []
    hidden_ability = ""
    name_length = len(name)
    for row in abilities_list_parent:
        if row.find('span'):
            # For some Pokemon all Abilities are written in a line
            ability_row = row.find_all('span')
            hidden = ''
            # Check needed if the Pokemon does not have a hidden ability
            if row.find('small'):
                hidden = row.find('small').text.strip()

            if len(ability_row) == 1:
                # The html uses \xa0 instead of a whitespace
                ability = ability_row[0].text.strip().replace('\xa0', ' ')
                # Not a valid Ability for Pokemon
                if ability == 'Cacophony':
                    continue
                # Case for normal abilities
                if hidden == name:
                    normal_abilities.append(ability)
                # Case for hidden abilities
                elif 'Hidden Ability' in hidden:
                    hidden_ability = ability
                # Case if the Pokemon does not have any hidden abilities
                elif hidden == '':
                    normal_abilities.append(ability)
                # Special case if the hidden ability is defined for multiple Pokemon forms
                elif 'Hidden Ability' in hidden and name == hidden[0:name_length]:
                    hidden_ability = ability
                # Special case for the Pokemon Shaymin
                elif hidden == 'Land Forme' or hidden == 'Sky Forme':
                    normal_abilities.append(ability)
                # Special case for the Pokemon Zygarde
                elif 'Forme' in hidden and ability not in normal_abilities:
                    normal_abilities.append(ability)
                # Special case for the Pokemon Gimmighoul
                elif 'Chest Form' in hidden or 'Roaming Form' in hidden:
                    normal_abilities.append(ability)
                # Special case for the Pokemon Terapagos
                elif hidden == 'Normal Form':
                    normal_abilities.append(ability)
            else:
                # If multiple abilities are in the same row the Pokemon name is missing or in brackets if it has multiple forms.
                if hidden == '('+name+')' or hidden == '':
                    normal_abilities.append(ability_row[0].text.strip().replace('\xa0', ' '))
                    normal_abilities.append(ability_row[1].text.strip().replace('\xa0', ' '))
                # Special case for the Pokemon Zygarde for the second ability
                elif ability_row[1].text == '*':
                    normal_abilities.append(ability_row[0].text.strip())
                # Special case for the Pokemon Ogerpon
                elif hidden == '(Teal Mask)':
                    normal_abilities.append(ability_row[0].text.strip())

    abilities = [normal_abilities]
    if hidden_ability != "":
        abilities.append(hidden_ability)
    return abilities

def get_stats(soup):
    stats_section = soup.findAll('th', {
        'style': 'padding-left: 0.2em; padding-right: 0.2em; display: flex; justify-content: space-between;'})
    # Only keep the stats of the newest Version
    while len(stats_section) > 6:
        stats_section.pop(0)
    stats = {}
    for row in stats_section:
        stat = row.text.strip().split(':')
        stat_name = stat[0].replace(' ', '')  # Remove white spaces for Sp. Attack and Sp. Defense
        stats[stat_name] = stat[1]
    return stats

def get_egg_data(soup):
    eggs = {}
    egg_section = soup.find('a', {'href': '/wiki/Egg_Group'}).parent

    egg_list = egg_section.find_next_sibling('table').find_all('a')
    egg_group = [egg.text.strip() for egg in egg_list if egg.text.strip() not in ['Cap', 'Cosplay']]
    eggs["EggGroup"] = egg_group

    hatch_section = soup.find('a', {'href': '/wiki/Egg_cycle'}).parent.parent
    hatch = hatch_section.find('td').text.strip().replace('\xa0', ' ').replace('\n', ' ')
    eggs["HatchTime"] = [hatch]
    return eggs

def get_gender(soup):
    gender_section = soup.find('a', {'title': 'List of Pokémon by gender ratio'}).parent
    gender_list = gender_section.find_next_sibling('table').find_all('td')
    gender = []
    for entry in gender_list:
        if ('male' in entry.text.strip() or 'female' in entry.text.strip() or "unknown" in entry.text.strip()):
            gender.append(entry.text.strip())
    return gender

def get_physique(soup):
    height_section = soup.find('a', {'title': 'List of Pokémon by height'}).parent
    # first element is in m and not feet
    height = height_section.find_next_sibling('table').find_all('td')[1].text.strip()

    # Weight
    weight_section = soup.find('a', {'title': 'Weight'}).parent
    # first element is in lbs and not kg
    weight = weight_section.find_next_sibling('table').find_all('td')[1].text.strip()
    physique = [height, weight]
    return physique

def get_biology(soup):
    biology_section = soup.find(id='Biology')
    biology = []
    if biology_section:
        current_elem = biology_section.find_next()
        while current_elem and current_elem.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if current_elem.name in ['p']:
                current_biology = current_elem.text.strip().replace('\n', '')
                biology.append(re.sub(r'[\d+]', '', current_biology))
            current_elem = current_elem.find_next()
    return biology

def get_evolution(soup, name):
    evolution_section = soup.find('span', id='Evolution')
    evolution_line = []
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
    # The Pokemon is the only Pokemon in the evolution line
    else:
        evolution_line.append(name)
    return evolution_line

def get_form(soup, name):
    forms = []
    form_section = soup.find('a', title='Pokémon category').parent.find_next('table')
    if form_section:
        for row in form_section.find_all('small'):
            # Replace empty space declaration of html file
            current_elem = row.text.strip().replace('\xa0', ' ')
            # Skip included elements
            if current_elem in forms:
                pass
            # Skip empty element
            elif current_elem == "":
                pass
            # Skip Base name element
            elif current_elem == name:
                pass
            else:
                forms.append(current_elem)
    return forms

def get_pokedex_entries(soup):
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
    return pokedex_entries

def get_major_appearances(soup):
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
            if sibling.name == "h4" and sibling.text.strip() == "Minor appearances":
                break
    major_appearances = {}
    content = ""
    for i in range(len(major_appearances_content)):
        if i <= len(major_appearances_title) - 1:
            major_appearances[major_appearances_title[i]] = major_appearances_content[i]
        else:
            if len(major_appearances_title) == 0:
                major_appearances['Other'] = content + " " + major_appearances_content[i]
            else:
                major_appearances[major_appearances_title[len(major_appearances_title)-1]] = content + " " + major_appearances_content[i]
    return major_appearances


def get_learnset(soup):
    level_up_moves_section = soup.find('span', {'id': 'By_leveling_up'}).parent
    level_up_moves_table = level_up_moves_section.find_next('table')

    # Extract the moves learned by level up
    level_up_moves = []
    i = 0
    for row in level_up_moves_table.find_all('tr')[1:]:  # Skip the header row
        cells = row.find_all('td')
        if len(cells) >= 7:
            if i == 0:
                i = i + 1
                continue
            level = cells[0].find('span').text.strip()
            if level[0] == '0':
                level = level[1:]
            elif level == 'Evo.':
                level = '0'
            elif level == 'Rem.':
                level = '999'
            move_name = cells[1].text.strip()
            move_type = cells[2].text.strip()
            move_category = cells[3].text.strip()
            power = cells[4].find('span').text.strip()
            if power[0] == '0':
                power = power[1:]
            if power == '000':
                power = '0'
            accuracy = cells[5].find('span').text.strip() + '%'
            if accuracy == "00—%":
                accuracy = "101%"
            if accuracy[0] == '0':
                accuracy = accuracy[1:]
            pp = cells[6].text.strip()
            level_up_moves.append((int(level), move_name, move_type, move_category, int(power), accuracy, int(pp)))

    # TM moves
    tm_moves_section = soup.find('span', {'id': 'By_TM'})
    tm_moves = []
    if tm_moves_section:
        tm_moves_parent = tm_moves_section.parent
        tm_moves_table = tm_moves_parent.find_next('table')

        i = 0
        for row in tm_moves_table.find_all('tr')[1:]:  # Skip the header row
            cells = row.find_all('td')
            if len(cells) >= 8:
                if i == 0:
                    i = i + 1
                    continue
                if cells[1].text.strip() == cells[2].text.strip():
                    cells = cells[1:]  # Somehow duplicate tm name
                tm_number = cells[1].text.strip()
                move_name = cells[2].text.strip()
                move_type = cells[3].text.strip()
                move_category = cells[4].text.strip()
                power = cells[5].find('span').text.strip()
                if power[0] == '0':
                    power = power[1:]
                if power == '000':
                    power = '0'
                accuracy = cells[6].find('span').text.strip()[:-2] + '%'
                if accuracy == "00—%":
                    accuracy = "101%"
                if accuracy[0] == '0':
                    accuracy = accuracy[1:]
                pp = cells[7].text.strip()
                tm_moves.append((tm_number, move_name, move_type, move_category, int(power), accuracy, int(pp)))

    learnset = [level_up_moves, tm_moves]
    return learnset


def get_trivia(soup):
    trivias_section = soup.find('span', {'id': 'Trivia'}).parent
    trivias_list = trivias_section.find_next('ul')

    # Extract the trivias items
    trivias = []
    for item in trivias_list.find_all('li'):
        trivias.append(item.text.strip().replace('\n', ''))
    return trivias

def main(bulbapedia_html):
    # Create Soup out of html
    bulbapedia_soup = BeautifulSoup(bulbapedia_html, 'html.parser')
    name = get_name(bulbapedia_soup)

    data = {
        'name': name,
        'dex_number': get_dex_number(bulbapedia_soup),
        'category': get_category(bulbapedia_soup),
        'type': get_type(bulbapedia_soup),
        'introduction': get_introduction(bulbapedia_soup),
        'abilities': get_ability(bulbapedia_soup, name),
        'stats': get_stats(bulbapedia_soup),
        'eggs': get_egg_data(bulbapedia_soup),
        'gender': get_gender(bulbapedia_soup),
        'physique': get_physique(bulbapedia_soup),
        'biology': get_biology(bulbapedia_soup),
        'evolution_line': get_evolution(bulbapedia_soup, name),
        'forms': get_form(bulbapedia_soup, name),
        'pokedex_entries': get_pokedex_entries(bulbapedia_soup),
        'major_appearances': get_major_appearances(bulbapedia_soup),
        'learnset': get_learnset(bulbapedia_soup),
        'trivias': get_trivia(bulbapedia_soup),
    }
    return data

if __name__ == "__main__":
    #data_sources = [
    #    ('../xml_data/bulbapedia_data/', '../data/bulbapedia_data', parse_bulbapedia_html),
    #]
    #for source in data_sources:
    #    if not os.path.exists(source[0]):
    #        os.makedirs(source[0])
    #        print(f"Directory '{source[0]}' created.")
    #    else:
    #        print(f"Directory '{source[0]}' already exists.")

    #for storing_dir, data_source, data_func in data_sources:
    #    i = 1
    #    for file in tqdm(os.listdir(data_source)):
    #        print("Parsing file " + file + "...")
    #        f = os.path.join(data_source, file)
    #        name = file.split('.')[0]
    #        if os.path.isfile(f) and i != 772:
    #            pokemon_data = data_func(f)
    #            save_pokemon_xml(pokemon_data, storing_dir, name)
    #        i += 1

    file = "../data/bulbapedia_data/0718_Zygarde.html"
    f = open(file, encoding="utf8")
    main(f)