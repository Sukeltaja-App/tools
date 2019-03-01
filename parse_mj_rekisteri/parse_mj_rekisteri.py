import csv, json, sys

fieldnames = [
  'kunta',
  'mj_id',
  'kohdenimi',
  'ajoitus',
  'tyyppi',
  'alatyyppi',
  'laji',
  'longitude',
  'latitude',
  'paikannustarkkuus',
  'paikannustapa',
  'selite',
  'tuhoutunut',
  'luontipvm',
  'muutospvm',
  'zala',
  'zylä',
  'vedenalainen'
]

"""
This function parses the content of the json file
to suit our needs.

:param content: a list (in json format) to parse
:returns: parsed and modified content

"""
def modify_content(content):
  columns_with_float_type = [
    'longitude',
    'latitude',
    'zala',
    'zylä'
  ]

  for row in content:
    for key in row:
      value = row[key]

      # null values to appropriate places
      if (value == '' or value == 'ei määritelty'):
        row[key] = None
      # replace 'Ei' with false
      if (key == 'tuhoutunut' and value == 'Ei'):
        row[key] = False
      # replace 'K', 'k' with true and 'E', 'e' with false
      if (key == 'vedenalainen'):
        if (value.lower() == 'k'):
          row[key] = True
        else:
          row[key] = False
      # string to int where appropriate
      if (key == 'mj_id'):
        row[key] = int(value)
      # string to float where appropriate
      if (key in columns_with_float_type):
        row[key] = float(value.replace(',', '.'))
  return content

"""
Opens a json file, modifies it using modify_content(),
and writes to disk with the same filename as given.

:param json_file: the input file (.json)
:raises FileNotFoundError: if input file not found
:returns: None

"""
def parse_json(json_file):
  with open(json_file, 'r') as input_file:
    content = json.load(input_file)
    modified_content = json.dumps(modify_content(content), indent=2, ensure_ascii=False)

  with open(json_file, 'w') as output_file:
    output_file.write(modified_content)
    print('Modified json.')

"""
Converts a csv file with ; as delimiter to json format.

:param csv_file: the input file (.csv)
:param json_file: the output file (.json)
:raises FileNotFoundError: if input file not found
:returns: None

"""
def csv_to_json(csv_file, json_file, fieldnames):
  print("\nReading csv file '%s'..." % csv_file)

  with open(csv_file) as input_file:
    next(input_file)  # Skip first row
    csv_reader = csv.DictReader(input_file, fieldnames=fieldnames, delimiter=';')

    content = json.dumps([ row for row in csv_reader ], indent=2, ensure_ascii=False)

  with open(json_file, 'w') as output_file:
    output_file.write(content)
    print("Converted to json '%s'." % json_file)

"""
This script parses target data from Museovirasto.

TO-DO:
  - remove all unused fields we don't want
    (maybe keep the extended data in a separate file
    if there's any future use?)
  - 'alatyyppi' -> make a new field 'material'
    - hylyt (puu) -> puu
    - hylyt (metalli) -> metalli
  - 'alatyyppi' -> make a new field 'type'
    - ruuhet -> 'ruuhi'
    - * -> hylky
  - convert latitude and longitude coordinates from
    ETRS-TM35FIN to WGS84 (maybe using for example
    https://olammi.iki.fi/sw/coordinates/ ?)
  - 'paikannustarkkuus' -> find out what the codes
    (0, 11000, 11001, 11002, 11003, 11004) mean using
    https://www.kyppi.fi/ and convert to appropriate strings
  - 'paikannustapa' -> find out what the codes
    (0, 1, 2, 3) mean using https://www.kyppi.fi/
    and convert to appropriate strings
  - convert 'pvm' to more appropriate date format (ISO 8601)
  - translate all fields to English where appropriate

:param param1: this is a first param
:param param2: this is a second param
:returns: this is a description of what is returned
:raises keyError: raises an exception
"""
def main():
  if len(sys.argv) != 3:
    print('\nThis is a small script to parse shipwreck data from Museovirasto.')
    print('Usage: python3 parse_mj_rekisteri.py <csv input filename> <json output filename>\n')
  else:
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    csv_to_json(input_file, output_file, fieldnames)
    parse_json(output_file)
    print('Done.\n')

if __name__ == "__main__":
  main()
