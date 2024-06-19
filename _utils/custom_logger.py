import time 
import salt.config
import logging 

log = logging.getLogger(__name__)
with open('/home/shlepov/loglog','a') as f:
    f.write(f'rewrite logger class{logging.getLoggerClass()}\n')
class CustomLogger:
    def __init__(self, opts):
        

        self.opts = opts
        self.last_check_opts = time.time()
        self.interval_check_opts = 120
        self._check_opts_interval = 0

    def _check_opts(self):
        if time.time() - self.last_check_opts >= self.interval_check_opts:
            start = time.time()
            self.opts = salt.config.master_config(self.opts['conf_file'])
            self._check_opts_interval = time.time() - start
            self.last_check_opts = time.time()

    def info(self,mess):
        self._check_opts()
        with open('/home/shlepov/testlog','a') as f:
            f.write(f'last_check_opts: {self.last_check_opts}\tlog_level: {self.opts.get("custom_log_lvl")}\t{self._check_opts_interval}\n')


        
