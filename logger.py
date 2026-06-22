import logging
from datetime import datetime

class Logger:
    def __init__(self, log_file="agent.log"):
        self.logger = logging.getLogger("AgentLogger")
        self.logger.setLevel(logging.INFO)
        
        # Запись в файл
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        self.logger.info(message)
        print(f"ℹ️ {message}")
    
    def warning(self, message):
        self.logger.warning(message)
        print(f"⚠️ {message}")
    
    def error(self, message):
        self.logger.error(message)
        print(f"❌ {message}")
    
    def success(self, message):
        self.logger.info(f"SUCCESS: {message}")
        print(f"✅ {message}")
