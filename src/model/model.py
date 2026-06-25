from abc import ABC, abstractmethod
from database.database import Database

class Model(ABC):
    def __init__(self):
        self.connection = Database()
        
    @abstractmethod
    def create(self):
        pass