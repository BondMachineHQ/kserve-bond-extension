from pynq import Overlay
from pynq import MMIO
import os
import numpy as np
import struct
import time
import struct
from pynq import DefaultHierarchy, DefaultIP, allocate
from utils import PrintHandler

class BondFirmwareHandlerST(object):
    
    _instance = None
    _overlay = None
    _sendchannel = None
    _recvchannel = None
    _benchcore = True
    _n_output = 0
    _n_input = 0
    _batchsize = 16
    _last_batch_size = 0
    _arch = None
    _kernel_name = None
    _kernel = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def random_pad(self, vec, pad_width, *_, **__):
        vec[:pad_width[0]] = np.random.uniform(0, 1, size=pad_width[0])
        vec[vec.size-pad_width[1]:] = np.random.uniform(0,1, size=pad_width[1])
    
    def load_bitsteam(self, firmware_abs_path, n_input, n_output, benchcore, arch):
        
        # initialize overlay, send and recv channel, n_inputs and n_outputs
        self._overlay = Overlay(firmware_abs_path)
        self._arch = arch
        if self._arch == "zynq":
            self._sendchannel = self._overlay.axi_dma_0.sendchannel
            self._recvchannel = self._overlay.axi_dma_0.recvchannel
        elif self._arch == "alveo":
            self._kernel_name = "krnl_vadd_rtl_1"
            self._kernel = self._overlay[self._kernel_name]
            
        self._n_input = n_input
        self._n_output = n_output
        self._benchcore = benchcore
        
    def convert_int_to_float(self, number):
        
        bin_str = bin(number)[2:].zfill(32)
        byte_str = int(bin_str, 2).to_bytes(4, byteorder='big')
        float_value = struct.unpack('>f', byte_str)[0]
        
        return float_value
                
    def predict(self, x_test):
        
        x_test = np.asarray(x_test)
        samples_len = len(x_test)
        
        PrintHandler().print_warning(" * Request to classify "+str(samples_len)+" samples  *")
        
        batches = []
        outputs = []
        fill = False
        
        if samples_len < self._batchsize:
            num_rows = self._batchsize - x_test.shape[0]
            zeros = np.random.rand(num_rows, x_test.shape[1])
            x_test = np.concatenate((x_test, zeros), axis=0)
            batches.append(x_test)
        else:
            n_batches = 0
            if samples_len == self._batchsize:
                n_batches = 1
            else:
                if (samples_len/self._batchsize % 2 != 0):
                    n_batches = int(samples_len/self._batchsize) + 1
                    fill = True
                else:
                    n_batches = int(samples_len/self._batchsize)
                
            batches = []
            for i in range(0, n_batches):
                new_batch = x_test[i*self._batchsize:(i+1)*self._batchsize]
                if (len(new_batch) < self._batchsize):
                    self._last_batch_size = len(new_batch)
                    new_batch = np.pad(new_batch,  [(0, self._batchsize-len(new_batch)), (0,0)], mode=self.random_pad)
                batches.append(new_batch)
        
        for i in range(0, len(batches)):
            
            input_shape  = (self._batchsize, self._n_input)
            output_shape = (self._batchsize, self._n_output)
            
            input_buffer = allocate(shape=input_shape, dtype=np.float32)
            output_buffer = allocate(shape=output_shape, dtype=np.int32)

            input_buffer[:]=batches[i]
            
            PrintHandler().print_warning(" * Going to transfer data input on AXI DMA channel *")
            
            if self._arch == "zynq":
                self._sendchannel.transfer(input_buffer)
                self._recvchannel.transfer(output_buffer)
                self._sendchannel.wait()
                self._recvchannel.wait()
                
                PrintHandler().print_success(" * Data transferred successfully *")
                
                if fill == True and i == len(batches) - 1:
                    outputs.append(output_buffer[0:self._last_batch_size])
                else:
                    outputs.append(output_buffer)
            elif self._arch == "alveo":
                input_buffer.sync_to_device()
                self._kernel.call(input_buffer, output_buffer)
                
        results_to_dump = []

        idx = 0
        for outcome in outputs:
            for out in outcome:
                
                if samples_len < self._batchsize:
                    if idx == samples_len:
                        break
                
                probabilities = []    
                for i in range(0, self._n_output):
                    probabilities.append(self.convert_int_to_float(out[i]))
                
                classification = np.argmax(np.asarray(probabilities))
                probabilities.append(float(classification)) # append the classification
                if self._benchcore == True:
                    probabilities.append(float(out[self._n_output+1])) # append the benchcore
                    results_to_dump.append(probabilities)
                else:
                    results_to_dump.append(probabilities)
                
                idx = idx + 1
        
        PrintHandler().print_success(" * Raw output is "+str(results_to_dump)+" *")
        
        return results_to_dump