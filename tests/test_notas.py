# tests/test_notas.py
import unittest
# Suponiendo que importas las validaciones o funciones del modelo/controlador del Sprint 2
from validaciones_notas import validar_nota, calcular_regularidad

class TestModuloNotas(unittest.TestCase):
    
    def test_nota_valida(self):
        # Verifica que notas entre 1 y 10 sean aceptadas
        self.assertTrue(validar_nota(6))
        self.assertTrue(validar_nota(10))
        self.assertTrue(validar_nota(1))

    def test_nota_invalida(self):
        # Verifica que notas fuera de rango o letras den error
        self.assertFalse(validar_nota(0))
        self.assertFalse(validar_nota(11))
        self.assertFalse(validar_nota(-5))

    def test_calculo_regularidad_regular(self):
        # Nota mayor o igual a 6 otorga regularidad
        self.assertEqual(calcular_regularidad(6), "Regular")
        self.assertEqual(calcular_regularidad(8), "Regular")

    def test_calculo_regularidad_libre(self):
        # Nota menor a 6 deja al alumno libre
        self.assertEqual(calcular_regularidad(5), "Libre")
        self.assertEqual(calcular_regularidad(2), "Libre")

if __name__ == '__main__':
    unittest.main()