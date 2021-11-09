import json
from json.decoder import JSONDecodeError
import os
import xml.etree.ElementTree as et

time = ['seconds', 's', 'hr', 'min', 'hours', 'minutes']
mass = ['g', 'mg']
volume = ['l', 'ml', 'ul']

def write_json_from_file(directory, input_fp, output_fp):
    with open(os.path.join(directory, input_fp), 'r', encoding='UTF-8') as file:
        sample_xdl = {'protocol': file.read()}
    with open(os.path.join(directory, output_fp), 'w+', encoding='UTF-8') as file:
        json.dump(sample_xdl, file, ensure_ascii=False, indent=4)

def write_json_from_string(directory, xdl_string, output_fp):
    sample_xdl = {'protocol': xdl_string}
    with open(os.path.join(directory, output_fp), 'w+', encoding='UTF-8') as file:
        json.dump(sample_xdl, file, ensure_ascii=False, indent=4)

def read_xdl(directory, fp):
    fp = os.path.join(directory, fp)
    try:
        with open(fp, encoding='UTF-8') as file:
            raw_json = json.load(file)
            file.close()
    except (FileNotFoundError, JSONDecodeError) as e:
        print("Invalid file")
    protocol = et.fromstring(raw_json['protocol'])
    return protocol

def get_units(param):
    units = param[0]
    units = units.split('[')[1][:-1]
    if units in time:
        search_term = 'time'
    elif units in mass:
        search_term = 'mass'
    elif units in volume:
        search_term = 'volume'
    else:
        search_term = ''
    return search_term

if __name__ == "__main__":
    here = os.path.dirname(__file__)
    write_json_from_file(here, 'simple_xdl.xdl', 'json_xdl.json')
    parameters = [['heat [seconds]',10], ['acetic acid [ml]', 10.0], ['salicyclic acid [g]', 3.0]]
    protocol = read_xdl(here, 'json_xdl.json')
    procedure = protocol.findall('Procedure')
    for step in procedure[0]:
        param = step.get('param')
        if param:
            num = int(param[-1])
            parameter = parameters[num]
            step.attrib[get_units(parameter)] = str(parameter[1])
            del step.attrib['param']
    for item in procedure[0]:
        print(item.tag, item.attrib)
    xdl_string = et.tostring(protocol, encoding='UTF-8')
    xdl_string = xdl_string.decode('UTF-8')
    write_json_from_string(here, xdl_string, 'xdl_mod.json')