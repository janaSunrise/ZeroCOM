from ..utils import Logger


class CustomLoggingClass:
    @property
    def logger(self):
        try:
            return self._log
        except AttributeError:
            self._log = Logger()
            return self._log
