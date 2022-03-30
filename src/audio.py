from abc import ABC, abstractmethod


class Audio(ABC):
    @abstractmethod
    def play():
        ...