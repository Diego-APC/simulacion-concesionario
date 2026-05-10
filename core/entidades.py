from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any
import numpy as np

class InteresCliente(Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"

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
    necesita_credito: bool
    interes: InteresCliente
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
    prob_interes_bajo: float = 0.3
    prob_interes_medio: float = 0.5
    prob_interes_alto: float = 0.2
    # Probabilidad de compra después de asesoría (sin crédito) según interés
    prob_compra_sin_credito: Dict[InteresCliente, float] = field(default_factory=lambda: {
        InteresCliente.BAJO: 0.50,
        InteresCliente.MEDIO: 0.80,
        InteresCliente.ALTO: 0.95,
    })
    # Semilla aleatoria (para reproducibilidad)
    semilla: int = 42
    # Verificación: mostrar logs detallados?
    verbose: bool = False

    def __post_init__(self):
        # Validaciones
        assert 0 <= self.prob_credito <= 1
        assert 0 <= self.prob_aprobacion_credito <= 1
        assert abs(self.prob_interes_bajo + self.prob_interes_medio + self.prob_interes_alto - 1.0) < 1e-6
        assert self.num_asesores > 0
        assert self.num_cajeros > 0
        assert self.num_personal_entrega > 0
        assert self.tasa_llegada_por_min > 0
        np.random.seed(self.semilla)