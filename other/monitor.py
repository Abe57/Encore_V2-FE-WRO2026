# Script de python para monitorear valores a través de wifi

import socket
import threading
import json
import time
import tkinter as tk
from tkinter import ttk, scrolledtext

UDP_PORT = 4210
BUFFER_SIZE = 2048

class TelemetryMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Monitor de Telemetría - Robot WRO")
        self.root.geometry("640x600")
        self.root.configure(bg="#1e1e1e")

        self.ultimo_paquete = time.time()
        self.conectado = False

        self._construir_interfaz()

        self.sock = None
        self.corriendo = True
        self.hilo = threading.Thread(target=self._escuchar_udp, daemon=True)
        self.hilo.start()

        self._revisar_conexion()

    def _construir_interfaz(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TLabel", background="#1e1e1e", foreground="white", font=("Segoe UI", 11))
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 13, "bold"))
        estilo.configure("TLabelframe", background="#1e1e1e", foreground="white")
        estilo.configure("TLabelframe.Label", background="#1e1e1e", foreground="#4fc3f7", font=("Segoe UI", 11, "bold"))

        # estado de conexion
        marco_estado = ttk.Frame(self.root)
        marco_estado.pack(fill="x", padx=10, pady=(10, 0))
        self.lbl_estado = ttk.Label(marco_estado, text="● Esperando datos...", style="Titulo.TLabel", foreground="orange")
        self.lbl_estado.pack(side="left")

        # sensores de proximidad
        marco_us = ttk.Labelframe(self.root, text="Sensores de Proximidad (HC-SR04)")
        marco_us.pack(fill="x", padx=10, pady=10)
        self.marco_us_interno = ttk.Frame(marco_us)
        self.marco_us_interno.pack(fill="x", padx=10, pady=10)
        self.labels_us = {}  # se crean dinámicamente al recibir el primer paquete

        # BNO055
        marco_bno = ttk.Labelframe(self.root, text="IMU (BNO055)")
        marco_bno.pack(fill="x", padx=10, pady=10)
        interno_bno = ttk.Frame(marco_bno)
        interno_bno.pack(fill="x", padx=10, pady=10)

        self.lbl_heading = self._crear_dato(interno_bno, "Heading:", 0)
        self.lbl_roll = self._crear_dato(interno_bno, "Roll:", 1)
        self.lbl_pitch = self._crear_dato(interno_bno, "Pitch:", 2)
        self.lbl_calib = self._crear_dato(interno_bno, "Calibración (sys/gyro/acc/mag):", 3)
        self.lbl_cw = self._crear_dato(interno_bno, "Dirección cw:", 4)
        self.lbl_ang_to_match = self._crear_dato(interno_bno, "angToMatch:", 5)
        self.lbl_turn_offset = self._crear_dato(interno_bno, "turnOffset:", 6)
        self.lbl_ini_angle = self._crear_dato(interno_bno, "ini_angle:", 7)
        self.lbl_accumulated_yaw = self._crear_dato(interno_bno, "accumulatedYaw:", 8)

        # consola
        marco_consola = ttk.Labelframe(self.root, text="Consola / Log de la ESP32")
        marco_consola.pack(fill="both", expand=True, padx=10, pady=10)
        self.consola = scrolledtext.ScrolledText(
            marco_consola, bg="#0d1117", fg="#58d68d", font=("Consolas", 10),
            insertbackground="white", height=12
        )
        self.consola.pack(fill="both", expand=True, padx=5, pady=5)
        self.consola.configure(state="disabled")

    def _crear_dato(self, padre, texto, fila):
        ttk.Label(padre, text=texto).grid(row=fila, column=0, sticky="w", pady=3)
        valor = ttk.Label(padre, text="--", foreground="#4fc3f7")
        valor.grid(row=fila, column=1, sticky="w", padx=10, pady=3)
        return valor

    def _escuchar_udp(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", UDP_PORT))

        while self.corriendo:
            try:
                datos, _ = self.sock.recvfrom(BUFFER_SIZE)
                self.ultimo_paquete = time.time()
                paquete = json.loads(datos.decode("utf-8", errors="ignore"))
                self.root.after(0, self._procesar_paquete, paquete)
            except (OSError, json.JSONDecodeError):
                continue

    def _procesar_paquete(self, paquete):
        tipo = paquete.get("tipo")

        if tipo == "sensores":
            self._actualizar_sensores_us(paquete.get("us", {}))
            bno = paquete.get("bno")
            if bno:
                self.lbl_heading.config(text=f"{bno.get('heading', '--')}°")
                self.lbl_roll.config(text=f"{bno.get('roll', '--')}°")
                self.lbl_pitch.config(text=f"{bno.get('pitch', '--')}°")
                self.lbl_calib.config(
                    text=f"{bno.get('cal_sys','-')}/{bno.get('cal_gyro','-')}/"
                         f"{bno.get('cal_accel','-')}/{bno.get('cal_mag','-')}"
                )
            else:
                self.lbl_heading.config(text="BNO055 no detectado")

            self.lbl_cw.config(text=str(paquete.get('cw', '--')))
            ang_to_match = paquete.get('angToMatch')
            self.lbl_ang_to_match.config(text=f"{ang_to_match}°" if ang_to_match is not None else "--")
            self.lbl_turn_offset.config(text=str(paquete.get('turnOffset', '--')))
            self.lbl_ini_angle.config(text=f"{paquete.get('ini_angle', '--')}°")
            self.lbl_accumulated_yaw.config(text=f"{paquete.get('accumulatedYaw', '--')}°")

        elif tipo == "log":
            self._agregar_consola(paquete.get("msg", ""))

    def _actualizar_sensores_us(self, datos_us):
        for nombre, distancia in datos_us.items():
            if nombre not in self.labels_us:
                fila = len(self.labels_us)
                ttk.Label(self.marco_us_interno, text=f"{nombre}:").grid(row=fila, column=0, sticky="w", pady=3)
                valor = ttk.Label(self.marco_us_interno, text="--", foreground="#4fc3f7", font=("Segoe UI", 11, "bold"))
                valor.grid(row=fila, column=1, sticky="w", padx=10, pady=3)
                self.labels_us[nombre] = valor

            if distancia is not None and distancia >= 0:
                self.labels_us[nombre].config(text=f"{distancia:.1f} cm")
            else:
                self.labels_us[nombre].config(text="sin eco")

    def _agregar_consola(self, mensaje):
        marca = time.strftime("%H:%M:%S")
        self.consola.configure(state="normal")
        self.consola.insert("end", f"[{marca}] {mensaje}\n")
        self.consola.see("end")
        self.consola.configure(state="disabled")

    def _revisar_conexion(self):
        if time.time() - self.ultimo_paquete < 1.5:
            if not self.conectado:
                self.conectado = True
                self.lbl_estado.config(text="● Conectado - recibiendo datos", foreground="#58d68d")
        else:
            if self.conectado or self.lbl_estado.cget("text").startswith("●"):
                self.conectado = False
                self.lbl_estado.config(text="● Sin señal de la ESP32...", foreground="orange")

        self.root.after(500, self._revisar_conexion)

    def cerrar(self):
        self.corriendo = False
        if self.sock:
            self.sock.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TelemetryMonitor(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()
