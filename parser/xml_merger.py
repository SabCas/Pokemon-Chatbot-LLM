import os 
import xmltodict
import german_parser
import english_parser


bisafans_dir = 'bisafans_data'
pokewiki_dir = 'pokewiki_data'
bulbapedia_dir = 'bulbapedia_data'



for bisa_file_name, poke_file_name, bulba_file_name in zip(os.listdir(bisafans_dir), os.listdir(pokewiki_dir), os.listdir(bulbapedia_dir)):
    with open(os.path.join(bisafans_dir, bisa_file_name), 'r') as file:
        bisafans_html = file.read()
    with open(os.path.join(pokewiki_dir, poke_file_name), 'r') as file:
        pokewiki_html = file.read()
    with open(os.path.join(bulbapedia_dir, bulba_file_name), 'r') as file:
        bulbapedia_html = file.read()

    german_data = german_parser.main(bisafans_html, pokewiki_html)
    english_data = english_parser.main(bulbapedia_html)

    # Example dictionary
    data = {
        "Pokemon": {
        "Name": 'Pikachu',
        "ID": 25,
        "Types": {
            'EnglishType': {'Type': ['Grass','Poison']},
            'GermanType': {'Type': german_data['type']},
        },
        'Bisafans': {
            "Introduction": german_data['intro'],
            "Game": {

            },
            "Anime": {
                "Biology": {"P":[biology.replace('\n', ' ') for biology in german_data['biologies']]},
                "category": german_data['category'] +'-Pokemon',
                "Appearances": {
                    "Series": {'Episode': [episode for episode in german_data['appearances']['Serie']]},
                    "Films": {'Movie': [movie for movie in german_data['appearances']['Filme und Spezialfilme']]}
                },
                "Trivias": {'Trivia': [trivia for trivia in german_data['trivias']]},
            }
            
        }
        
        }
    }
    

# Convert dictionary to XML
xml_str = xmltodict.unparse(data, pretty=True)
with open('pika.xml', 'w') as writer:
    writer.write(xml_str)