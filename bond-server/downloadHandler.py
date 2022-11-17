import os
import requests
from utils import PrintHandler

class DownloadHandler(object):
    
    _instance = None
    _base_url = "https://minio.131.154.96.42.myip.cloud.infn.it/public/fpga/"
    _download_folder = os.getcwd()

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    
    def download_bitstream(self, bitfile_name):
        
        files_to_download = [bitfile_name+".bit", bitfile_name+".hwh" ]
        for file_to_download in files_to_download:
            endpoint_url = self._base_url + file_to_download
            response = requests.get(endpoint_url)
            open(os.getcwd()+"/"+file_to_download, "wb").write(response.content)
            