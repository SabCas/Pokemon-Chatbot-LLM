import os
from lxml import etree

def validate_xml(xml_file, xsd_file):
    """
    Validate an XML file against an XSD schema.

    :param xml_file: Path to the XML file
    :param xsd_file: Path to the XSD schema file
    :return: True if XML is valid, False otherwise
    """
    with open(xsd_file, 'rb') as f:
        schema_root = etree.XML(f.read())
    schema = etree.XMLSchema(schema_root)

    xml_parser = etree.XMLParser(schema=schema)

    try:
        with open(xml_file, 'rb') as f:
            etree.fromstring(f.read(), xml_parser)
        return True
    except etree.XMLSyntaxError as e:
        print(f"XMLSyntaxError in {xml_file}: {e}")
        return False


def validate_directory(directory, xsd_file):
    """
    Validate all XML files in a directory against an XSD schema.

    :param directory: Path to the directory containing XML files
    :param xsd_file: Path to the XSD schema file
    """
    valid_files = []
    invalid_files = []

    for xml_filename in os.listdir(directory):
        xml_file = os.path.join(directory, xml_filename)
       
        if validate_xml(xml_file, xsd_file):
            valid_files.append(xml_file)
        else:
            invalid_files.append(xml_file)
    if len(invalid_files):
        print(f"Invalid XML files: {invalid_files}")
    else:
        print("All xml files passed the validation test!")


def main(xml_directory, xsd_schema_file):
    # Define the directory containing XML files and the path to the XSD schema file
    xml_directory = "/path/to/xml/files"
    xsd_schema_file = "/path/to/schema.xsd"

    validate_directory(xml_directory, xsd_schema_file)
