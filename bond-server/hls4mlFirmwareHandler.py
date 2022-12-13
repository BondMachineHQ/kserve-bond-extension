import numpy as np
from axi_stream_driver import NeuralNetworkOverlay

class Hls4mlFirmwareHandler(object):
    
    _instance = None
    _overlay = None
    
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance
    
    def load_bitsteam(self, firmware_abs_path, x_test_shape, y_test_shape):
        self._overlay = NeuralNetworkOverlay(firmware_abs_path, x_test_shape, y_test_shape)
        
    def predict(self, input_data):
        y_hw, latency, throughput = self._overlay.predict(input_data, profile=True, debug=False)
        o0 = y_hw[:len(input_data)][0][0]
        o1 = y_hw[:len(input_data)][0][1]
        
        return [float(o0), float(o1), float(np.argmax(y_hw[:len(input_data)][0]))]

    