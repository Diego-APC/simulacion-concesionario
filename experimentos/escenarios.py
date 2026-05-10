from core.entidades import ConfiguracionSimulacion

def obtener_escenarios_base():
    """Define varios escenarios para experimentos"""
    config_base = ConfiguracionSimulacion()
    escenarios = []
    
    # Escenario 1: Base (3 asesores)
    escenarios.append((config_base, "Base_3Asesores"))
    
    # Escenario 2: 2 asesores
    config2 = ConfiguracionSimulacion(num_asesores=2)
    escenarios.append((config2, "2_Asesores"))
    
    # Escenario 3: 4 asesores
    config3 = ConfiguracionSimulacion(num_asesores=4)
    escenarios.append((config3, "4_Asesores"))
    
    # Escenario 4: Mayor tasa de llegada (más clientes)
    config4 = ConfiguracionSimulacion(tasa_llegada_por_min=0.3)  # media 3.33 min
    escenarios.append((config4, "AltaDemanda_3Asesores"))
    
    # Escenario 5: Menor probabilidad de crédito
    config5 = ConfiguracionSimulacion(prob_credito=0.2)
    escenarios.append((config5, "BajoCredito_3Asesores"))
    
    return escenarios