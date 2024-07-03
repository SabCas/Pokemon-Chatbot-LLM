import os 
import xmltodict
import german_parser
import english_parser
from tqdm import tqdm



def main(data_directories, target_directory):
    bisafans_dir = data_directories[0]
    pokewiki_dir = data_directories[1]
    bulbapedia_dir = data_directories[2]

    os.makedirs(target_directory, exist_ok=True)

    for bisa_file_name, poke_file_name, bulba_file_name in tqdm(zip(sorted(os.listdir(bisafans_dir)), 
                                                            sorted(os.listdir(pokewiki_dir)), 
                                                            sorted(os.listdir(bulbapedia_dir))), total=1024):
        
        with open(os.path.join(bisafans_dir, bisa_file_name), 'r', encoding='utf-8') as file:
            bisafans_html = file.read()
        with open(os.path.join(pokewiki_dir, poke_file_name), 'r', encoding='utf-8') as file:
            pokewiki_html = file.read()
        with open(os.path.join(bulbapedia_dir, bulba_file_name), 'r', encoding='utf-8') as file:
            bulbapedia_html = file.read()

        store_path = os.path.join(target_directory, bisa_file_name[:4] + '.xml')
        if os.path.exists(store_path):
            continue
        #if '0772_Type' == bulba_file_name:
        #   continue
        
        german_data = german_parser.main(bisafans_html, pokewiki_html)
        english_data = english_parser.main(bulbapedia_html)


        # Example dictionary
        abilities_list_eng = [{'Name': ability, "Hidden": False} for ability in english_data['abilities'][0]]
        if len(english_data['abilities']) > 1:
            abilities_list_eng.append({'Name': english_data['abilities'][1], "Hidden": True})

        # Example dictionary
        abilities_list_ger = [{'Name': ability, "Hidden": False} for ability in german_data['abilities'][0]]
        abilities_list_ger.append({'Name': german_data['abilities'][1], "Hidden": True})


        data = {
            "Pokemon": {
            "Name": {
                'English': english_data['name'],
                'German': bisa_file_name[bisa_file_name.find('_')+1:-5]
            },
            "ID": int(f'1{english_data['dex_number']}') - 10000,
            "Types": {
                'EnglishType': {'Type': english_data['type']},
                'GermanType': {'Type': german_data['type']},
            },
            "EnglishData": {
                "Category": english_data['category'],
                "EvolutionLine": {'Name': [name for name in english_data['evolution_line']]},
                "Forms": {"Name": [name for name in english_data['forms']]},
                "Introduction": english_data['introduction'],
                "Biology": {'P': [biology for biology in english_data['biology']]},
                "Trivias": {'Trivia': [trivia for trivia in english_data['trivias']]},
                "Game": {
                    "Abilities": {
                        "Ability": abilities_list_eng,
                        },
                    "Stats": english_data['stats'],
                    "Physique": {
                        "Height": english_data["physique"][0],
                        "Weight": english_data["physique"][1],
                    },
                    "GenderRatio": english_data["gender"],
                    "LearnableAttacks": {
                        "LevelUp": {
                            "Attack": [{'Level': attack[0], 
                                        'MoveName': attack[1],  
                                        'Type': attack[2],  
                                        'Category': attack[3],  
                                        'Power': attack[4], 
                                        'Accuracy': attack[5],  
                                        'PP': attack[6]} for attack in english_data['learnset'][0]]
                                        },
                        'TechnicalMachine': {
                            "Attack": [{'Level': attack[0], 
                                        'MoveName': attack[1],  
                                        'Type': attack[2],  
                                        'Category': attack[3],  
                                        'Power': attack[4], 
                                        'Accuracy': attack[5],  
                                        'PP': attack[6]} for attack in english_data['learnset'][1]]
                                        },     
                    },
                },
                "Anime": {
                    "Appearance": [{'Title': appearance,
                                    'Summary': english_data['major_appearances'][appearance]
                    } for appearance in english_data['major_appearances']],
                },
            },
            'GermanData': {
                "Category": german_data['category'] + ' Pokémon',
                "EvolutionLine": {'Name': [name for name in german_data['evolutions']]},
                "Forms": {"Name": [name for name in german_data['forms']]},
                "Introduction": german_data['intro'],
                "Biology": {"P":[biology.replace('\n', ' ') for biology in german_data['biologies']]},
                "Trivias": {'Trivia': [trivia for trivia in german_data['trivias']]},
                "Game": {
                    "Abilities": {
                        "Ability": abilities_list_ger,
                        },
                    "Stats": german_data['stats'],
                    "Physique": {
                        "Height": german_data["physique"][0],
                        "Weight": german_data["physique"][1],
                    },
                    "GenderRatio": english_data["gender"],
                    "LearnableAttacks": {
                        "LevelUp": {
                            "Attack": [{'Level': attack[0], 
                                        'MoveName': attack[1],  
                                        'Type': attack[2],  
                                        'Category': attack[3],  
                                        'Power': attack[4], 
                                        'Accuracy': attack[5],  
                                        'PP': attack[6]} for attack in german_data['attacks']['levelup']]
                                        },
                        'TechnicalMachine': {
                            "Attack": [{'Level': attack[0], 
                                        'MoveName': attack[1],  
                                        'Type': attack[2],  
                                        'Category': attack[3],  
                                        'Power': attack[4], 
                                        'Accuracy': attack[5],  
                                        'PP': attack[6]} for attack in german_data['attacks']['tm']]
                                        },     
                    },
                },
                "Anime": {
                    "Appearances": {
                        "Series": {'Episode': [episode for episode in german_data['appearances']['Serie']]},
                        "Films": {'Movie': [movie for movie in german_data['appearances']['Filme und Spezialfilme']]}
                    },
                },
            },
            },
        }


        # Convert dictionary to XML
        xml_str = xmltodict.unparse(data, pretty=True)

        with open(store_path, 'w', encoding='utf-8') as writer:
            writer.write(xml_str)