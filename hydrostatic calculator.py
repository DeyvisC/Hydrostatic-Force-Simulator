import customtkinter as ctk
import tkinter as tk
from tkinter import Canvas
import math


# --- CONFIGURACIÓN INICIAL ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# --- DATOS Y FACTORES DE CONVERSIÓN ---
FLUIDOS = {
    "Agua":         {"densidad": 1000,  "color": "#03A9F4", "borde": "#01579B"},
    "Aceite":       {"densidad": 920,   "color": "#FDD835", "borde": "#FBC02D"},
    "Mercurio":     {"densidad": 13600, "color": "#B0BEC5", "borde": "#546E7A"},
    "Gasolina":     {"densidad": 680,   "color": "#FFB74D", "borde": "#E65100"},
    "Glicerina":    {"densidad": 1260,  "color": "#BA68C8", "borde": "#8E24AA"},
    "Agua de Mar":  {"densidad": 1027,  "color": "#26A69A", "borde": "#00695C"},
    "Alcohol":      {"densidad": 789,   "color": "#EF5350", "borde": "#C62828"}
}


CONV_PRESION = {"Pa": 1.0, "atm": 101325.0, "PSI": 6894.76, "mmHg": 133.322, "Bar": 100000.0}
CONV_DENSIDAD = {"kg/m³": 1.0, "g/cm³": 1000.0, "lb/ft³": 16.0185}
CONV_LONGITUD = {
    "Metros (m)": 1.0,
    "Centímetros (cm)": 0.01,
    "Milímetros (mm)": 0.001,
    "Kilómetros (km)": 1000.0,
    "Pies (ft)": 0.3048,
    "Pulgadas (in)": 0.0254
}


