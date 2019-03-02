import csv, json, sys
from coordinates import ETRSTM35FINxy_to_WGS84lalo as convert
from datetime import datetime

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
  'z_ala',
  'z_ylä',
  'vedenalainen'
]

columns_with_float_type = [
    'longitude',
    'latitude',
    'z_ala',
    'z_ylä'
  ]

columns_with_int_type = [
  'mj_id',
  'paikannustarkkuus',
  'paikannustapa'
]

columns_with_date_type = [
  'luontipvm',
  'muutospvm'
]

wanted_keys = {
  'mj_id',
  'kohdenimi',
  'latitude',
  'longitude',
  'material',
  'type'
}

def create_extended_json_file(content):
  """
  This function parses and modifies the content of
  the json file to create an extended json file
  with all the parameters given by Museovirasto.

  :param content: a list (in json format) to parse
  :returns: parsed and modified content
  """
  for row in content:
    for key in row:
      value = row[key]

      # null values to appropriate places
      if (not value or value == 'ei määritelty'):
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
      if (key in columns_with_int_type):
        row[key] = int(value)
      # string to float where appropriate
      if (key in columns_with_float_type):
        row[key] = float(value)
      # date to ISO 8601 where appropriate
      if (value and key in columns_with_date_type):
        row[key] = datetime.strptime(value, '%d.%m.%y').strftime('%Y-%m-%d')

    # convert coordinates from ETRS-TM35FIN to WGS84
    coordinates = convert({ 'N': row['latitude'], 'E': row['longitude'] })
    row['latitude'] = coordinates['La']
    row['longitude'] = coordinates['Lo']

  return content

def create_targets_file(content):
  """
  This function parses and modifies the content of
  the json file to create a json file of targets
  in a suitable format to be directly dumped to sukeltaja_backend.

  :param content: a list (in json format) to parse
  :returns: parsed and modified content
  """
  for row in content:
    alatyyppi = row['alatyyppi']

    # create material and type
    if (alatyyppi == 'hylyt (puu)'):
      row['type'] = 'hylky'
      row['material'] = 'puu'
    elif (alatyyppi == 'hylyt (metalli)'):
      row['type'] = 'hylky'
      row['material'] = 'metalli'
    elif (alatyyppi == 'ruuhet'):
      row['type'] = 'ruuhi'
      row['material'] = 'puu'
    # delete unwanted keys
    unwanted_keys = set(row) - set(wanted_keys)
    for key in unwanted_keys:
      del row[key]
    # rename kohdenimi to name
    row['name'] = row['kohdenimi']
    del row['kohdenimi']

  return content


def modify_json(json_file, modify_content, filename):
  """
  Opens a json file, modifies it using some function,
  and writes to disk with the given filename.

  :param json_file: the input file (.json)
  :param modify_content: a one parameter function to modify the content
  :param filename: the ouput file (.json)
  :raises FileNotFoundError: if input file not found
  """
  with open(json_file, 'r') as input_file:
    content = json.load(input_file)
    modified_content = json.dumps(modify_content(content), indent=2, ensure_ascii=False)

  with open(filename, 'w') as output_file:
    output_file.write(modified_content)

def csv_to_json(csv_file, json_file, fieldnames):
  """
  Converts a csv file with ; as delimiter to json format.

  :param csv_file: the input file (.csv)
  :param json_file: the output file (.json)
  :raises FileNotFoundError: if input file not found
  """
  print("\nReading csv file '%s'..." % csv_file)

  with open(csv_file) as input_file:
    next(input_file)  # Skip first row
    csv_reader = csv.DictReader(input_file, fieldnames=fieldnames, delimiter=';')

    content = json.dumps([ row for row in csv_reader ], indent=2, ensure_ascii=False)

  with open(json_file, 'w') as output_file:
    output_file.write(content)
    print("Converted to json '%s'." % json_file)

def print_instructions():
  """
  Prints usage instructions to the command line.
  """
  print('\nThis is a small script to parse shipwreck data from Museovirasto.')
  print('Usage:',
    'python3 parse_mj_rekisteri.py',
    '<csv input filename>',
    '<json extended output filename>',
    '<json targets ouput filename (optional)>\n'
  )

def parse_target_data(input_file, extended_file, targets_file = None):
  """
  Parses target data from Museovirasto.

  The script first converts a given csv file of shipwrecks to
  json format. It then:

  1)  creates an "extended" json file with all the information,
  2)  if a targets filename is given, creates a json file with only
      the data we need in a format suitable to be dumped
      directly to sukeltaja-backend.

  :param input_file: the input file (.csv)
  :param extended_file: the extended output file (.json)
  :param targets_file: the targets output file (.json)
  """
  csv_to_json(input_file, extended_file, fieldnames)

  modify_json(extended_file, create_extended_json_file, extended_file)
  print("Created extended json file as '%s'." % extended_file)

  if (targets_file):
    modify_json(extended_file, create_targets_file, targets_file)
    print("Created targets json file as '%s'." % targets_file)

  print('Done.\n')

def main():
  """
  Main entry of the script.

  If a proper number of arguments is given, run the script,
  otherwise print instructions.
  """
  args = sys.argv[1:]

  if len(args) == 2:
    parse_target_data(args[0], args[1])
  elif len(args) == 3:
    parse_target_data(args[0], args[1], args[2])
  else:
    print_instructions()

if __name__ == "__main__":
  main()
