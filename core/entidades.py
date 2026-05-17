from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import numpy as np


class EstadoCliente(Enum):
    ESPERA_ASESOR = "es_asesor"
    EN_ASESOR = "en_asesor"
    ESPERA_CREDITO = "es_credito"
    EN_CREDITO = "en_credito"
    ESPERA_CAJA = "es_caja"
    EN_CAJA = "en_caja"
    ESPERA_ENTREGA = "es_entrega"
    EN_ENTREGA = "en_entrega"
    ABANDONO = "abandono"
    VENTA_EXITOSA = "venta"

@dataclass
class Cliente:
    id: int
    tiempo_llegada: float
    necesita_credito: Optional[bool] = None
    estado: EstadoCliente = EstadoCliente.ESPERA_ASESOR
    tiempo_inicio_asesor: Optional[float] = None
    tiempo_fin_asesor: Optional[float] = None
    tiempo_inicio_credito: Optional[float] = None
    tiempo_fin_credito: Optional[float] = None
    tiempo_inicio_caja: Optional[float] = None
    tiempo_fin_caja: Optional[float] = None
    tiempo_inicio_entrega: Optional[float] = None
    tiempo_fin_entrega: Optional[float] = None
    tiempo_abandono: Optional[float] = None
    credito_aprobado: Optional[bool] = None
    compra_decidida: Optional[bool] = None

@dataclass
class ConfiguracionSimulacion:
    num_asesores: int = 3
    num_cajeros: int = 1
    num_personal_entrega: int = 1      
    duracion_jornada_min: float = 480.0  # 8 horas
    tasa_llegada_por_min: float = 0.2    # exponencial con media 5 min
    tiempo_asesor_min: float = 4.0
    tiempo_asesor_moda: float = 8.0
    tiempo_asesor_max: float = 15.0
    tiempo_credito_min: float = 10.0
    tiempo_credito_max: float = 25.0
    tiempo_caja_min: float = 3.0
    tiempo_caja_max: float = 6.0     # uniforme, si se prefiere constante usar min=max
    tiempo_entrega_min: float = 4.0
    tiempo_entrega_moda: float = 5.0
    tiempo_entrega_max: float = 8.0
    prob_credito: float = 0.4
    prob_aprobacion_credito: float = 0.75
    prob_compra_sin_credito: float = 0.10   # 10% compra directa
    prob_compra_con_credito: float = 0.15   # 15% compra con crédito
    prob_abandono_despues_asesoria: float = 0.75  # 75% abandona
    # En entidades.py
    max_espera_asesor_min: float = 10.0
    max_espera_caja_min: float = 10.0
    max_espera_entrega_min: float = 30.0
    
    # Semilla aleatoria (para reproducibilidad)
    semilla: int = 42
    # Verificación: mostrar logs detallados?
    verbose: bool = False

def __post_init__(self):
    # Validaciones de probabilidades de compra/abandono
    assert 0 <= self.prob_compra_sin_credito <= 1
    assert 0 <= self.prob_compra_con_credito <= 1
    assert 0 <= self.prob_abandono_despues_asesoria <= 1
    total = self.prob_compra_sin_credito + self.prob_compra_con_credito + self.prob_abandono_despues_asesoria
    assert abs(total - 1.0) < 1e-6, f"Las probabilidades deben sumar 1 (suman {total})"
    
    # Validación de aprobación de crédito
    assert 0 <= self.prob_aprobacion_credito <= 1
    
    # Validaciones de recursos
    assert self.num_asesores > 0
    assert self.num_cajeros > 0
    assert self.num_personal_entrega > 0
    assert self.tasa_llegada_por_min > 0
    
    np.random.seed(self.semilla)

        