from typing import Dict, Any, Optional
from core.entidades import ConfiguracionSimulacion
from infraestructura.motor_simpy import SimuladorSimPy
from infraestructura.repositorio_resultados import RepositorioJSON
from core.casos_uso import OrquestadorSimulacion

def ejecutar_simulacion(config: Optional[ConfiguracionSimulacion] = None, nombre_escenario: str = "custom") -> Dict[str, Any]:
    """
    API pública para ejecutar la simulación con configuración personalizada.
    Retorna métricas.
    """
    if config is None:
        config = ConfiguracionSimulacion()
    motor = SimuladorSimPy()
    repo = RepositorioJSON()
    orquestador = OrquestadorSimulacion(motor, repo)
    metricas = orquestador.ejecutar_escenario(config, nombre_escenario)
    return metricas