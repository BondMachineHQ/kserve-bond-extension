from datetime import datetime

class PrintHandler:

    _instance = None
    _WHITE = '\033[97m'
    _HEADER = '\033[95m'
    _OKBLUE = '\033[94m'
    _OKCYAN = '\033[96m'
    _OKGREEN = '\033[92m'
    _WARNING = '\033[93m'
    _FAIL = '\033[91m'
    _ENDC = '\033[0m'
    _BOLD = '\033[1m'
    _UNDERLINE = '\033[4m'

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def print_warning(self, text):
        print(self._WARNING+datetime.today().strftime('%Y-%m-%d %H:%M:%S')+" "+text+self._WHITE)
        
    def print_success(self, text):
        print(self._OKGREEN+datetime.today().strftime('%Y-%m-%d %H:%M:%S')+" "+text+self._WHITE)
        
    def print_fail(self, text):
        print(self._FAIL+datetime.today().strftime('%Y-%m-%d %H:%M:%S')+" "+text+self._WHITE)