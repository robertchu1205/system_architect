import imp
import sys
import logging

def check_module(name,  module_path):
    try:
        imp.find_module(name, module_path)
        return True
    except ImportError:
        return False

def dynamic_imp(name,  module_path):
    try:
        fp, path, desc = imp.find_module(name, module_path)
        myModule = imp.load_module(name, fp,  path, desc)
    except Exception as e:
        raise Exception(str(e))
        logging.error(e)
          
    return myModule