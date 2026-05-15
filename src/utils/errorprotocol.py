"""
errorprotocol.py
---------------
Main log file of ReMaild, for all kind of debug, info and errors.
This is the file that is executed the first.
"""
# importing the modules
import logging
from pathlib import Path
from rich.console import Console
from rich.text import Text
from io import StringIO


def get_style(message: str, levelname: str) -> str:
    if levelname == "INFO" and "SUCCESS: " in message:
        return "bold green"
    level_styles: dict = {
                "DEBUG": "blue",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold red"
            }
    return level_styles.get(levelname, "white")

class RichConsoleHandler(logging.Handler):
    """
    Class for logging colorful in the console
    """
    def __init__(self):
        super().__init__()
        self.console = Console()
        
    
    def emit(self, record):
        message = self.format(record=record)
        style: str = get_style(message=message, levelname=record.levelname) # type: ignore
        self.console.print(message, style=style)
        
class RichFileHandler(logging.FileHandler):
    """
    Class for logging colorful on files (ANSI)
    """
    def __init__(self, filename: str, mode="w", encoding="utf-8"):
        super().__init__(filename, mode, encoding)
        self.console = Console(file=self.stream)
        #self.console = Console(file=open(file=str(filename), mode=mode, encoding=encoding))
    def emit(self, record):
        message = self.format(record) # add timestamps
        style = get_style(message=message, levelname=record.levelname) # get the style color
        temp_console = Console(record=None) 
        buffer = StringIO()
        temp_console.file = buffer
        text = Text(message, style=style)
        temp_console.print(text, markup=False, emoji=False)
        self.stream.write(buffer.getvalue())
        self.stream.flush()

class logger:
    """
    Main Logging class for ReMailD
    """
    def __init__(self):
        try:
            self.logger = logging.getLogger(__name__)
            # Alle vorherigen Handler entfernen, damit nichts mehrfach angehängt wird
            if self.logger.hasHandlers():
                self.logger.handlers.clear()
            self.logger.propagate = False
                
            # Die logger definieren, einmal als Console Ausgabe und einmal als Datei
            self.console_handler = RichConsoleHandler()
            self.logger.addHandler(self.console_handler)
            self.file_handler = RichFileHandler(str(Path(Path(__file__).parent.parent.parent / "ReMailD.log")), mode="w", encoding="utf-8")
        
            self.logger.addHandler(self.file_handler)
                
            # die Formatter für Debug-Ausgabe erscheihnt phen Zeitangabe
            # die Formatter für den File Logger definieren
            self.formatter = logging.Formatter(
                "{asctime} - {levelname} - {message}",
                style="{",
                datefmt="%Y-%m-%d %H:%M:%S",
            ) 
            self.consoleformatter = logging.Formatter(
                "{levelname}: {message}",
                style="{"
            )
                
            self.file_handler.setFormatter(self.formatter)
            self.console_handler.setFormatter(self.consoleformatter)
            self.logger.setLevel(logging.DEBUG)
        except FileNotFoundError:
            log.log_error("FileNotFoundError: It seems the logging file does not exist. Please relaunch remaild.")
            Path((Path(__file__).parent.parent.parent / "ReMailD.log")).touch(exist_ok=False)
            exit(1)
        except Exception as e:
            log.log_error(f"Exception while initializing the logger: {e}")
            exit(1)
        
        
    def log_debug(self, msg: str) -> None:
        self.logger.debug(msg, stacklevel=logging.DEBUG)
    def log_info(self, msg: str) -> None:          
        self.logger.info(msg, stacklevel=logging.INFO)
    def log_warning(self, msg: str) -> None:
        self.logger.warning(msg, stacklevel=logging.WARNING)
    def log_error(self, msg: str) -> None:
        self.logger.error(msg, stacklevel=logging.ERROR)
    def log_critical(self, msg: str) -> None:
        self.logger.critical(msg, stacklevel=logging.CRITICAL)

    
if __name__ == "__main__":
    print((str(Path(Path(__file__).parent.parent.parent / "ReMailD.log"))))
    log: logger = logger()
    log.log_info("this is an info")
    log.log_debug("debugger")
    log.log_warning("this is an unimportant warning")
    log.log_error("error 404")
    log.log_critical("crit")
    log.log_info("SUCCESS: What a success!")