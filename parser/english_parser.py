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

def main(bulbapedia_html):
    # Create Soup out of html
    soup = BeautifulSoup(bulbapedia_html, 'html.parser')

    # Extract Pokémon name
    pokemon_name = soup.find('h1', {'id': 'firstHeading'}).text.strip()[:-10]

    # Extract Pokemon id
    dex_number = soup.find_all('a', {'title': 'List of Pokémon by National Pokédex number'})[1].text.strip()[1:]

    # Category
    category = soup.find('a', {'title': 'Pokémon category'}).text.strip()

    # Extract Pokémon type(s)
    type_section = soup.find('a', {'title': 'Type'}).parent
    type_list = type_section.find_next_sibling('table').find_all('b')
    type = [type.text.strip() for type in type_list if 'Unknown' != type.text.strip()]

    # Introduction
    intro_first_tag = soup.find('a', {'title': 'List of Pokémon by base friendship'})
    intro_end_tag = soup.find('a', {'href': '#Biology'})
    introduction = extract_p_text_between_tags(intro_first_tag, intro_end_tag)

    # Extract Pokémon abilities
    abilities_section = soup.find('a', {'title': 'Ability'}).parent
    abilities_list_parent = abilities_section.find_next_sibling('table').find_all('td')
    hidden_abilities_list = abilities_section.find_next_sibling('table').find_all('small')

    normal_abilities = []
    hidden_ability = ""
    for row in abilities_list_parent:
        if row.find('small'):
            if row.find('small').text.strip() == 'Hidden Ability' and row.find('a').text.strip() != 'Cacophony':
                hidden_ability = row.find('a').text.strip()
        else:
            normal_abilities.append(row.text.strip())

    abilities = [normal_abilities]
    if hidden_ability != "":
        abilities.append(hidden_ability)

    # Extract Pokémon stats (assuming they are in the first table with class 'roundy')
    stats_section = soup.findAll('th', {
        'style': 'padding-left: 0.2em; padding-right: 0.2em; display: flex; justify-content: space-between;'})
    # TODO: add stats for every gen
    # Only keep the stats of the newest Version
    while len(stats_section) > 6:
        stats_section.pop(0)
    stats = {}
    for row in stats_section:
        stat = row.text.strip().split(':')
        stat_name = stat[0].replace(' ', '')  # Remove white spaces for Sp. Attack and Sp. Defense
        stats[stat_name] = stat[1]

    # Egg Data
    eggs = {}
    egg_section = soup.find('a', {'href': '/wiki/Egg_Group'}).parent

    egg_list = egg_section.find_next_sibling('table').find_all('a')
    egg_group = [egg.text.strip() for egg in egg_list if egg.text.strip() not in ['Cap', 'Cosplay']]
    eggs["EggGroup"] = egg_group

    hatch_section = soup.find('a', {'href': '/wiki/Egg_cycle'}).parent.parent
    hatch = hatch_section.find('td').text.strip().replace('\xa0', ' ').replace('\n', ' ')
    eggs["HatchTime"] = [hatch]

    # Gender
    gender_section = soup.find('a', {'title': 'List of Pokémon by gender ratio'}).parent
    gender_list = gender_section.find_next_sibling('table').find_all('td')
    gender = []
    for entry in gender_list:
        if ('male' in entry.text.strip() or 'female' in entry.text.strip() or "unknown" in entry.text.strip()):
            gender.append(entry.text.strip())

    # Physique
    # Height
    height_section = soup.find('a', {'title': 'List of Pokémon by height'}).parent
    # first element is in m and not feet
    height = height_section.find_next_sibling('table').find_all('td')[1].text.strip()

    # Weight
    weight_section = soup.find('a', {'title': 'Weight'}).parent
    # first element is in m and not feet
    weight = weight_section.find_next_sibling('table').find_all('td')[1].text.strip()
    physique = [height, weight]

    # Biology
    biology_section = soup.find(id='Biology')
    biology = []
    if biology_section:
        current_elem = biology_section.find_next()
        while current_elem and current_elem.name not in ['h2', 'h3', 'h4', 'h5', 'h6']:
            if current_elem.name in ['p']:
                biology.append(current_elem.text.strip().replace('\n', ''))
            current_elem = current_elem.find_next()

    # Evolution
    evolution_section = soup.find('span', id='Evolution')
    evolution_line = []  # TODO: decide if the evolution line should appear if its only 1 pokemon#[pokemon_name]
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
            if sibling.name == "h4" and sibling.text.strip() == "Minor appearances":
                break
    major_appearances = {}
    content = ""
    for i in range(len(major_appearances_content)):
        if i <= len(major_appearances_title) - 1:
            major_appearances[major_appearances_title[i]] = major_appearances_content[i]
        else:
            major_appearances[major_appearances_title[len(major_appearances_title)-1]] = content + " " + major_appearances_content[i]

    # Pokemon Learn set
    # Level up moves
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
            move_name = cells[1].text.strip()
            move_type = cells[2].text.strip()
            move_category = cells[3].text.strip()
            power = cells[4].find('span').text.strip()
            if power[0] == '0':
                power = power[1:]
            if power == '000':
                power = '0'
            accuracy = cells[5].find('span').text.strip() + '%'
            if accuracy == "00—":
                accuracy = "999"
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
            if len(cells) >= 6:
                if i == 0:
                    i = i + 1
                    continue
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
                if accuracy == "00—":
                    accuracy = "999"
                if accuracy[0] == '0':
                    accuracy = accuracy[1:]
                pp = cells[7].text.strip()
                tm_moves.append((tm_number, move_name, move_type, move_category, int(power), accuracy, int(pp)))

    learnset = [level_up_moves, tm_moves]

    # trivias
    trivias_section = soup.find('span', {'id': 'Trivia'}).parent
    trivias_list = trivias_section.find_next('ul')

    # Extract the trivias items
    trivias = []
    for item in trivias_list.find_all('li'):
        trivias.append(item.text.strip().replace('\n', ''))

    return {
        'name': pokemon_name,
        'dex_number': dex_number,
        'category': category,
        'type': type,
        'introduction': introduction,
        'abilities': abilities,
        'stats': stats,
        'eggs': eggs,
        'gender': gender,
        'physique': physique,
        'biology': biology,
        'evolution_line': evolution_line,
        'forms': forms,
        'pokedex_entries': pokedex_entries,
        'major_appearances': major_appearances,
        'learnset': learnset,
        'trivias': trivias,
    }

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

    file = "../data/bulbapedia_data/0001_Bulbasaur.html"
    f = open(file, encoding="utf8")
    main(f)