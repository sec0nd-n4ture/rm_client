from abc import ABC, abstractmethod


class Job(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass
