import poke_data_downloader 
import poke_xml_creator
import poke_xml_vaildator


BISAFANS_DATA_DIRECTORY = '../data/bisafans_data'
POKEWIKI_DATA_DIRECTORY = '../data/pokewiki_data'
BULBAPEDIA_DATA_DIRECTORY = '../data/bulbapedia_data'

PARSED_DATA_DESTINATION_DIRECTORY = '../data/parsed_data'
XSD_FILE_PATH = 'Pokemon.xsd'

# Start download
poke_data_downloader.main(data_directories=[BISAFANS_DATA_DIRECTORY, POKEWIKI_DATA_DIRECTORY, BULBAPEDIA_DATA_DIRECTORY])

# Parse data and create xml files
poke_xml_creator.main([BISAFANS_DATA_DIRECTORY, POKEWIKI_DATA_DIRECTORY, BULBAPEDIA_DATA_DIRECTORY], PARSED_DATA_DESTINATION_DIRECTORY)

# Validate xml files
poke_xml_vaildator.main(PARSED_DATA_DESTINATION_DIRECTORY, XSD_FILE_PATH)

