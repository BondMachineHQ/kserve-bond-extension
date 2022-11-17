from pynq import Overlay
from pynq import MMIO
import os
import numpy as np
import struct
import time

class BondFirmwareHandler(object):
    
    _instance = None
    _overlay = None
    _spi0 = None
    _bm_ip_name = "bondmachineip_0"
    _benchcore = True
    _n_output = 0

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def get_binary_from_float(self, num):
        return bin(struct.unpack('!i',struct.pack('!f',num))[0])
    
    def bin_to_float(self, binary):
        return struct.unpack('!f',struct.pack('!I', int(binary, 2)))[0]
    
    def read_output(self, n_input):
        starting_offset = (n_input*4)+(2*4)
        result_from_bm_ml = []
        offset = starting_offset
        
        borderRange = self._n_output + 1 if self._benchcore == True else self._n_output
        for i in range(0, borderRange):
            bin_res = bin(self._spi0.read_mm(offset, 4))
            
            if self._benchcore == True:
                if i != borderRange-1:
                    output = self.bin_to_float(str(bin_res).replace("b", ""))
                else:
                    output = int(str(bin_res), 2)
            else:
                output = self.bin_to_float(str(bin_res).replace("b", ""))
                
            result_from_bm_ml.append(output)
            offset = offset + 4
        
        return result_from_bm_ml
    
    def load_bitsteam(self, firmware_abs_path):
        
        self._overlay = Overlay(firmware_abs_path)
        self._bm_starting_address  = (self._overlay.ip_dict[self._bm_ip_name]["phys_addr"])
        self._spi0 = MMIO(self._bm_starting_address, 128)
        
    def predict(self, input_shape, input_data, n_output):
        
        idx = 0
        results_to_dump = []
        offset = 0
        self._n_output = n_output
        
        for feature in input_data:
            binToSend = self.get_binary_from_float(feature)
            decToSend = int(binToSend, 2)
            if self._spi0 == None:
                raise Exception("bitsream not loaded")
            self._spi0.write_mm(offset, decToSend)
            offset = offset + 4 # 4 BYTE = 32 BIT
            
        time.sleep(0.5)
        out = np.asarray(self.read_output(input_shape[1]))
        classification = np.argmax(out[0:2])
        
        return [float(out[0]), float(out[1]), float(classification)]
    