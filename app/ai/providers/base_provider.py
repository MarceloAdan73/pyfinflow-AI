from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Interfaz abstracta para providers de IA"""

    @abstractmethod
    def chat(self, messages: list[dict], **kwargs) -> str:
        """Envía mensajes al LLM y retorna la respuesta"""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Verifica si el provider está disponible"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Nombre del provider"""
        ...
