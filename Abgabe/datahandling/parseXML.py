import os
import xml.etree.ElementTree as ET
from neo4j import GraphDatabase

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "yourPassword"

# Initialize Neo4j driver
driver = GraphDatabase.driver(uri, auth=(user, password))

def parse_and_import_xml(root):
    try:
        # Extract English name
        name_element_en = root.find('.//Name/English')
        if name_element_en is None:
            raise ValueError("English name not found in XML.")
        name_en = name_element_en.text.strip()

        # Extract German name
        name_element_de = root.find('.//Name/German')
        if name_element_de is None:
            raise ValueError("German name not found in XML.")
        name_de = name_element_de.text.strip()

        # Extract types for English
        types_en = []
        english_types_element = root.find('.//Types/EnglishType')
        if english_types_element is not None:
            types_elements_en = english_types_element.findall('Type')
            types_en = [t.text.strip() for t in types_elements_en]

        # Extract types for German
        types_de = []
        german_types_element = root.find('.//Types/GermanType')
        if german_types_element is not None:
            types_elements_de = german_types_element.findall('Type')
            types_de = [t.text.strip() for t in types_elements_de]

        # Extract abilities for both languages
        ability_en = root.find('.//EnglishData/Game/Abilities/Ability/Name')
        ability_en = ability_en.text.strip() if ability_en is not None else False
        hidden_en = root.find('.//EnglishData/GameAbilities/Abiity/Hidden')
        hidden_en = hidden_en.text.strip() == 'true' if hidden_en is not None else False

        ability_de = root.find('.//GermanData/Game/Abilities/Ability/Name')
        ability_de = ability_de.text.strip() if ability_de is not None else False
        hidden_de = root.find('.//GermanData/Game/Abilities/Ability/Hidden')
        hidden_de = hidden_de.text.strip() == 'true' if hidden_de is not None else False

        # Extract stats
        stats = {}
        stats_elements = root.findall('.//Stats/*')
        for stat in stats_elements:
            stat_name = stat.tag
            stat_value = int(stat.text.strip())
            stats[stat_name] = stat_value

        # Extract height, weight, gender ratio
        height_element = root.find('.//Physique/Height')
        height = height_element.text.strip() if height_element is not None else ''

        weight_element = root.find('.//Physique/Weight')
        weight = weight_element.text.strip() if weight_element is not None else ''

        gender_ratio_element = root.find('.//GenderRatio')
        gender_ratio = gender_ratio_element.text.strip() if gender_ratio_element is not None else ''

        # Extract biology for both languages
        biology_elements_en = root.findall('.//EnglishData/Biology/P')
        biology_en = '\n'.join(p.text.strip() for p in biology_elements_en)

        biology_elements_de = root.findall('.//GermanData/Biology/P')
        biology_de = '\n'.join(p.text.strip() for p in biology_elements_de)

        # Extract introduction for both languages
        introduction_element_en = root.find('.//EnglishData/Introduction')
        introduction_en = introduction_element_en.text.strip() if introduction_element_en is not None else ''

        introduction_element_de = root.find('.//GermanData/Introduction')
        introduction_de = introduction_element_de.text.strip() if introduction_element_de is not None else ''

        # Extract trivia for both languages
        trivia_elements_en = root.findall('.//EnglishData/Trivias/Trivia')
        trivia_en = '\n'.join(p.text.strip() for p in trivia_elements_en)

        trivia_elements_de = root.findall('.//GermanData/Trivias/Trivia')
        trivia_de = '\n'.join(p.text.strip() for p in trivia_elements_de)

        # Extract category
        category_element_en = root.find('.//EnglishData/Category')
        category_en = category_element_en.text.strip() if category_element_en is not None else ''

        category_element_de = root.find('.//GermanData/Category')
        category_de = category_element_de.text.strip() if category_element_de is not None else ''

        # Extract shiny variant
        shiny_variant_element = root.find('.//ShinyVariant')
        shiny_variant = shiny_variant_element.text.strip() if shiny_variant_element is not None else ''

        # Extract evolution line for English
        evolution_line_en = []
        evolution_line_element_en = root.find('.//EnglishData/EvolutionLine')
        if evolution_line_element_en is not None:
            evolution_names_en = evolution_line_element_en.findall('Name')
            evolution_line_en = [name.text.strip() for name in evolution_names_en]

        # Extract evolution line for German
        evolution_line_de = []
        evolution_line_element_de = root.find('.//GermanData/EvolutionLine')
        if evolution_line_element_de is not None:
            evolution_names_de = evolution_line_element_de.findall('Name')
            evolution_line_de = [name.text.strip() for name in evolution_names_de]

        # Extract attacks for English
        attacks_en = []
        english_attacks_element = root.find('.//EnglishData/Game/LearnableAttacks/LevelUp')
        if english_attacks_element is not None:
            attack_elements_en = english_attacks_element.findall('Attack')
            for attack_element in attack_elements_en:
                level = attack_element.find('Level').text.strip()
                move_name = attack_element.find('MoveName').text.strip()
                move_type = attack_element.find('Type').text.strip()
                category = attack_element.find('Category').text.strip()
                power = attack_element.find('Power').text.strip()
                accuracy = attack_element.find('Accuracy').text.strip()
                pp = attack_element.find('PP').text.strip()
                attacks_en.append({
                    'Level': level,
                    'MoveName': move_name,
                    'Type': move_type,
                    'Category': category,
                    'Power': power,
                    'Accuracy': accuracy,
                    'PP': pp
                })

        # Extract attacks for German
        attacks_de = []
        german_attacks_element = root.find('.//GermanData/Game/LearnableAttacks/LevelUp')
        if german_attacks_element is not None:
            attack_elements_de = german_attacks_element.findall('Attack')
            for attack_element in attack_elements_de:
                level = attack_element.find('Level').text.strip()
                move_name = attack_element.find('MoveName').text.strip()
                move_type = attack_element.find('Type').text.strip()
                category = attack_element.find('Category').text.strip()
                power = attack_element.find('Power').text.strip()
                accuracy = attack_element.find('Accuracy').text.strip()
                pp = attack_element.find('PP').text.strip()
                attacks_de.append({
                    'Level': level,
                    'MoveName': move_name,
                    'Type': move_type,
                    'Category': category,
                    'Power': power,
                    'Accuracy': accuracy,
                    'PP': pp
                })

        with driver.session() as session:
            session.write_transaction(create_pokemon, name_en, name_de, types_en, types_de, ability_en, ability_de, hidden_en, hidden_de, stats, height, weight, gender_ratio, biology_en, biology_de, introduction_en, introduction_de, trivia_en, trivia_de, category_en, category_de, shiny_variant, evolution_line_en, evolution_line_de, attacks_en, attacks_de)
    except Exception as e:
        print(f"Error parsing or importing XML: {e}")

