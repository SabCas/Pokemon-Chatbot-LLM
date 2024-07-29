import re
from bs4 import BeautifulSoup

def get_type(soup):
    """
    Extracts the type(s) of a Pokémon from the HTML.
    """
    table = soup.find_all('dl', {'class': 'dl-horizontal'})[0]
    for entry in table.find_all('dt'):
        if entry.text != 'Typ':
            continue
        return [type_img.get('alt').strip() for type_img in entry.find_next().find_all('img')]

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
        clean_list = [re.sub(r'\[\d+\]', '', element.strip().replace('\u2060', ''))
                      for element in p_texts if len(element.strip()) > 0]
        return clean_list

    info_text = ' '.join(p_texts)
    info_text = ' '.join(info_text.split()).replace('\u2060', '')
    cleaned_biology = re.sub(r'\[\d+\]', '', info_text)
    
    return cleaned_biology

def get_data_from_table(soup, table_id, desired_data):
    """
    Retrieves specific data from a table identified by table_id.
    """
    table = soup.find_all('dl', {'class': 'dl-horizontal'})[table_id]
    for entry in table.find_all('dt'):
        if entry.text != desired_data:
            continue
        return entry.find_next().text

def get_appearances(soup):
    """
    Extracts appearance data (series and movies) of a Pokémon.
    """
    appearances = {'Serie':[],
                   'Filme und Spezialfilme': []}

    for title in soup.find_all('h4'):
        if title.text != 'Serie':
            continue
        for list_element in title.find_next().find_all('li')[1::2]:
            le_text = list_element.text.strip()
            le_text = le_text[le_text.find(' ') + 1:]
            if le_text not in appearances[title.text]:
                appearances[title.text].append(le_text)

    for title in soup.find_all('h4'):
        if title.text != 'Filme und Spezialfilme':
            continue
        for list_element in title.find_next().find_all('li'):
            le_text = list_element.text.strip().split('\n')[0]
            if le_text not in appearances[title.text]:
                appearances[title.text].append(le_text)

    return appearances

def get_trivias(soup):
    """
    Extracts trivia information of a Pokémon.
    """
    for title in soup.find_all('h3'):
        if title.text != 'Trivia':
            continue
        if title.find_next().text.strip().split('\n') is not None:
            return title.find_next().text.strip().split('\n')
    return []

def get_gender_ratio(soup):
    """
    Extracts gender ratio of a Pokémon.
    """
    gender_str = get_data_from_table(soup, 0, 'Geschlecht').strip()
    if 'Kein Geschlecht' in gender_str:
        return gender_str
    oitar = ' '.join(gender_str.replace('♀', 'weiblich').replace('♂', 'männlich').split()[::-1])
    ratio = ' - '.join(oitar.split(' - ')[::-1])
    return ratio

def get_evolutions(soup):
    """
    Extracts evolution information of a Pokémon.
    """
    evo_list = []
    for s in soup.find('div', id='evoRow').find_all('div', class_='valignBottom'):
        name = s.text.strip()
        if 'Mega-' in name or 'Gigadynamax-' in name or 'Alola-' in name or 'Galar-' in name:
            continue
        evo_list.append(name)
    return evo_list

def get_forms(soup):
    """
    Extracts different forms of a Pokémon.
    """
    forms = []
    if soup.find('div', id='sonder') is None:
        return []
    
    if soup.find('div', id='sonder').find('h2') is None:
        for a in soup.find('div', id='sonder').find('div', id='bilderdex').find_all('a'):
            forms.append(a.text.strip())
        return forms

    if soup.find('div', id='sonder').find('ul', class_='nav-tabs'):
        for element in soup.find('div', id='sonder').find('ul').find_all('li'):
            forms.append(element.text.strip())
        return forms
    else:
        name = soup.find('div', id='sonder').find('h2').text.strip()
        return [name]