class AppHidrostatica(ctk.CTk):
    def __init__(self):
        super().__init__()


        self.title("Suite Hidrostática Profesional v19.0 - All in One")
        self.geometry("1400x900")
       
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self, width=1350, height=850)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        self.tabview.add("CALCULADORA")
        self.tabview.add("SIMULADOR 3D")

        self._init_calculadora(self.tabview.tab("CALCULADORA"))
        self._init_simulador(self.tabview.tab("SIMULADOR 3D"))


    # =========================================================================
    #  MÓDULO 1: CALCULADORA (Interfaz Moderna + Conversor Mejorado)
    # =========================================================================
    def _init_calculadora(self, parent):
        # Variables
        self.c_densidad = tk.DoubleVar(value=1000.0)
        self.c_gravedad = tk.DoubleVar(value=9.81)
        self.c_altura = tk.DoubleVar(value=2.0)
        self.c_largo = tk.DoubleVar(value=3.0)
        self.c_ancho = tk.DoubleVar(value=2.0)
        self.c_radio = tk.DoubleVar(value=1.5)
       
        self.conv_valor = tk.DoubleVar(value=1.0)
        self.conv_res = tk.StringVar(value="---")


        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.columnconfigure(2, weight=1)


        frame_datos = ctk.CTkFrame(parent)
        frame_datos.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
       
        ctk.CTkLabel(frame_datos, text="PARÁMETROS", font=("Roboto Medium", 20)).pack(pady=20)


        ctk.CTkLabel(frame_datos, text="Fluido:").pack(anchor="w", padx=20)
        self.c_combo_fluido = ctk.CTkComboBox(frame_datos, values=list(FLUIDOS.keys()), command=self._set_fluido_calc)
        self.c_combo_fluido.pack(fill="x", padx=20, pady=(0, 15))
        self.c_combo_fluido.set("Agua")


        self._crear_input(frame_datos, "Densidad (kg/m³):", self.c_densidad)
        self._crear_input(frame_datos, "Gravedad (m/s²):", self.c_gravedad)


        ctk.CTkLabel(frame_datos, text="Geometría del Tanque:", text_color="#3B8ED0").pack(anchor="w", padx=20, pady=(20,5))
        self.c_combo_geo = ctk.CTkComboBox(frame_datos, values=["Rectangular", "Cilíndrica"], command=self._update_geo_inputs)
        self.c_combo_geo.pack(fill="x", padx=20, pady=5)
       
        self.geo_frame = ctk.CTkFrame(frame_datos, fg_color="transparent")
        self.geo_frame.pack(fill="x", padx=5, pady=5)
        self._update_geo_inputs("Rectangular")


        ctk.CTkButton(frame_datos, text="CALCULAR RESULTADOS", command=self._calcular_calc,
                      height=50, font=("Roboto Medium", 14)).pack(fill="x", padx=20, pady=30)


        # --- COLUMNA 2: RESULTADOS ---
        frame_res = ctk.CTkFrame(parent, fg_color="transparent")
        frame_res.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


        self.res_vars = {
            "P": tk.StringVar(value="---"),
            "F": tk.StringVar(value="---"),
            "V": tk.StringVar(value="---")
        }


        self._crear_tarjeta_resultado(frame_res, "PRESIÓN HIDROSTÁTICA", self.res_vars["P"])
        self._crear_tarjeta_resultado(frame_res, "FUERZA TOTAL EN FONDO", self.res_vars["F"])
        self._crear_tarjeta_resultado(frame_res, "VOLUMEN DE LÍQUIDO", self.res_vars["V"])


        frame_conv = ctk.CTkFrame(parent)
        frame_conv.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
       
        ctk.CTkLabel(frame_conv, text="CONVERSOR UNIVERSAL", font=("Roboto Medium", 20)).pack(pady=20)
       
        self.combo_tipo_conv = ctk.CTkComboBox(frame_conv, values=["Longitud", "Presión", "Densidad"], command=self._update_units_conv)
        self.combo_tipo_conv.pack(fill="x", padx=20, pady=10)
       
        ctk.CTkEntry(frame_conv, textvariable=self.conv_valor, placeholder_text="Valor").pack(fill="x", padx=20, pady=10)
       
        self.combo_u1 = ctk.CTkComboBox(frame_conv, values=[])
        self.combo_u1.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_conv, text="⬇ a ⬇").pack()
        self.combo_u2 = ctk.CTkComboBox(frame_conv, values=[])
        self.combo_u2.pack(fill="x", padx=20, pady=5)
       
        ctk.CTkButton(frame_conv, text="Convertir", command=self._convertir, fg_color="#546E7A").pack(pady=20)
       
        ctk.CTkLabel(frame_conv, textvariable=self.conv_res, font=("Roboto", 24, "bold"), text_color="#2CC985").pack()
        self._update_units_conv("Longitud")


    def _crear_input(self, parent, text, var):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text=text).pack(side="left")
        ctk.CTkEntry(f, textvariable=var, width=100, justify="right").pack(side="right")


    def _crear_tarjeta_resultado(self, parent, titulo, var):
        card = ctk.CTkFrame(parent, corner_radius=15, border_width=2, border_color="#3B8ED0")
        card.pack(fill="x", pady=10)
        ctk.CTkLabel(card, text=titulo, font=("Roboto", 12), text_color="gray").pack(pady=(15, 0))
        ctk.CTkLabel(card, textvariable=var, font=("Roboto", 26, "bold"), text_color="#3B8ED0").pack(pady=(0, 15))


    def _update_geo_inputs(self, choice):
        for w in self.geo_frame.winfo_children(): w.destroy()
        self._crear_input(self.geo_frame, "Altura (h) [m]:", self.c_altura)
        if choice == "Rectangular":
            self._crear_input(self.geo_frame, "Largo (L) [m]:", self.c_largo)
            self._crear_input(self.geo_frame, "Ancho (b) [m]:", self.c_ancho)
        else:
            self._crear_input(self.geo_frame, "Radio (r) [m]:", self.c_radio)


    def _set_fluido_calc(self, choice):
        self.c_densidad.set(FLUIDOS[choice]["densidad"])


    def _calcular_calc(self):
        try:
            rho, g, h = self.c_densidad.get(), self.c_gravedad.get(), self.c_altura.get()
            p = rho * g * h
            if self.c_combo_geo.get() == "Rectangular": area = self.c_largo.get() * self.c_ancho.get()
            else: area = math.pi * (self.c_radio.get()**2)
           
            self.res_vars["P"].set(f"{p:,.2f} Pa")
            self.res_vars["F"].set(f"{p*area:,.2f} N")
            self.res_vars["V"].set(f"{area*h:,.2f} m³")
        except: pass


    def _update_units_conv(self, choice):
        if choice == "Presión": d = CONV_PRESION
        elif choice == "Densidad": d = CONV_DENSIDAD
        else: d = CONV_LONGITUD
       
        units = list(d.keys())
        self.combo_u1.configure(values=units)
        self.combo_u2.configure(values=units)
        self.combo_u1.set(units[0])
        self.combo_u2.set(units[1] if len(units)>1 else units[0])


    def _convertir(self):
        try:
            v, u1, u2 = self.conv_valor.get(), self.combo_u1.get(), self.combo_u2.get()
            tipo = self.combo_tipo_conv.get()
           
            if tipo == "Presión": d = CONV_PRESION
            elif tipo == "Densidad": d = CONV_DENSIDAD
            else: d = CONV_LONGITUD
           
            res = (v * d[u1]) / d[u2]
           
            self.conv_res.set(f"{res:.4f}")
        except:
            self.conv_res.set("Error")


    # =========================================================================
    #  MÓDULO 2: SIMULADOR 3D (AVANZADO)
    # =========================================================================
    def _init_simulador(self, parent):
        # Variables Lógica
        self.s_densidad = tk.DoubleVar(value=1000.0)
        self.s_h_max = tk.DoubleVar(value=2.0)
        self.s_gravedad = tk.DoubleVar(value=9.81)
        self.s_ang_izq = tk.DoubleVar(value=90.0)
        self.s_ang_der = tk.DoubleVar(value=90.0)
        self.s_ancho = tk.DoubleVar(value=1.5)
        self.s_largo = tk.DoubleVar(value=2.0)
        self.s_radio = tk.DoubleVar(value=1.0)
       
        self.zoom_level = tk.DoubleVar(value=1.0)
        self.nivel_agua = 0.0
        self.animando = False
        self.color_fluido = FLUIDOS["Agua"]["color"]
        self.color_borde_fluido = FLUIDOS["Agua"]["borde"]
       
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.mouse_on_canvas = False
        self.offset_x = 0
        self.offset_y = 0


        # Telemetría
        self.live_vars = {
            "nivel": tk.StringVar(value="0.00 m"),
            "volumen": tk.StringVar(value="0.00 L"),
            "presion": tk.StringVar(value="0 Pa"),
            "fuerza": tk.StringVar(value="0 N"),
            "f_izq": tk.StringVar(value="0 N"),
            "f_der": tk.StringVar(value="0 N")
        }


        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)


        # 1. Panel Izquierdo (Controles)
        sidebar = ctk.CTkFrame(parent, width=350, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
       
        ctk.CTkLabel(sidebar, text="CONFIGURACIÓN SIMULADOR", font=("Roboto", 16, "bold")).pack(pady=20)
       
        # Fluido
        ctk.CTkLabel(sidebar, text="Fluido:").pack(anchor="w", padx=20)
        self.combo_sim = ctk.CTkComboBox(sidebar, values=list(FLUIDOS.keys()), command=self._actualizar_fluido_sim)
        self.combo_sim.pack(fill="x", padx=20, pady=(0,10))
        self.combo_sim.set("Agua")


        # Geometría
        ctk.CTkLabel(sidebar, text="Geometría Base:").pack(anchor="w", padx=20)
        self.combo_shape_sim = ctk.CTkComboBox(sidebar, values=["Rectangular", "Cilíndrica"], command=self._update_sim_sliders)
        self.combo_shape_sim.pack(fill="x", padx=20, pady=(0,10))
        self.combo_shape_sim.set("Rectangular")


        # Container Sliders Dinámicos
        self.frame_sliders_sim = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.frame_sliders_sim.pack(fill="both", expand=True, padx=5, pady=10)


        self.btn_animar = ctk.CTkButton(sidebar, text="LLENAR / PAUSAR", command=self._toggle_anim, fg_color="#2CC985", hover_color="#229A65")
        self.btn_animar.pack(fill="x", padx=20, pady=5)
       
        ctk.CTkButton(sidebar, text="VACIAR TANQUE", command=self._reset_sim, fg_color="#D32F2F", hover_color="#B71C1C").pack(fill="x", padx=20, pady=(5,20))


        center_frame = ctk.CTkFrame(parent, fg_color="transparent")
        center_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
       
        canvas_container = ctk.CTkFrame(center_frame, corner_radius=10, border_width=2, border_color="#3B8ED0")
        canvas_container.pack(fill="both", expand=True)
       
        self.canvas = tk.Canvas(canvas_container, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=2, pady=2)
       
        # Bindings
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Leave>', self._on_mouse_leave)
        self.canvas.bind('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind('<Button-4>', self._on_mousewheel)
        self.canvas.bind('<Button-5>', self._on_mousewheel)
        self.canvas.bind('<ButtonPress-3>', self._start_pan)
        self.canvas.bind('<B3-Motion>', self._do_pan)


        # Barra Zoom
        zoom_frame = ctk.CTkFrame(center_frame, height=40, fg_color="transparent")
        zoom_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(zoom_frame, text="ZOOM").pack(side="left", padx=10)
        ctk.CTkSlider(zoom_frame, from_=0.5, to=5.0, variable=self.zoom_level, command=lambda v: self._dibujar()).pack(side="left", fill="x", expand=True)


        # 3. Panel Derecho (Datos)
        right_panel = ctk.CTkFrame(parent, width=280, corner_radius=0)
        right_panel.grid(row=0, column=2, sticky="nsew")
       
        self._add_header(right_panel, "TELEMETRÍA")
       
        self._add_data_row(right_panel, "Nivel Agua", self.live_vars["nivel"])
        self._add_data_row(right_panel, "Volumen", self.live_vars["volumen"], "#3B8ED0")
       
        ctk.CTkFrame(right_panel, height=2, fg_color="gray").pack(fill="x", padx=20, pady=15)
       
        self._add_data_row(right_panel, "Presión Fondo", self.live_vars["presion"], "#E53935")
        self._add_data_row(right_panel, "Fuerza Fondo", self.live_vars["fuerza"], "#E53935")
       
        ctk.CTkFrame(right_panel, height=2, fg_color="gray").pack(fill="x", padx=20, pady=15)
       
        self._add_data_row(right_panel, "F. Pared Izq", self.live_vars["f_izq"], "#43A047")
        self._add_data_row(right_panel, "F. Pared Der", self.live_vars["f_der"], "#43A047")


        # Inicialización final
        self._update_sim_sliders("Rectangular")
        self.after(100, self._dibujar)


    def _add_header(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=("Roboto", 16, "bold"), text_color="#3B8ED0").pack(pady=20)


    def _add_data_row(self, parent, label, var, color="text_color"):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f, text=label).pack(side="left")
       
        text_col = ["black", "white"] if color == "text_color" else color
        ctk.CTkLabel(f, textvariable=var, font=("Roboto", 16, "bold"), text_color=text_col).pack(side="right")


    def _update_sim_sliders(self, choice=None):
        # Limpiar
        for widget in self.frame_sliders_sim.winfo_children(): widget.destroy()
       
        forma = self.combo_shape_sim.get()
       
        self._add_slider_group("Dimensiones")
        self._create_slider_sim("Altura Total (m)", self.s_h_max, 0.1, 10.0)
       
        if forma == "Rectangular":
            self._create_slider_sim("Ancho Base (X) [m]", self.s_ancho, 0.1, 5.0)
            self._create_slider_sim("Profundidad (Z) [m]", self.s_largo, 0.1, 10.0)
        else:
            self._create_slider_sim("Radio Base (r) [m]", self.s_radio, 0.1, 3.0)
           
        self._add_slider_group("Paredes")
        self._create_slider_sim("Ángulo Izq (°)", self.s_ang_izq, 45, 135)
        self._create_slider_sim("Ángulo Der (°)", self.s_ang_der, 45, 135)
       
        self._add_slider_group("Física")
        self._create_slider_sim("Gravedad (m/s²)", self.s_gravedad, 1, 25)
        self._create_slider_sim("Densidad (kg/m³)", self.s_densidad, 500, 14000)
       
        self._dibujar()


    def _add_slider_group(self, title):
        ctk.CTkLabel(self.frame_sliders_sim, text=title, font=("Roboto", 12, "bold"), text_color="gray").pack(anchor="w", pady=(15,5))


    def _create_slider_sim(self, label, variable, vmin, vmax):
        f = ctk.CTkFrame(self.frame_sliders_sim, fg_color="transparent")
        f.pack(fill="x", pady=2)
       
        f_head = ctk.CTkFrame(f, fg_color="transparent")
        f_head.pack(fill="x")
        ctk.CTkLabel(f_head, text=label, font=("Roboto", 11)).pack(side="left")
       
        entry_var = tk.StringVar(value=f"{variable.get():.3f}")
        entry = ctk.CTkEntry(f_head, textvariable=entry_var, width=70, height=25, justify="center")
        entry.pack(side="right")
       
        def update_from_entry(event=None):
            try:
                val = float(entry_var.get())
                variable.set(val)
                self._dibujar()
            except: pass
           
        entry.bind("<Return>", update_from_entry)
        entry.bind("<FocusOut>", update_from_entry)
       
        def update_from_slider(val):
            entry_var.set(f"{val:.3f}")
            self._dibujar()


        ctk.CTkSlider(f, from_=vmin, to=vmax, variable=variable, command=update_from_slider).pack(fill="x", pady=5)


    def _actualizar_fluido_sim(self, choice):
        d = FLUIDOS[choice]
        self.s_densidad.set(d["densidad"])
        self.color_fluido = d["color"]
        self.color_borde_fluido = d["borde"]
        self._update_sim_sliders()


    # --- LÓGICA DE DIBUJO ---
    def _dibujar(self):
        self.canvas.delete("all")
        w_c = self.canvas.winfo_width()
        h_c = self.canvas.winfo_height()
        if w_c < 50: return


        # Datos
        h_max = self.s_h_max.get()
        ang_izq = self.s_ang_izq.get()
        ang_der = self.s_ang_der.get()
        rho = self.s_densidad.get()
        g = self.s_gravedad.get()
        forma = self.combo_shape_sim.get()


        if forma == "Rectangular":
            base_visual = self.s_ancho.get()
            profundidad_z = self.s_largo.get()
        else:
            base_visual = self.s_radio.get() * 2
            profundidad_z = 0


        # Física
        presion_fondo = rho * g * self.nivel_agua
       
        dx_izq = abs(self.nivel_agua / math.tan(math.radians(ang_izq)) if ang_izq != 90 else 0)
        dx_der = abs(self.nivel_agua / math.tan(math.radians(ang_der)) if ang_der != 90 else 0)
       
        # Cálculos de Volumen y Fuerza
        if forma == "Rectangular":
            area_base = base_visual * profundidad_z
            fuerza_fondo = presion_fondo * area_base
            w_top_calc = base_visual + dx_izq + dx_der
            area_trapecio = ((base_visual + w_top_calc) / 2) * self.nivel_agua
            volumen_total = area_trapecio * profundidad_z
        else:
            r_base = self.s_radio.get()
            area_base = math.pi * (r_base**2)
            fuerza_fondo = presion_fondo * area_base
            ang_prom = (ang_izq + ang_der) / 2
            dr = abs(self.nivel_agua / math.tan(math.radians(ang_prom)) if ang_prom != 90 else 0)
            r_top = r_base + dr
            volumen_total = (math.pi * self.nivel_agua / 3) * (r_base**2 + r_top**2 + r_base*r_top)


        def calc_f_lat(ang):
            if ang<=0 or self.nivel_agua<=0: return 0
            L_mojada = self.nivel_agua / math.sin(math.radians(ang))
            p_z = profundidad_z if forma == "Rectangular" else 1.0
            return (0.5 * rho * g * self.nivel_agua) * (L_mojada * p_z)


        f_izq = calc_f_lat(ang_izq)
        f_der = calc_f_lat(ang_der)


        # Update Textos
        self.live_vars["nivel"].set(f"{self.nivel_agua:.3f} m")
        self.live_vars["presion"].set(f"{presion_fondo:,.0f} Pa")
        self.live_vars["fuerza"].set(f"{fuerza_fondo:,.0f} N")
        if volumen_total < 1.0: self.live_vars["volumen"].set(f"{volumen_total*1000:.1f} L")
        else: self.live_vars["volumen"].set(f"{volumen_total:.3f} m³")
        self.live_vars["f_izq"].set(f"{f_izq:,.0f} N")
        self.live_vars["f_der"].set(f"{f_der:,.0f} N")


        # Dibujo
        margen = 60
        off_izq = h_max / math.tan(math.radians(ang_izq)) if ang_izq!=90 else 0
        off_der = h_max / math.tan(math.radians(ang_der)) if ang_der!=90 else 0
        ancho_total_vis = base_visual + abs(off_izq) + abs(off_der)
       
        sx = (w_c - margen*2) / max(ancho_total_vis, 0.1)
        sy = (h_c - margen*2) / max(h_max, 0.1)
        base_px_m = min(sx, sy)
        self.px_m = base_px_m * self.zoom_level.get()


        cx = (w_c / 2) + self.offset_x
        y_base = (h_c - margen) + self.offset_y
       
        x_base_izq = cx - (base_visual * self.px_m / 2)
        x_base_der = cx + (base_visual * self.px_m / 2)
        x_top_izq = x_base_izq - (off_izq * self.px_m)
        x_top_der = x_base_der + (off_der * self.px_m)
        y_top = y_base - (h_max * self.px_m)


        # Agua
        if self.nivel_agua > 0:
            y_a = yb = y_base
            h_px = self.nivel_agua * self.px_m
            y_a = y_base - h_px
            ratio = self.nivel_agua / h_max
            x_ai = x_base_izq + (x_top_izq - x_base_izq) * ratio
            x_ad = x_base_der + (x_top_der - x_base_der) * ratio
           
            self.canvas.create_polygon(x_base_izq, y_base, x_base_der, y_base, x_ad, y_a, x_ai, y_a,
                                     fill=self.color_fluido, outline="")
            self.geo_agua = {'y_s': y_a, 'y_b': y_base, 'xi': x_ai, 'xd': x_ad, 'bi': x_base_izq, 'bd': x_base_der}
       
        # Paredes
        self.canvas.create_line(x_top_izq, y_top, x_base_izq, y_base, x_base_der, y_base, x_top_der, y_top, width=4, fill="#37474F", capstyle="round")
       
        # Cota
        txt = f"Ancho: {base_visual:.2f}m" if forma == "Rectangular" else f"Ø {base_visual:.2f}m"
        self.canvas.create_text(cx, y_base+20, text=txt, fill="#555", font=("Arial", 10, "bold"))


        if self.mouse_on_canvas: self._draw_tooltip(self.last_mouse_x, self.last_mouse_y)


    def _draw_tooltip(self, x, y):
        self.canvas.delete("tip")
        if self.nivel_agua <= 0 or not hasattr(self, 'geo_agua'): return
        ga = self.geo_agua
        if ga['y_s'] <= y <= ga['y_b']:
             if min(ga['xi'], ga['bi']) <= x <= max(ga['xd'], ga['bd']):
                 total_h_px = ga['y_b'] - ga['y_s']
                 if total_h_px > 0:
                     ratio = (y - ga['y_s']) / total_h_px
                     prof_real = ratio * self.nivel_agua
                     pres = self.s_densidad.get() * self.s_gravedad.get() * prof_real
                     
                     self.canvas.create_line(ga['xi'], y, ga['xd'], y, fill="white", dash=(2,2), tags="tip")
                     self.canvas.create_oval(x-3,y-3,x+3,y+3, fill="red", outline="white", tags="tip")
                     
                     txt = f"Prof: {prof_real:.2f} m\nP: {pres:,.0f} Pa"
                     self.canvas.create_rectangle(x+15, y-45, x+150, y, fill="#263238", outline="#00E5FF", tags="tip")
                     self.canvas.create_text(x+25, y-22, text=txt, fill="white", font=("Arial", 10), anchor="w", tags="tip")


    # --- Mouse Events ---
    def _on_mousewheel(self, event):
        d = 0.1 if (event.num == 4 or event.delta > 0) else -0.1
        self.zoom_level.set(max(0.5, min(5.0, self.zoom_level.get() + d)))
        self._dibujar()
    def _start_pan(self, event): self.pan_start_x = event.x; self.pan_start_y = event.y
    def _do_pan(self, event):
        self.offset_x += event.x - self.pan_start_x; self.offset_y += event.y - self.pan_start_y
        self.pan_start_x = event.x; self.pan_start_y = event.y; self._dibujar()
    def _on_mouse_move(self, event): self.mouse_on_canvas=True; self.last_mouse_x=event.x; self.last_mouse_y=event.y; self._dibujar()
    def _on_mouse_leave(self, event): self.mouse_on_canvas=False; self.canvas.delete("tip")


    # Animación
    def _toggle_anim(self):
        if not self.animando:
            self.animando = True
            if self.nivel_agua >= self.s_h_max.get(): self.nivel_agua = 0
            self._loop()
        else: self.animando = False


    def _loop(self):
        if not self.animando: return
        tgt = self.s_h_max.get()
        self.nivel_agua += tgt/150
        if self.nivel_agua > tgt: self.nivel_agua = tgt
        self._dibujar()
        if self.nivel_agua < tgt: self.after(20, self._loop)
        else: self.animando = False


    def _reset_sim(self): self.animando=False; self.nivel_agua=0; self._dibujar()


if __name__ == "__main__":
    app = AppHidrostatica()
    app.mainloop()