def create_pokemon(tx, name_en, name_de, types_en, types_de, ability_en, ability_de, hidden_en, hidden_de, stats, height, weight, gender_ratio, biology_en, biology_de, introduction_en, introduction_de, trivia_en, trivia_de, category_en, category_de, shiny_variant, evolution_line_en, evolution_line_de, attacks_en, attacks_de):
    query = (
        f"MERGE (p_en:Pokemon:EnglishVersion {{name: $name_en}}) "
        f"ON CREATE SET p_en.height = $height, p_en.weight = $weight, p_en.gender_ratio = $gender_ratio, "
        f"p_en.biology = $biology_en, p_en.introduction = $introduction_en, p_en.trivia = $trivia_en, p_en.category = $category_en, p_en.shiny_variant = $shiny_variant, "
        f"p_en.hp = $hp, p_en.attack = $attack, p_en.defense = $defense, p_en.sp_atk = $sp_atk, p_en.sp_def = $sp_def, p_en.speed = $speed "
        "WITH p_en "
        "FOREACH (type_name_en IN $types_en | "
        "   MERGE (t_en:Type {name: type_name_en}) "
        "   MERGE (p_en)-[:HAS_TYPE]->(t_en) "
        ") "
        "WITH p_en "
        "FOREACH (attack_en IN $attacks_en | "
        "   MERGE (a_en:Attack {name: attack_en.MoveName, level: attack_en.Level, type: attack_en.Type, category: attack_en.Category, power: attack_en.Power, accuracy: attack_en.Accuracy, pp: attack_en.PP}) "
        "   MERGE (p_en)-[:LEARNS]->(a_en) "
        ") "
        "WITH p_en "
        f"MERGE (p_de:Pokemon:GermanVersion {{name: $name_de}}) "
        f"ON CREATE SET p_de.height = $height, p_de.weight = $weight, p_de.gender_ratio = $gender_ratio, "
        f"p_de.biology = $biology_de, p_de.introduction = $introduction_de, p_de.trivia = $trivia_de, p_de.category = $category_de, p_de.shiny_variant = $shiny_variant, "
        f"p_de.hp = $hp, p_de.attack = $attack, p_de.defense = $defense, p_de.sp_atk = $sp_atk, p_de.sp_def = $sp_def, p_de.speed = $speed "
        "WITH p_en, p_de "
        "FOREACH (type_name_de IN $types_de | "
        "   MERGE (t_de:Type {name: type_name_de}) "
        "   MERGE (p_de)-[:HAS_TYPE]->(t_de) "
        ") "
        "WITH p_en, p_de "
        "FOREACH (attack_de IN $attacks_de | "
        "   MERGE (a_de:Attack {name: attack_de.MoveName, level: attack_de.Level, type: attack_de.Type, category: attack_de.Category, power: attack_de.Power, accuracy: attack_de.Accuracy, pp: attack_de.PP}) "
        "   MERGE (p_de)-[:LEARNS]->(a_de) "
        ") "
        "WITH p_en, p_de "
        "MERGE (a_en:Ability {name: $ability_en, hidden: $hidden_en}) "
        "MERGE (p_en)-[:HAS_ABILITY]->(a_en) "
        "WITH p_en, p_de "
        "MERGE (a_de:Ability {name: $ability_de, hidden: $hidden_de}) "
        "MERGE (p_de)-[:HAS_ABILITY]->(a_de) "
        "WITH p_en, p_de "
        "FOREACH (evolution_name_en IN $evolution_line_en | "
        "   MERGE (e_en:Pokemon {name: evolution_name_en}) "
        "   MERGE (p_en)-[:EVOLVES_TO]->(e_en) "
        ") "
        "WITH p_en, p_de "
        "FOREACH (evolution_name_de IN $evolution_line_de | "
        "   MERGE (e_de:Pokemon {name: evolution_name_de}) "
        "   MERGE (p_de)-[:EVOLVES_TO]->(e_de) "
        ") "
        "MERGE (p_en)-[:GERMAN_VERSION]->(p_de)"
    )
    tx.run(query, name_en=name_en, name_de=name_de, types_en=types_en, types_de=types_de, ability_en=ability_en, ability_de=ability_de, hidden_en=hidden_en, hidden_de=hidden_de,
           height=height, weight=weight, gender_ratio=gender_ratio,
           biology_en=biology_en, biology_de=biology_de, introduction_en=introduction_en, introduction_de=introduction_de, trivia_en=trivia_en, trivia_de=trivia_de, category_en=category_en, category_de=category_de, shiny_variant=shiny_variant, evolution_line_en=evolution_line_en, evolution_line_de=evolution_line_de,
           attacks_en=attacks_en, attacks_de=attacks_de,
           hp=stats.get('hp', 0), attack=stats.get('attack', 0), defense=stats.get('defense', 0),
           sp_atk=stats.get('sp_atk', 0), sp_def=stats.get('sp_def', 0), speed=stats.get('speed', 0))

def main(folder_path):
    try:
        # Check if folder_path is a valid directory
        if not os.path.isdir(folder_path):
            raise ValueError(f"Folder path '{folder_path}' is not a valid directory.")

        # Iterate over files in the directory
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if file_path is a file and ends with .xml
            if os.path.isfile(file_path) and filename.endswith('.xml'):
                try:
                    print(f"Processing file {filename}...")
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    parse_and_import_xml(root)
                    print(f"Successfully imported data from {file_path}")
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
    except Exception as e:
        print(f"Error in main function: {e}")

if __name__ == "__main__":
    folder_path = r'D:\Coding\Uni\Texttechnology\Project\final_data\final_data'  # Replace with your folder path
    main(folder_path)
    driver.close()


