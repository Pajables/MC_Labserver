import os
import sys
import cv2 as cv
import numpy as np
from flask import current_app, jsonify
import xml.etree.ElementTree as et
import json

class SynthesisPlanner:
    time = ['seconds', 's', 'hr', 'min', 'hours', 'minutes']
    mass = ['g', 'mg']
    volume = ['l', 'ml', 'ul']
    temp = ['K', '°C']
    
    def __init__(self, enabled_modules):
        self.name = 'test'
        if "azo_synthesis" in enabled_modules:
            from .azo_synthesis import AzoSynthesis
            self.azo = AzoSynthesis()

    
    @classmethod
    def update_xdl(cls, parameters, xdl_file):
        """Updates XDL from a database entry

        Args:
            parameters (list): pairs of values corresponding to [parameter name, parameter amount]
            xdl_file (JSON file): A JSON file containing an XDL protocol string

        Returns:
            string: A utf-8 encoded XDL string.
        """
        protocol = cls.load_xdl_file(xdl_file)
        if protocol[0] is None:
            return False, protocol[1]
        else:
            protocol = protocol[0]
            if protocol.find("Synthesis"):
                procedure = protocol[0].findall("Procedure")
            else:
                procedure = protocol.findall('Procedure')
            for step in procedure[0]:
                step_param_no = 0
                param = step.get(f'step_param{step_param_no}')
                # iterate through all the step's parameters
                while param:
                    param_num = int(param.split('_')[1])
                    print(param_num, file=sys.stderr)
                    parameter = parameters[param_num]
                    search_term, units = cls.get_units(parameter[0])
                    # update this parameter with relevant value from table.
                    step.attrib[search_term] = str(parameter[1]) + ' ' + units
                    del step.attrib[f'step_param{step_param_no}']
                    step_param_no += 1
                    param = step.get(f'step_param{step_param_no}')
            xdl_string = et.tostring(protocol, encoding='UTF-8')
            xdl_string = xdl_string.decode('UTF-8')
            return True, xdl_string

    @classmethod
    def load_xdl_file(cls, xdl_file):
        xdl_file = os.path.join(current_app.config['PROTOCOL_FOLDER'], xdl_file)
        if xdl_file[-4:] == ".xdl":
            try:
                with open(xdl_file, encoding='UTF-8') as xdl:
                    raw_xdl = xdl.read()
                    protocol = et.fromstring(raw_xdl)
            except (FileNotFoundError, KeyError) as e:
                return (None, str(e))
        else:
            # file must be json
            try:
                with open(xdl_file, encoding='UTF-8') as xdl:
                    raw_file = json.load(xdl)
                    protocol = et.fromstring(raw_file['protocol'])
            except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError) as e:
                return (None, str(e))
        return (protocol,)
    
    @classmethod
    def load_xdl_string(cls, xdl_string):
        try:
            protocol = et.fromstring(xdl_string)
        except et.ParseError as e:
            return None, str(e)
        return protocol, None

    @classmethod
    def get_units(cls, units):
        units = units.split('[')[1][:-1]
        if units in cls.time:
            search_term = 'time'
        elif units in cls.mass:
            search_term = 'mass'
        elif units in cls.volume:
            search_term = 'volume'
        elif units in cls.temp:
            search_term = 'temp'
        else:
            search_term = ''
        return search_term, units
    
    @classmethod
    def write_json_from_file(directory, input_fp, output_fp):
        with open(os.path.join(directory, input_fp), 'r', encoding='UTF-8') as file:
            sample_xdl = {'protocol': file.read()}
        with open(os.path.join(directory, output_fp), 'w+', encoding='UTF-8') as file:
            json.dump(sample_xdl, file, ensure_ascii=False, indent=4)


    def upload_reaction_img(self, data, img_metadata):
        """Gets a reaction image from an HTTP request. Decodes the image using Opencv and performs processing if required.

        Args:
            data (string): The binary encoded image string
            img_metadata (dict): Information about the image used for constructing a useful filename
            img_processing (string): The type of processing to be applied, if any. 

        Returns:
            [type]: [description]
        """
        filename = f"{img_metadata['reaction_name']}_ID{img_metadata['reaction_id']}_IMG{img_metadata['img_number']}.png"
        nparr = np.fromstring(data, np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR)
        cv.imwrite(os.path.join(current_app.config['REACTION_IMAGE_FOLDER'],filename), img)
        if img_metadata.get('img_processing') == "azo":
            try:
                roi = img_metadata.get('img_roi')
                colour = self.azo.get_reaction_colour(img, roi)
                b, g, r = colour
                print(r, g, b, file=sys.stderr)
                hexnum = int(r) << 16
                hexnum = hexnum | (int(g) << 8)
                hexnum = hexnum | int(b)
                return hexnum
            except AttributeError:
                return jsonify({'error': f"{img_metadata.get('img_processing')} has not been implemented on this server instance"})
        return f"{img.shape[1]}x{img.shape[0]}"