#!/bin/python

#> Imports
import time
import os
#</Imports

#> Main >/
class Logger:
    def __init__(self, log_format: str, log_dir: str, ignored_categories: tuple[str]):
        self.log_format = log_format
        self.log_dir = log_dir
        self.ignored_categories = ignored_categories
        self.log_files = {}
        if not os.path.exists(self.log_dir):
            os.mkdir(self.log_dir)
    def close(self):
        self.log('*', 'Closing all logs')
        for l,f in self.log_files.items():
            print(f'Closed log {l}:{f["file"].name} at {time.strftime("%Y-%m-%d %H:%M:%S")}')
            f['file'].close()
        self.log_files = {}
    def __del__(self): # Just in case
        self.close()
    def log(self, category, message):
        if category == '*':
            for l in self.log_files:
                self.log(l, '*'+message)
            return
        if category in self.ignored_categories: return False
        if category not in self.log_files:
            self.log_files[category] = {'file': open(self.log_dir+category, 'a'), 'count': 1, 'written': 0}
            print(f'Opened log {category} at {self.log_dir+category} at {time.strftime("%Y-%m-%d %H:%M:%S")}')
            self.log_files[category]['written'] += self.log_files[category]['file'].write(time.strftime(self.log_format).replace('{message}', 'Log opened'))
        self.log_files[category]['written'] += self.log_files[category]['file'].write(time.strftime(self.log_format).replace('{message}', message))
        self.log_files[category]['count'] += 1
    def flush(self, category='*'):
        if category == '*':
            for l,f in self.log_files.items():
                print(f'Flushed log {l}:{f["file"].name} at {time.strftime("%Y-%m-%d %H:%M:%S")}')
                f['file'].flush()
            return
        if category not in self.log_files:
            return False
        print(f'Flushed log {category}:{self.log_files[category]["file"].name} at {time.strftime("%Y-%m-%d %H:%M:%S")}')
        self.log_files[category]['file'].flush()
