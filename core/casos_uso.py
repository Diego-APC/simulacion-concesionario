from typing import Dict, Any, List
from core.entidades import ConfiguracionSimulacion
from core.interfaces import MotorSimulacion, RepositorioResultados

class OrquestadorSimulacion:
    def __init__(self, motor: MotorSimulacion, repositorio: RepositorioResultados):
        self.motor = motor
        self.repositorio = repositorio
    
    def ejecutar_escenario(self, config: ConfiguracionSimulacion, nombre_escenario: str) -> Dict[str, Any]:
        metricas = self.motor.ejecutar(config)
        self.repositorio.guardar(config, metricas, nombre_escenario)
        return metricas
    
    def ejecutar_multiples_escenarios(self, escenarios: List[tuple]) -> List[Dict[str, Any]]:
        resultados = []
        for config, nombre in escenarios:
            res = self.ejecutar_escenario(config, nombre)
            resultados.append({"nombre": nombre, **res})
        return resultados