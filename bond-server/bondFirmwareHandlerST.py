from pynq import Overlay
from pynq import MMIO
import os
import numpy as np
import struct
import time
import struct

class BondFirmwareHandlerST(object):
    
    _instance = None
    _overlay = None
    _sendchannel = None
    _recvchannel = None
    _benchcore = True
    _n_output = 0
    _n_input = 0
    _batchsize = 16

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def random_pad(self, vec, pad_width, *_, **__):
        vec[:pad_width[0]] = np.random.uniform(0, 1, size=pad_width[0])
        vec[vec.size-pad_width[1]:] = np.random.uniform(0,1, size=pad_width[1])
    
    def load_bitsteam(self, firmware_abs_path, n_input, n_output):
        
        # initialize overlay, send and recv channel, n_inputs and n_outputs
        self._overlay = Overlay(firmware_abs_path)
        self._sendchannel = overlay.axi_dma_0.sendchannel
        self._recvchannel = overlay.axi_dma_0.recvchannel
        self._n_input = n_input
        self._n_output = n_output
        
        
    def convert_int_to_float(self, number):
        
        bin_str = bin(number)[2:].zfill(32)
        byte_str = int(bin_str, 2).to_bytes(4, byteorder='big')
        float_value = struct.unpack('>f', byte_str)[0]
        
        return float_value
                
    def predict(self, x_test):
        
        samples_len = len(x_test)
        
        n_batches = 0
        fill = False
        if (samples_len/self._batchsize % 2 != 0):
            n_batches = int(samples_len/self._batchsize) + 1
            fill = True
        else:
            n_batches = int(samples_len/self._batchsize)
            
        batches = []
        last_self._batchsize = 0
        for i in range(0, n_batches):
            new_batch = X_test[i*self._batchsize:(i+1)*self._batchsize]
            if (len(new_batch) < self._batchsize):
                last_self._batchsize = len(new_batch)
                new_batch = np.pad(new_batch,  [(0, self._batchsize-len(new_batch)), (0,0)], mode=self.random_pad)
            batches.append(new_batch)
            
        outputs = []
        for i in range(0, len(batches)):
            input_shape  = (self._batchsize, self._n_input)
            output_shape = (self._batchsize, self._n_output)
            input_buffer = allocate(shape=input_shape, dtype=np.float32)
            output_buffer = allocate(shape=output_shape, dtype=np.int32)

            input_buffer[:]=batches[i]
            sendchannel.transfer(input_buffer)
            recvchannel.transfer(output_buffer)
            if fill == True and i == len(batches) - 1:
                outputs.append(output_buffer[0:last_batch_size])
            else:
                outputs.append(output_buffer)
                
        
        results_to_dump = []

        for outcome in outputs:
            for out in outcome:
                
                prob_0_float_value = convert_int_to_float(out[0])
                prob_1_float_value = convert_int_to_float(out[1])
                
                classification = np.argmax([prob_0_float_value, prob_1_float_value])