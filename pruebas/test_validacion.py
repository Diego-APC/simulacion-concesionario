import unittest
import numpy as np
from core.validacion import prueba_kolmogorov_smirnov, validar_distribucion_llegadas

class TestValidacion(unittest.TestCase):
    def test_ks_exponencial(self):
        # Generar datos exponenciales con tasa 0.2 (media 5)
        datos = np.random.exponential(5, 1000)
        from scipy.stats import expon
        def cdf(x):
            return expon.cdf(x, scale=5)
        res = prueba_kolmogorov_smirnov(datos, cdf)
        self.assertTrue(res["acepta_H0"], "Debería aceptar distribución exponencial")
    
    def test_ks_no_exponencial(self):
        datos = np.random.normal(5, 1, 1000)
        from scipy.stats import expon
        def cdf(x):
            return expon.cdf(x, scale=5)
        res = prueba_kolmogorov_smirnov(datos, cdf)
        self.assertFalse(res["acepta_H0"], "No debería aceptar exponencial")

if __name__ == "__main__":
    unittest.main()