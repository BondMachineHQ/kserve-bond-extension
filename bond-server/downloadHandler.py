import os
import requests
from utils import PrintHandler
import subprocess
import json

class DownloadHandler(object):
    
    _instance = None
    _base_url = "https://minio.131.154.96.26.myip.cloud.infn.it/fpga-models/"
    _download_folder = os.getcwd()
    _necessary_keys = ["board", "n_inputs", "n_outputs", "predictor", "dataset"]
    _predictor = None
    _flavor = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    
    def download_bitstream(self, bitfile_name):
        files_to_download = [bitfile_name+".bit", bitfile_name+".hwh", bitfile_name+".json"]
        for file_to_download in files_to_download:
            endpoint_url = self._base_url + file_to_download
            response = requests.get(endpoint_url)
            open(os.getcwd()+"/"+file_to_download, "wb").write(response.content)
            
    
    def check_bitstream(self, bitfile_name):
        file_info = subprocess.getoutput("file "+bitfile_name+".bit")
        if "Xilinx BIT" not in file_info:
            raise Exception("Downloaded bitstream is not correct")
        
    def parse_metadata(self, bitfile_name):
        f = open(bitfile_name+".json")
        metadata_info = json.load(f)
        f.close()
        
        for necessary_key in self._necessary_keys:
            if necessary_key not in metadata_info:
                raise Exception(necessary_key+" key not defined")
            
        return metadata_info
    
    def set_flavor(self, value):
        self._flavor = value
        
    def get_flavor(self):
        return self._flavor
    
    def set_predictor(self, value):
        self._predictor = value
        
    def get_predictor(self):
        return self._predictor