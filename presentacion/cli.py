import argparse
from tabulate import tabulate
from core.entidades import ConfiguracionSimulacion
from infraestructura.motor_simpy import SimuladorSimPy
from infraestructura.repositorio_resultados import RepositorioJSON
from core.casos_uso import OrquestadorSimulacion
from experimentos.escenarios import obtener_escenarios_base

def ejecutar_cli():
    parser = argparse.ArgumentParser(description="Simulación DES de Concesionario")
    parser.add_argument("--escenario", type=str, default="Base_3Asesores", help="Nombre del escenario a ejecutar")
    parser.add_argument("--todos", action="store_true", help="Ejecutar todos los escenarios predefinidos")
    parser.add_argument("--ver", action="store_true", help="Mostrar resultados históricos")
    args = parser.parse_args()
    
    motor = SimuladorSimPy()
    repo = RepositorioJSON()
    orquestador = OrquestadorSimulacion(motor, repo)
    
    if args.ver:
        historial = repo.cargar_todos()
        if historial:
            table = []
            for h in historial:
                m = h["metricas"]
                table.append([
                    h["escenario"],
                    m["total_clientes"],
                    m["ventas_exitosas"],
                    f"{m['tasa_conversion']:.1f}%",
                    f"{m['tiempo_promedio_sistema_min']:.1f}",
                    f"{m['utilizacion_asesores']:.2f}"
                ])
            print(tabulate(table, headers=["Escenario", "Clientes", "Ventas", "Conversión", "Tiempo prom (min)", "Uso asesores"]))
        else:
            print("No hay resultados almacenados. Ejecute simulación primero.")
        return
    
    if args.todos:
        escenarios = obtener_escenarios_base()
        print(f"Ejecutando {len(escenarios)} escenarios...")
        for config, nombre in escenarios:
            print(f"Corriendo {nombre}...")
            metricas = orquestador.ejecutar_escenario(config, nombre)
            print(f"  Ventas: {metricas['ventas_exitosas']}/{metricas['total_clientes']} -> {metricas['tasa_conversion']:.1f}%")
        print("Todos los escenarios completados.")
    else:
        # Buscar escenario por nombre o crear uno personalizado
        escenarios_base = obtener_escenarios_base()
        config = None
        for c, n in escenarios_base:
            if n == args.escenario:
                config = c
                break
        if config is None:
            # Permitir configuración personalizada vía parámetros adicionales (simplificado)
            config = ConfiguracionSimulacion()
        metricas = orquestador.ejecutar_escenario(config, args.escenario)
        print("\nResultados de la simulación:")
        for k, v in metricas.items():
            print(f"  {k}: {v:.2f}" if isinstance(v, float) else f"  {k}: {v}")