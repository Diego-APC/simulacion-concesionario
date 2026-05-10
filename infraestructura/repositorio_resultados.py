import json
import os
from typing import List, Dict, Any
from core.interfaces import RepositorioResultados

class RepositorioJSON(RepositorioResultados):
    def __init__(self, archivo="resultados_simulacion.json"):
        self.archivo = archivo
    
    def guardar(self, config, metricas, escenario_id):
        datos = {
            "escenario": escenario_id,
            "configuracion": {
                "num_asesores": config.num_asesores,
                "num_cajeros": config.num_cajeros,
                "num_personal_entrega": config.num_personal_entrega,
                "duracion": config.duracion_jornada_min,
                "tasa_llegada": config.tasa_llegada_por_min,
                "prob_credito": config.prob_credito,
            },
            "metricas": metricas
        }
        # Cargar existentes
        existentes = []
        if os.path.exists(self.archivo):
            with open(self.archivo, "r") as f:
                existentes = json.load(f)
        existentes.append(datos)
        with open(self.archivo, "w") as f:
            json.dump(existentes, f, indent=2)
    
    def cargar_todos(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.archivo):
            with open(self.archivo, "r") as f:
                return json.load(f)
        return []