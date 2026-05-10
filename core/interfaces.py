from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .entidades import ConfiguracionSimulacion

class MotorSimulacion(ABC):
    """Abstracción del motor de eventos discretos (SimPy o scheduler casero)"""
    @abstractmethod
    def ejecutar(self, config: ConfiguracionSimulacion, callbacks: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Ejecuta la simulación y retorna métricas"""
        pass

class RepositorioResultados(ABC):
    @abstractmethod
    def guardar(self, config: ConfiguracionSimulacion, metricas: Dict[str, Any], escenario_id: str):
        pass

    @abstractmethod
    def cargar_todos(self) -> List[Dict[str, Any]]:
        pass