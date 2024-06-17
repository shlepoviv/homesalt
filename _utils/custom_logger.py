import time 
import salt.config
class CustomLogger:
    def __init__(self, opts):
        self.opts = opts
        self.last_check_opts = time.time()
        self.interval_check_opts = 120

    def _check_opts(self):
        if time.time() - self.last_check_opts >= self.interval_check_opts:
            self.opts = salt.config.master_config(self.opts['conf_file'])
            self.last_check_opts = time.time()

    def info(self,mess):
        self._check_opts()
        with open('/home/shlepov/testlog','a') as f:
            f.write(f'last_check_opts: {self.last_check_opts}\tlog_level: {self.opts.get("custom_log_lvl")}\t{mess}\n')


        