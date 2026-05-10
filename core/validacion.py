import numpy as np
from scipy.stats import chisquare, kstest
from typing import Dict, List, Tuple, Any

def prueba_chi_cuadrado(datos_observados: List[float], esperados: List[float], n_bins: int = 10) -> Dict[str, Any]:
    """
    Prueba chi-cuadrado para datos observados vs distribución esperada.
    Se discretizan los datos en 'n_bins' intervalos.
    Retorna estadístico, p-valor y si acepta H0 (alpha=0.05).
    """
    if len(datos_observados) == 0:
        return {"error": "No hay datos"}
    # Crear bins con la misma frecuencia esperada (uniforme) o usar rangos
    min_val, max_val = np.min(datos_observados), np.max(datos_observados)
    bins = np.linspace(min_val, max_val, n_bins+1)
    observed_freq, _ = np.histogram(datos_observados, bins=bins)
    expected_freq = np.full(n_bins, len(datos_observados) / n_bins)
    # Evitar frecuencias esperadas muy bajas
    # Si hay bins con expected < 5, combinarlos (simplificado, aquí se asume suficientes datos)
    stat, p = chisquare(observed_freq, f_exp=expected_freq)
    return {
        "estadistico": stat,
        "p_valor": p,
        "acepta_H0": p > 0.05,
        "n_datos": len(datos_observados)
    }

def prueba_kolmogorov_smirnov(datos: List[float], cdf_func, args=()) -> Dict[str, Any]:
    """
    Prueba KS comparando datos con una función de distribución acumulativa teórica.
    cdf_func: función CDF teórica (ej. lambda x: exponencial.cdf(x, scale=media))
    Retorna estadístico D, p-valor.
    """
    if len(datos) == 0:
        return {"error": "No hay datos"}
    stat, p = kstest(datos, cdf_func, args=args)
    return {
        "estadistico_D": stat,
        "p_valor": p,
        "acepta_H0": p > 0.05
    }

def validar_distribucion_llegadas(tiempos_entre_llegadas: List[float], tasa_por_min: float) -> Dict:
    """
    Valida que los tiempos entre llegadas sigan una exponencial con media 1/tasa.
    """
    from scipy.stats import expon
    media_esperada = 1.0 / tasa_por_min
    def cdf_expon(x):
        return expon.cdf(x, scale=media_esperada)
    return prueba_kolmogorov_smirnov(tiempos_entre_llegadas, cdf_expon)

def validar_distribucion_asesor(tiempos_atencion: List[float], params_triangular: Tuple) -> Dict:
    """
    Valida que los tiempos de atención sigan triangular(min, moda, max).
    params_triangular = (min, moda, max)
    """
    from scipy.stats import triang
    a, c, b = params_triangular
    # La distribución triangular en scipy tiene parámetros: loc=a, scale=b-a, c=(c-a)/(b-a)
    loc = a
    scale = b - a
    c_param = (c - a) / scale if scale > 0 else 0.5
    def cdf_triangular(x):
        return triang.cdf(x, c=c_param, loc=loc, scale=scale)
    return prueba_kolmogorov_smirnov(tiempos_atencion, cdf_triangular)