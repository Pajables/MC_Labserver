import os
import json

def write_json_from_file(directory, input_fp, output_fp):
    with open(os.path.join(directory, input_fp), 'r', encoding='UTF-8') as file:
        sample_xdl = {'protocol': file.read()}
    with open(os.path.join(directory, output_fp), 'w+', encoding='UTF-8') as file:
        json.dump(sample_xdl, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    here = os.path.dirname(__file__)
    write_json_from_file(here, 'aspirin.xdl', 'aspirin.json')