def get_abilities(soup):
    """
    Extracts abilities of a Pokémon.
    """
    ability1 = get_data_from_table(soup, 1, 'Fähigkeit 1').strip()
    ability2 = get_data_from_table(soup, 1, 'Fähigkeit 2').strip()
    hidden_ability = get_data_from_table(soup, 1, 'Versteckte Fähigkeit').strip()
    if ability2 == 'Keine':
        return [[ability1], hidden_ability]
    return [[ability1, ability2], hidden_ability]

def get_stats(soup):
    """
    Extracts stats of a Pokémon.
    """
    result = {}
    for title in soup.find_all('h3'):
        if title.text.strip() != 'Statuswerte':
            continue
        div_tag = title.find_next()
        for row in div_tag.find_all('tr')[2:-1]:
            values = row.find_all('td')
            result[values[0].text.strip().replace('‑','')] = int(values[2].text.strip())
    return result

def get_physique(soup):
    """
    Extracts height and weight of a Pokémon.
    """
    height = get_data_from_table(soup, 0, 'Größe').strip().replace('Meter', 'm')
    weight = get_data_from_table(soup, 0, 'Gewicht').strip().replace('Kilogramm', 'kg')
    return height, weight

def get_attacks(soup):
    """
    Extracts attack moves of a Pokémon.
    """
    attack_dict = {}
    
    found_attack_divs = []
    for right_title in soup.find_all('h4'):
        if right_title.text.strip() not in ['Durch Level-Up', 'Durch TMs']:
            continue
        else:
            found_attack_divs.append(right_title.find_next())
    

    for learn_typ, div in zip(['levelup', 'tm'], found_attack_divs):
        table = div.find('tbody')
        attack_dict[learn_typ] = []
        if table is None:
            continue
        for row in table.find_all('tr'):
            values = row.find_all('td')
            lvl = values[0].text.strip()
            name = values[1].find('a').text.strip()
            try:
                typ = values[2].find('img').get('alt')
                kat = values[3].find('img').get('title')
            except:
                typ = 'Psycho'
                kat = 'Status'
            power = values[4].text.strip()
            prec = values[5].text.strip()
            ap = values[6].text.strip()
            attack_dict[learn_typ].append([lvl, name, typ, kat, power, prec, ap])
    return attack_dict

def main(bisafans_html, pokewiki_html):
    """
    Main function to create BeautifulSoup objects and extract data using all defined functions.
    """
    bisafans_soup = BeautifulSoup(bisafans_html, 'html.parser')
    pokewiki_soup = BeautifulSoup(pokewiki_html, 'html.parser')

    # Locate the start and end tags for the intro and biology sections
    intro_first_tag = pokewiki_soup.find('table', {'class': 'infobox-pokemon'})
    intro_end_tag = pokewiki_soup.find('div', {'id': 'toc'})

    biology_first_tag = pokewiki_soup.find('span', {'id': 'Spezies'})
    if 'id="In_den_Hauptspielen"' in pokewiki_html:
        biology_end_tag = pokewiki_soup.find('span', {'id': 'In_den_Hauptspielen'})
    else:
        biology_end_tag = pokewiki_soup.find('span', {'id': 'In_den_Spielen'})

    # Ensure the tags were found before proceeding
    if not intro_first_tag or not intro_end_tag or not biology_first_tag or not biology_end_tag:
        raise ValueError("One or more tags not found in the provided HTML.")

    # Extract data using the defined functions
    data = {
        "type": get_type(bisafans_soup),
        "intro": extract_p_text_between_tags(intro_first_tag, intro_end_tag),
        "biologies": extract_p_text_between_tags(biology_first_tag, biology_end_tag, True),
        "appearances": get_appearances(bisafans_soup),
        "trivias": get_trivias(bisafans_soup),
        "gender": get_gender_ratio(bisafans_soup),
        "evolutions": get_evolutions(bisafans_soup),
        "forms": get_forms(bisafans_soup),
        "abilities": get_abilities(bisafans_soup),
        "stats": get_stats(bisafans_soup),
        "physique": get_physique(bisafans_soup),
        "attacks": get_attacks(bisafans_soup),
        'category': get_data_from_table(bisafans_soup, 0, 'Art')
    }

    return data
