import logging
import sys


class Logger:
    def __init__(self, name, level=logging.DEBUG) -> None:
        """
        Initialize the Logger instance.
        :param name: Name of the logger.
        :param log_file_dir: File to save the log messages.
        :param level: Logging level.
        """

        self.name = name

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # file_handler
        file_handler = logging.StreamHandler(sys.stdout)
        file_handler.setLevel(level)

        # formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def log(self, level: str, message: str):
        """
        Log a message with the given level.
        :param level: The level of the message (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        :param message: The message to log.
        """

        with open("log_text.txt", "a+", encoding="utf-8") as f:
            f.write(f"{self.name} - {level} - {message}\n")

        level = level.upper()
        if level == "DEBUG":
            self.logger.debug(message)
        elif level == "INFO":
            self.logger.info(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "CRITICAL":
            self.logger.critical(message)
        else:
            raise ValueError(f"Invalid logging level: {level}")


ai_log = Logger("AI")
history_log = Logger("History")
mail_log = Logger("Mail")
main_log = Logger("Main")
reminder_log = Logger("Reminder")
db_log = Logger("Database")
ticket_log = Logger("Ticket")
todolist_log = Logger("ToDo-List")
