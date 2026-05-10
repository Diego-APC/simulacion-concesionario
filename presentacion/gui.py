import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from threading import Thread
from core.entidades import ConfiguracionSimulacion
from infraestructura.motor_simpy import SimuladorSimPy
from infraestructura.repositorio_resultados import RepositorioJSON
from core.casos_uso import OrquestadorSimulacion
from core.validacion import validar_distribucion_llegadas, validar_distribucion_asesor

class SimulacionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Concesionario - DES")
        self.root.geometry("1200x700")
        self.motor = SimuladorSimPy()
        self.repo = RepositorioJSON()
        self.orquestador = OrquestadorSimulacion(self.motor, self.repo)
        self.config = ConfiguracionSimulacion()
        self.resultados = None
        self.datos_validacion = None
        
        self.crear_widgets()
    
    def crear_widgets(self):
        # Frame izquierdo: controles
        frame_control = ttk.LabelFrame(self.root, text="Configuración", padding=10)
        frame_control.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # Parámetros editables
        ttk.Label(frame_control, text="Número de asesores:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.num_asesores = tk.IntVar(value=3)
        ttk.Spinbox(frame_control, from_=1, to=10, textvariable=self.num_asesores, width=5).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame_control, text="Número de cajeros:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.num_cajeros = tk.IntVar(value=1)
        ttk.Spinbox(frame_control, from_=1, to=5, textvariable=self.num_cajeros, width=5).grid(row=1, column=1, pady=5)

        ttk.Label(frame_control, text="Personal de entrega:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.num_entrega = tk.IntVar(value=1)
        ttk.Spinbox(frame_control, from_=1, to=5, textvariable=self.num_entrega, width=5).grid(row=2, column=1, pady=5)

        
        ttk.Label(frame_control, text="Tasa llegada (clientes/min):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tasa_llegada = tk.DoubleVar(value=0.2)
        ttk.Entry(frame_control, textvariable=self.tasa_llegada, width=10).grid(row=3, column=1, pady=5)
        
        ttk.Label(frame_control, text="Prob. necesidad crédito:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.prob_credito = tk.DoubleVar(value=0.4)
        ttk.Scale(frame_control, from_=0, to=1, variable=self.prob_credito, orient=tk.HORIZONTAL, length=100).grid(row=4, column=1, pady=5)
        ttk.Label(frame_control, textvariable=self.prob_credito).grid(row=4, column=2)
        
        ttk.Label(frame_control, text="Número de réplicas:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.replicas = tk.IntVar(value=1)
        ttk.Spinbox(frame_control, from_=1, to=20, textvariable=self.replicas, width=5).grid(row=5, column=1, pady=5)
        
        btn_simular = ttk.Button(frame_control, text="Iniciar Simulación", command=self.iniciar_simulacion)
        btn_simular.grid(row=6, column=0, columnspan=2, pady=20)
        
        btn_validar = ttk.Button(frame_control, text="Validar distribuciones", command=self.validar_distribuciones)
        btn_validar.grid(row=7, column=0, columnspan=2, pady=5)
        
        # Frame derecho: pestañas para resultados y gráficos
        notebook = ttk.Notebook(self.root)
        notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de resultados texto
        self.frame_resultados = ttk.Frame(notebook)
        notebook.add(self.frame_resultados, text="Resultados")
        self.text_resultados = tk.Text(self.frame_resultados, wrap=tk.WORD, height=20, width=60)
        self.text_resultados.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña de gráficos
        self.frame_graficos = ttk.Frame(notebook)
        notebook.add(self.frame_graficos, text="Gráficos")
        
        # Pestaña de validación
        self.frame_validacion = ttk.Frame(notebook)
        notebook.add(self.frame_validacion, text="Validación")
        self.text_validacion = tk.Text(self.frame_validacion, wrap=tk.WORD, height=20, width=60)
        self.text_validacion.pack(fill=tk.BOTH, expand=True)
    
    def iniciar_simulacion(self):
        # Deshabilitar botón durante simulación
        self.text_resultados.delete(1.0, tk.END)
        self.text_resultados.insert(tk.END, "Simulando... por favor espere.\n")
        self.root.update()
        # Actualizar configuración
        self.config.num_asesores = self.num_asesores.get()
        self.config.tasa_llegada_por_min = self.tasa_llegada.get()
        self.config.prob_credito = self.prob_credito.get()
        self.config.num_cajeros = self.num_cajeros.get()
        self.config.num_personal_entrega = self.num_entrega.get()
        self.config.semilla = 42  # fija para reproducibilidad
        replicas = self.replicas.get()
        
        # Ejecutar en hilo separado para no bloquear GUI
        def ejecutar():
            try:
                metricas = self.motor.ejecutar(self.config, replicas=replicas)
                self.resultados = metricas
                self.datos_validacion = self.motor.datos_validacion
                self.root.after(0, self.mostrar_resultados)
                self.root.after(0, self.graficar_resultados)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        Thread(target=ejecutar).start()
    
    def mostrar_resultados(self):
        self.text_resultados.delete(1.0, tk.END)
        m = self.resultados
        texto = f"RESUMEN DE SIMULACIÓN (promedio sobre {self.replicas.get()} réplicas)\n"
        texto += f"Total clientes atendidos: {m['total_clientes']:.1f}\n"
        texto += f"Ventas exitosas: {m['ventas_exitosas']:.1f}\n"
        texto += f"Abandonos: {m['abandonos']:.1f}\n"
        texto += f"Tasa de conversión: {m['tasa_conversion']:.1f}%\n"
        texto += f"Tiempo promedio en sistema (compradores): {m['tiempo_promedio_sistema_min']:.2f} min\n"
        texto += f"Tiempo espera asesor: {m['tiempo_espera_asesor_prom']:.2f} min\n"
        texto += f"Tiempo espera crédito: {m['tiempo_espera_credito_prom']:.2f} min\n"
        texto += f"Tiempo espera caja: {m['tiempo_espera_caja_prom']:.2f} min\n"
        texto += f"Tiempo espera entrega: {m['tiempo_espera_entrega_prom']:.2f} min\n"
        texto += f"Utilización asesores: {m['utilizacion_asesores']:.2%}\n"
        texto += f"Utilización cajeros: {m['utilizacion_cajeros']:.2%}\n"
        texto += f"Utilización entrega: {m['utilizacion_entrega']:.2%}\n"
        texto += f"Cola media asesores: {m['cola_media_asesor']:.2f} clientes\n"
        texto += f"Cola media caja: {m['cola_media_caja']:.2f}\n"
        texto += f"Cola media entrega: {m['cola_media_entrega']:.2f}\n"
        self.text_resultados.insert(tk.END, texto)
    
    def graficar_resultados(self):
        # Limpiar frame de gráficos
        for widget in self.frame_graficos.winfo_children():
            widget.destroy()
        
        # Gráfico de barras de tiempos
        fig, axes = plt.subplots(2, 2, figsize=(8, 6))
        tiempos = ['Asesor', 'Crédito', 'Caja', 'Entrega']
        valores = [
            self.resultados['tiempo_espera_asesor_prom'],
            self.resultados['tiempo_espera_credito_prom'],
            self.resultados['tiempo_espera_caja_prom'],
            self.resultados['tiempo_espera_entrega_prom']
        ]
        axes[0,0].bar(tiempos, valores, color='skyblue')
        axes[0,0].set_title('Tiempos de espera promedio (min)')
        axes[0,0].set_ylabel('Minutos')
        
        # Gráfico de utilización
        recursos = ['Asesores', 'Cajeros', 'Entrega']
        uso = [
            self.resultados['utilizacion_asesores']* 100,
            self.resultados['utilizacion_cajeros']* 100,
            self.resultados['utilizacion_entrega']* 100
        ]
        bars = axes[0,1].bar(recursos, uso, color='lightgreen')
        axes[0,1].set_title('Utilización de recursos')
        axes[0,1].set_ylabel('Porcentaje (%)')
        axes[0,1].set_ylim(0, 100)

        # Etiquetas de datos
        for bar, val in zip(bars, uso):
            axes[0,1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=9)
        
        # Evolución de cola (simulada, aquí solo mostramos promedio)
        colas = ['Asesores', 'Caja', 'Entrega']
        longitudes = [
            self.resultados['cola_media_asesor'],
            self.resultados['cola_media_caja'],
            self.resultados['cola_media_entrega']
        ]
        axes[1,0].bar(colas, longitudes, color='salmon')
        axes[1,0].set_title('Longitud promedio de colas')
        axes[1,0].set_ylabel('Clientes')
        
        # Conversión y totales
        axes[1,1].pie([self.resultados['ventas_exitosas'], self.resultados['abandonos']], 
                      labels=['Ventas', 'Abandonos'], autopct='%1.1f%%')
        axes[1,1].set_title('Composición final')
        
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=self.frame_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def validar_distribuciones(self):
        if self.datos_validacion is None:
            messagebox.showinfo("Validación", "Primero ejecute la simulación para obtener datos.")
            return
        self.text_validacion.delete(1.0, tk.END)
        # Validar tiempos entre llegadas (exponencial)
        llegadas = self.datos_validacion.get("tiempos_entre_llegadas", [])
        if len(llegadas) > 0:
            res_lleg = validar_distribucion_llegadas(llegadas, self.config.tasa_llegada_por_min)
            self.text_validacion.insert(tk.END, "VALIDACIÓN DISTRIBUCIÓN LLEGADAS (Exponencial)\n")
            self.text_validacion.insert(tk.END, f"Estadístico KS: {res_lleg.get('estadistico_D', 0):.4f}\n")
            self.text_validacion.insert(tk.END, f"p-valor: {res_lleg.get('p_valor', 0):.4f}\n")
            self.text_validacion.insert(tk.END, f"¿Acepta H0 (distribución correcta)? {res_lleg.get('acepta_H0', False)}\n\n")
        else:
            self.text_validacion.insert(tk.END, "No hay suficientes datos de llegadas.\n")
        
        # Validar tiempos de atención asesor (triangular)
        atenciones = self.datos_validacion.get("tiempos_atencion_asesor", [])
        if len(atenciones) > 0:
            params = (self.config.tiempo_asesor_min, self.config.tiempo_asesor_moda, self.config.tiempo_asesor_max)
            res_asesor = validar_distribucion_asesor(atenciones, params)
            self.text_validacion.insert(tk.END, "VALIDACIÓN DISTRIBUCIÓN ATENCIÓN ASESOR (Triangular)\n")
            self.text_validacion.insert(tk.END, f"Estadístico KS: {res_asesor.get('estadistico_D', 0):.4f}\n")
            self.text_validacion.insert(tk.END, f"p-valor: {res_asesor.get('p_valor', 0):.4f}\n")
            self.text_validacion.insert(tk.END, f"¿Acepta H0? {res_asesor.get('acepta_H0', False)}\n")
        else:
            self.text_validacion.insert(tk.END, "No hay datos de tiempos de atención asesor.\n")

def ejecutar_gui():
    root = tk.Tk()
    app = SimulacionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    ejecutar_gui()