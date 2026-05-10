import simpy
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from core.entidades import Cliente, ConfiguracionSimulacion, EstadoCliente, InteresCliente
from core.interfaces import MotorSimulacion

class SimuladorSimPy(MotorSimulacion):
    def __init__(self):
        self.resultados = None
        self.datos_validacion = {
            "tiempos_entre_llegadas": [],
            "tiempos_atencion_asesor": [],
        }
    
    def ejecutar(self, config: ConfiguracionSimulacion, replicas: int = 1, callbacks: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ejecuta 'replicas' corridas y promedia resultados.
        Además recolecta datos de la primera réplica para validación.
        """
        metricas_acum = {}
        self.datos_validacion = {"tiempos_entre_llegadas": [], "tiempos_atencion_asesor": []}
        for r in range(replicas):
            # Nueva semilla por réplica (para independencia)
            if config.semilla is not None:
                np.random.seed(config.semilla + r)
            env = simpy.Environment()
            asesores = simpy.Resource(env, capacity=config.num_asesores)
            cajeros = simpy.Resource(env, capacity=config.num_cajeros)
            personal_entrega = simpy.Resource(env, capacity=config.num_personal_entrega)
            
            stats = {
                "clientes_atendidos": 0,
                "ventas_exitosas": 0,
                "abandonos": 0,
                "tiempos_sistema": [],
                "tiempos_espera_asesor": [],
                "tiempos_espera_credito": [],
                "tiempos_espera_caja": [],
                "tiempos_espera_entrega": [],
                "utilizacion_asesores": [],
                "utilizacion_cajeros": [],
                "utilizacion_entrega": [],
                "cola_media_asesor": [],
                "cola_media_caja": [],
                "cola_media_entrega": [],
            }
            # Monitoreo
            def monitorear():
                while True:
                    yield env.timeout(1.0)
                    stats["utilizacion_asesores"].append(asesores.count / config.num_asesores)
                    stats["utilizacion_cajeros"].append(cajeros.count / config.num_cajeros)
                    stats["utilizacion_entrega"].append(personal_entrega.count / config.num_personal_entrega)
                    stats["cola_media_asesor"].append(len(asesores.queue))
                    stats["cola_media_caja"].append(len(cajeros.queue))
                    stats["cola_media_entrega"].append(len(personal_entrega.queue))
            env.process(monitorear())
            
            cliente_id = 0
            # Para validación: guardar tiempos entre llegadas
            ultima_llegada = 0.0
            tiempos_entre_llegadas = []
            tiempos_atencion_asesor = []
            
            def llegada_cliente():
                nonlocal cliente_id, ultima_llegada
                while True:
                    intervalo = np.random.exponential(1.0 / config.tasa_llegada_por_min)
                    yield env.timeout(intervalo)
                    # Recolectar tiempo entre llegadas (solo primera réplica)
                    if r == 0:
                        ahora = env.now
                        if ultima_llegada > 0:
                            tiempos_entre_llegadas.append(ahora - ultima_llegada)
                        ultima_llegada = ahora
                    cliente_id += 1
                    necesita_credito = np.random.random() < config.prob_credito
                    r_interes = np.random.random()
                    if r_interes < config.prob_interes_bajo:
                        interes = InteresCliente.BAJO
                    elif r_interes < config.prob_interes_bajo + config.prob_interes_medio:
                        interes = InteresCliente.MEDIO
                    else:
                        interes = InteresCliente.ALTO
                    cliente = Cliente(id=cliente_id, tiempo_llegada=env.now, necesita_credito=necesita_credito, interes=interes)
                    env.process(proceso_cliente(env, cliente, asesores, cajeros, personal_entrega, config, stats, tiempos_atencion_asesor if r==0 else None))
            
            env.process(llegada_cliente())
            env.run(until=config.duracion_jornada_min)
            
            # Almacenar datos de validación (solo primera réplica)
            if r == 0:
                self.datos_validacion["tiempos_entre_llegadas"] = tiempos_entre_llegadas
                self.datos_validacion["tiempos_atencion_asesor"] = tiempos_atencion_asesor
            
            # Acumular métricas para promedio
            for key in ["ventas_exitosas", "abandonos", "clientes_atendidos"]:
                metricas_acum[key] = metricas_acum.get(key, 0) + stats[key]
            metricas_acum["tiempos_sistema"] = metricas_acum.get("tiempos_sistema", []) + stats["tiempos_sistema"]
            for key in ["tiempos_espera_asesor", "tiempos_espera_credito", "tiempos_espera_caja", "tiempos_espera_entrega"]:
                metricas_acum[key] = metricas_acum.get(key, []) + stats[key]
            for key in ["utilizacion_asesores", "utilizacion_cajeros", "utilizacion_entrega", "cola_media_asesor", "cola_media_caja", "cola_media_entrega"]:
                metricas_acum[key] = metricas_acum.get(key, []) + stats[key]
        
        # Promedios
        n_replicas = replicas
        metricas_finales = {
            "total_clientes": metricas_acum.get("clientes_atendidos", 0) / n_replicas,
            "ventas_exitosas": metricas_acum.get("ventas_exitosas", 0) / n_replicas,
            "abandonos": metricas_acum.get("abandonos", 0) / n_replicas,
            "tasa_conversion": (metricas_acum.get("ventas_exitosas", 0) / max(1, metricas_acum.get("clientes_atendidos", 1))) * 100,
            "tiempo_promedio_sistema_min": np.mean(metricas_acum["tiempos_sistema"]) if metricas_acum["tiempos_sistema"] else 0,
            "tiempo_espera_asesor_prom": np.mean(metricas_acum["tiempos_espera_asesor"]) if metricas_acum["tiempos_espera_asesor"] else 0,
            "tiempo_espera_credito_prom": np.mean(metricas_acum["tiempos_espera_credito"]) if metricas_acum["tiempos_espera_credito"] else 0,
            "tiempo_espera_caja_prom": np.mean(metricas_acum["tiempos_espera_caja"]) if metricas_acum["tiempos_espera_caja"] else 0,
            "tiempo_espera_entrega_prom": np.mean(metricas_acum["tiempos_espera_entrega"]) if metricas_acum["tiempos_espera_entrega"] else 0,
            "utilizacion_asesores": np.mean(metricas_acum["utilizacion_asesores"]) if metricas_acum["utilizacion_asesores"] else 0,
            "utilizacion_cajeros": np.mean(metricas_acum["utilizacion_cajeros"]) if metricas_acum["utilizacion_cajeros"] else 0,
            "utilizacion_entrega": np.mean(metricas_acum["utilizacion_entrega"]) if metricas_acum["utilizacion_entrega"] else 0,
            "cola_media_asesor": np.mean(metricas_acum["cola_media_asesor"]) if metricas_acum["cola_media_asesor"] else 0,
            "cola_media_caja": np.mean(metricas_acum["cola_media_caja"]) if metricas_acum["cola_media_caja"] else 0,
            "cola_media_entrega": np.mean(metricas_acum["cola_media_entrega"]) if metricas_acum["cola_media_entrega"] else 0,
        }
        self.resultados = metricas_finales
        return metricas_finales
    
# Proceso individual del cliente
def proceso_cliente(env, cliente, asesores, cajeros, personal_entrega, config, stats, lista_tiempos_asesor=None):
    # 1. Espera y atención asesor
    llegada_asesor = env.now
    with asesores.request() as req:
        yield req
        tiempo_espera_asesor = env.now - llegada_asesor
        stats["tiempos_espera_asesor"].append(tiempo_espera_asesor)
        cliente.tiempo_inicio_asesor = env.now
        # Tiempo de atención asesor (triangular)
        duracion = np.random.triangular(
            config.tiempo_asesor_min,
            config.tiempo_asesor_moda,
            config.tiempo_asesor_max
        )
        if lista_tiempos_asesor is not None:
            lista_tiempos_asesor.append(duracion)
        yield env.timeout(duracion)
        cliente.tiempo_fin_asesor = env.now
    
    # 2. Decisión post asesoría
    if not cliente.necesita_credito:
        # Decisión de compra según interés
        prob = config.prob_compra_sin_credito[cliente.interes]
        compra = np.random.random() < prob
        if not compra:
            cliente.estado = EstadoCliente.ABANDONO
            cliente.tiempo_abandono = env.now
            stats["abandonos"] += 1
            return
    else:
        # 3. Proceso de crédito (sin recurso, solo retardo)
        llegada_credito = env.now
        cliente.tiempo_inicio_credito = env.now
        duracion_credito = np.random.uniform(config.tiempo_credito_min, config.tiempo_credito_max)
        yield env.timeout(duracion_credito)
        cliente.tiempo_fin_credito = env.now
        tiempo_espera_credito = env.now - llegada_credito
        stats["tiempos_espera_credito"].append(tiempo_espera_credito)
        aprobado = np.random.random() < config.prob_aprobacion_credito
        cliente.credito_aprobado = aprobado
        if not aprobado:
            cliente.estado = EstadoCliente.ABANDONO
            cliente.tiempo_abandono = env.now
            stats["abandonos"] += 1
            return
    
    # 4. Pago en caja
    llegada_caja = env.now
    with cajeros.request() as req:
        yield req
        cliente.tiempo_inicio_caja = env.now
        tiempo_espera_caja = env.now - llegada_caja
        stats["tiempos_espera_caja"].append(tiempo_espera_caja)
        duracion_caja = np.random.uniform(config.tiempo_caja_min, config.tiempo_caja_max)
        yield env.timeout(duracion_caja)
        cliente.tiempo_fin_caja = env.now
    
    # 5. Entrega
    llegada_entrega = env.now
    with personal_entrega.request() as req:
        yield req
        cliente.tiempo_inicio_entrega = env.now
        tiempo_espera_entrega = env.now - llegada_entrega
        stats["tiempos_espera_entrega"].append(tiempo_espera_entrega)
        duracion_entrega = np.random.triangular(
            config.tiempo_entrega_min,
            config.tiempo_entrega_moda,
            config.tiempo_entrega_max
        )
        yield env.timeout(duracion_entrega)
        cliente.tiempo_fin_entrega = env.now
    
    cliente.estado = EstadoCliente.VENTA_EXITOSA
    tiempo_total = env.now - cliente.tiempo_llegada
    stats["tiempos_sistema"].append(tiempo_total)
    stats["ventas_exitosas"] += 1