import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from database import execute_query, obtener_id_asistente_por_nombre

class ControlSesiones:
    def __init__(self, root, main_system):
        self.root = root
        self.main_system = main_system
        self.ventana_detalle = None
        self.ventana_sesiones = None

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título mejorado
        title = ctk.CTkLabel(main_frame, text="Control de Sesiones", font=("Helvetica", 36, "bold"))
        title.pack(pady=(50, 40))

        # Panel de búsqueda mejorado
        search_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        search_frame.pack(fill="x", padx=20, pady=10)

        btn_style = {
            "width": 150,
            "height": 40,
            "corner_radius": 8,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white",
        }

        # Contenedor para todos los controles de búsqueda
        controls_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=40)

        # Búsqueda por nombre
        name_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        name_frame.pack(side="left", padx=(0, 40))
        ctk.CTkLabel(name_frame, text="Nombre:", font=("Helvetica", 12)).pack(side="left")
        self.search_name = ctk.CTkEntry(name_frame, width=200, height=32,
                                    placeholder_text="Ingrese nombre")
        self.search_name.pack(side="left", padx=(10, 10))
        ctk.CTkButton(name_frame, text="Buscar por Nombre",
                    command=self.search_by_name, **btn_style).pack(side="left")

        # Búsqueda por fechas
        date_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        date_frame.pack(side="left", padx=(0, 20))

        # Contenedor para fecha Desde
        from_container = ctk.CTkFrame(date_frame, fg_color="transparent")
        from_container.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(from_container, text="Desde:", font=("Helvetica", 12)).pack(side="left", padx=(0, 10))
        self.date_from = DateEntry(from_container, width=12, background='black',
                                foreground='white', borderwidth=2,
                                date_pattern='yyyy-mm-dd')
        self.date_from.pack(side="left")

        # Contenedor para fecha Hasta
        to_container = ctk.CTkFrame(date_frame, fg_color="transparent")
        to_container.pack(side="left")
        ctk.CTkLabel(to_container, text="Hasta:", font=("Helvetica", 12)).pack(side="left", padx=(0, 10))
        self.date_to = DateEntry(to_container, width=12, background='black',
                            foreground='white', borderwidth=2,
                            date_pattern='yyyy-mm-dd')
        self.date_to.pack(side="left", padx=(0, 10))

        ctk.CTkButton(date_frame, text="Buscar por Fecha",
                    command=self.search_by_date, **btn_style).pack(side="left")

        # Botón mostrar todos
        ctk.CTkButton(controls_frame, text="Mostrar Todos",
                    command=self.actualizar_lista, **btn_style).pack(side="left", padx=20)

        # Enhanced table style
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            rowheight=30,
            font=('Helvetica', 10)
        )
        style.configure("Treeview.Heading",
                font=('Helvetica', 10, 'bold'),
                padding=5)
        style.map(
            "Treeview",
            background=[("selected", "#D3D3D3")],
            foreground=[("selected", "#000000")],
        )

        # Tabla mejorada
        table_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", border_width=1)
        table_frame.pack(fill="both", expand=True, pady=(10, 20), padx=40)

        columns = ("ID", "Paciente", "Tratamiento", "Primera Sesión", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")

        # Configurar columnas con anchos apropiados
        column_widths = {
            "ID": 50,
            "Paciente": 200,
            "Tratamiento": 200,
            "Primera Sesión": 150,
            "Estado": 150
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=column_widths[col], anchor="w")

        # Add scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Pack table and scrollbars
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.registrar_sesion)
        
        close_btn_style = btn_style.copy()
        close_btn_style.update(
            {
                "fg_color": "#e74c3c",
                "hover_color": "#c0392b",
                "border_color": "#c0392b",
            }
        )

        # Botón para volver abajo de la tabla
        ctk.CTkButton(main_frame, text="Volver al Menú Principal",
                    command=self.volver_menu_principal, **close_btn_style).pack(pady=10)

        self.actualizar_lista()

    def search_by_name(self):
        search_term = self.search_name.get().lower()
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            paciente = str(values[1]).lower()
            if search_term in paciente:
                self.tree.reattach(item, "", 0)
            else:
                self.tree.detach(item)

    def search_by_date(self):
        date_from = self.date_from.get_date()
        date_to = self.date_to.get_date()

        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            fecha_sesion = datetime.strptime(values[3], '%Y-%m-%d').date()

            if date_from <= fecha_sesion <= date_to:
                self.tree.reattach(item, "", 0)
            else:
                self.tree.detach(item)

    def actualizar_lista(self):
        # Limpiar la tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT
                ta.id,
                p.nombre as nombre_paciente,
                t.nombre as nombre_tratamiento,
                t.es_promocion,
                ta.fecha_asignacion as primera_sesion,
                ta.sesiones_asignadas,
                ta.sesiones_restantes,
                CASE
                    WHEN t.es_promocion THEN (
                        SELECT COUNT(*)
                        FROM promocion_componentes pc
                        WHERE pc.tratamiento_asignado_id = ta.id
                        AND pc.sesiones_restantes > 0
                    )
                    ELSE ta.sesiones_restantes
                END as componentes_pendientes
            FROM tratamientos_asignados ta
            JOIN pacientes p ON ta.paciente_id = p.id
            JOIN tratamientos t ON ta.tratamiento_id = t.id
            ORDER BY primera_sesion DESC
        """
        results = execute_query(query, fetch=True)

        for row in results:
            es_promocion = row[3]

            if es_promocion:
                estado = "PROMOCION"
                color_tag = None  # No aplicar color a promociones
            else:
                if row[6] <= 0:
                    estado = "Completado"
                    color_tag = "completado"
                elif row[4] == 'Sin iniciar':
                    estado = "Sin iniciar"
                    color_tag = "sin_iniciar"
                else:
                    estado = "En progreso"
                    color_tag = "en_progreso"

            # Insertar datos en la tabla
            item_id = self.tree.insert("", "end", values=(
                row[0],      # ID (oculto)
                row[1],      # Paciente
                f"{'🎁 ' if es_promocion else ''}{row[2]}",  # Tratamiento (con emoji si es promoción)
                row[4],      # Primera sesión
                estado      # Estado
            ))

            # Aplicar colores según el estado solo a tratamientos individuales
            if not es_promocion:
                self.tree.tag_configure(color_tag, foreground={
                    'completado': 'green',
                    'sin_iniciar': 'red',
                    'en_progreso': 'blue'
                }[color_tag])
                self.tree.item(item_id, tags=(color_tag,))

    def search_pacientes(self, event):
        search_term = self.search_entry.get().lower()
        for item in self.tree.get_children():
            paciente = self.tree.item(item)['values'][1].lower()
            if search_term not in paciente:
                self.tree.detach(item)
            else:
                self.tree.reattach(item, "", 0)

    def registrar_sesion(self, event):
        try:
            item = self.tree.selection()[0]
            tratamiento_id = self.tree.item(item)['values'][0]  # ID oculto
            self.mostrar_detalle_sesiones(tratamiento_id)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el detalle: {str(e)}", parent=self.root)



    def cargar_sesiones(self, tree_sesiones, tratamiento_id, componente_id=None):
        # Limpiar la tabla
        for item in tree_sesiones.get_children():
            tree_sesiones.delete(item)

        if componente_id:
            query = """
                SELECT
                    sr.numero_sesion,
                    sr.fecha_sesion,
                    a.nombre as esteticista,
                    sr.monto_abonado,
                    sr.estado_pago,
                    sr.proxima_cita,
                    sr.estado_sesion,
                    sr.comision_sumada,
                    sr.realizada,
                    ta.sesiones_asignadas,
                    ta.sesiones_restantes
                FROM sesiones_realizadas sr
                LEFT JOIN asistentes a ON sr.asistente_id = a.id
                JOIN tratamientos_asignados ta ON sr.tratamiento_asignado_id = ta.id
                WHERE sr.tratamiento_asignado_id = ? AND sr.nombre_componente = ?
                ORDER BY sr.numero_sesion
            """
            params = (tratamiento_id, componente_id)
        else:
            query = """
                SELECT
                    sr.numero_sesion,
                    sr.fecha_sesion,
                    a.nombre as esteticista,
                    sr.monto_abonado,
                    sr.estado_pago,
                    sr.proxima_cita,
                    sr.estado_sesion,
                    sr.comision_sumada,
                    sr.realizada,
                    ta.sesiones_asignadas,
                    ta.sesiones_restantes
                FROM sesiones_realizadas sr
                LEFT JOIN asistentes a ON sr.asistente_id = a.id
                JOIN tratamientos_asignados ta ON sr.tratamiento_asignado_id = ta.id
                WHERE sr.tratamiento_asignado_id = ?
                ORDER BY sr.numero_sesion
            """
            params = (tratamiento_id,)

        sesiones = execute_query(query, params, fetch=True)

        # Obtener información del tratamiento
        query = """
            SELECT sesiones_asignadas, sesiones_restantes
            FROM tratamientos_asignados
            WHERE id = ?
        """
        info_tratamiento = execute_query(query, (tratamiento_id,), fetch=True)[0]

        if info_tratamiento:
            sesiones_totales = info_tratamiento[0]
            sesiones_restantes = info_tratamiento[1]
            estado = "COMPLETADO" if sesiones_restantes == 0 else f"Faltan {sesiones_restantes} sesiones"

            # Insertar información de progreso como primer elemento
            tree_sesiones.insert("", 0, values=(
                "PROGRESO",
                f"Total: {sesiones_totales}",
                f"Realizadas: {sesiones_totales - sesiones_restantes}",
                f"Restantes: {sesiones_restantes}",
                estado,
                "",
                "",
                ""
            ), tags=('info',))

            # Configurar estilo para la fila de información
            tree_sesiones.tag_configure('info', background='#f0f0f0', foreground='#000000')

        for sesion in sesiones:
            item_id = tree_sesiones.insert("", "end", values=(
                f"Sesión {sesion[0]}",
                sesion[1],
                sesion[2] or "No asignado",
                f"${sesion[3]:.2f}" if sesion[3] else "$0.00",
                sesion[4] or "Pendiente",
                sesion[5] or "No programada",
                sesion[6] or "Pendiente",
                "Sí" if sesion[8] else "No"  # Mostrar si la sesión fue realizada
            ))

            # Aplicar estilos
            if sesion[8] and sesion[4] == 'PAGADO':  # realizada y pagada
                tree_sesiones.tag_configure('completada', foreground='green')
                tree_sesiones.item(item_id, tags=('completada',))
            elif sesion[6] == 'Cancelada':
                tree_sesiones.tag_configure('cancelada', foreground='red')
                tree_sesiones.item(item_id, tags=('cancelada',))
            elif sesion[4] == 'Pendiente':
                tree_sesiones.tag_configure('pendiente', foreground='orange')
                tree_sesiones.item(item_id, tags=('pendiente',))

    def mostrar_detalle_sesiones(self, tratamiento_id):
        try:
            self.ventana_detalle = ctk.CTkToplevel(self.root)
            self.ventana_detalle.title("Detalle de Sesiones")
            self.ventana_detalle.geometry("1000x600")
        
            main_frame = ctk.CTkFrame(self.ventana_detalle, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Obtener información del tratamiento
            query = """
                SELECT
                    p.nombre,
                    t.nombre,
                    ta.costo_total,
                    ta.total_pagado,
                    ta.saldo_pendiente,
                    ta.sesiones_asignadas,
                    ta.sesiones_restantes,
                    t.es_promocion
                FROM tratamientos_asignados ta
                JOIN pacientes p ON ta.paciente_id = p.id
                JOIN tratamientos t ON ta.tratamiento_id = t.id
                WHERE ta.id = ?
            """
            info = execute_query(query, (tratamiento_id,), fetch=True)[0]

            if not info:
                raise Exception("No se encontró información del tratamiento")
                    
            es_promocion = info[7]

            # Panel de información principal
            info_frame = ctk.CTkFrame(main_frame, fg_color="#F0F0F0", border_width=1)
            info_frame.pack(fill="x", pady=10, padx=5)

            # Encabezado con nombre del paciente y tipo de tratamiento
            header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=20, pady=(15,5))

            ctk.CTkLabel(header_frame,
                        text=info[0],  # Nombre del paciente
                        font=("Helvetica", 20, "bold")).pack(side="left")

            tipo_label = ctk.CTkLabel(header_frame,
                        text=f"{'Promoción' if es_promocion else 'Tratamiento'}: {info[1]}",
                        font=("Helvetica", 14))
            tipo_label.pack(side="right")

            # Información financiera
            financial_frame = ctk.CTkFrame(info_frame, fg_color="#FFFFFF", border_width=1)
            financial_frame.pack(fill="x", padx=20, pady=(5,15))

            # Dividir la información financiera en tres columnas
            for i, (label, value) in enumerate([
                ("Monto Total", f"${info[2]:.2f}"),
                ("Total Pagado", f"${info[3]:.2f}"),
                ("Saldo Pendiente", f"${info[4]:.2f}")
            ]):
                column = ctk.CTkFrame(financial_frame, fg_color="transparent")
                column.pack(side="left", expand=True, padx=10, pady=10)

                ctk.CTkLabel(column, text=label,
                            font=("Helvetica", 12)).pack()
                ctk.CTkLabel(column, text=value,
                            font=("Helvetica", 16, "bold")).pack()
 
            if es_promocion:
                self.mostrar_componentes_promocion(main_frame, tratamiento_id)
            else:
                self.mostrar_lista_sesiones(main_frame, tratamiento_id, self.ventana_detalle)

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}", parent=self.root)
            if hasattr(self, 'ventana_detalle'):
                self.ventana_detalle.destroy()

    def mostrar_componentes_promocion(self, main_frame, tratamiento_id):
        try:
            query = """
                SELECT
                    pd.nombre_componente,
                    pd.cantidad_sesiones,
                    COALESCE(pc.sesiones_restantes, pd.cantidad_sesiones) as sesiones_restantes,
                    COUNT(sr.id) AS sesiones_realizadas,
                    pc.id as componente_id
                FROM promocion_detalles pd
                JOIN tratamientos_asignados ta ON pd.promocion_id = ta.tratamiento_id
                LEFT JOIN promocion_componentes pc ON ta.id = pc.tratamiento_asignado_id
                    AND pd.nombre_componente = pc.tratamiento_id
                LEFT JOIN sesiones_realizadas sr ON sr.tratamiento_asignado_id = ta.id
                    AND sr.nombre_componente = pd.nombre_componente
                WHERE ta.id = ?
                GROUP BY pd.nombre_componente
            """
            componentes = execute_query(query, (tratamiento_id,), fetch=True)

            componentes_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
            componentes_frame.pack(fill="both", expand=True, pady=10, padx=5)

            header = ctk.CTkFrame(componentes_frame, fg_color="#F0F0F0")
            header.pack(fill="x", pady=(0, 10))
            ctk.CTkLabel(header, text="Tratamientos Incluidos",
                        font=("Helvetica", 16, "bold")).pack(pady=10)

            # Frame para contener los componentes y el scrollbar
            scrollable_frame = ctk.CTkFrame(componentes_frame, fg_color="transparent")
            scrollable_frame.pack(fill="both", expand=True)

            # Canvas para el scrollbar
            canvas = ctk.CTkCanvas(scrollable_frame, bg="#FFFFFF")
            canvas.pack(side="left", fill="both", expand=True)

            scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side="right", fill="y")

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            # Frame dentro del canvas
            inner_frame = ctk.CTkFrame(canvas, fg_color="transparent")
            canvas.create_window((0, 0), window=inner_frame, anchor="nw")

            for comp in componentes:
                self.crear_componente_ui(inner_frame, comp, tratamiento_id)

        except Exception as e:
            raise Exception(f"Error al cargar componentes: {str(e)}")

    def crear_componente_ui(self, parent_frame, comp_data, tratamiento_id):
        nombre_componente = comp_data[0]
        sesiones_asignadas = comp_data[1]
        sesiones_realizadas = comp_data[3]
        componente_id = comp_data[4]
        
        comp_frame = ctk.CTkFrame(parent_frame, fg_color="#F8F8F8", border_width=1)
        comp_frame.pack(fill="x", pady=5)

        info_frame = ctk.CTkFrame(comp_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=20, pady=15, expand=True)

        ctk.CTkLabel(info_frame, text=nombre_componente,
                    font=("Helvetica", 14, "bold")).pack(anchor="w")

        progress_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(5, 0))

        ctk.CTkLabel(progress_frame,
                    text=f"{sesiones_realizadas}/{sesiones_asignadas} sesiones",
                    font=("Helvetica", 12)).pack(side="left")

        ctk.CTkButton(comp_frame,
                    text="Ver Detalle",
                    command=lambda: self.mostrar_sesiones_componente_promocion(
                        tratamiento_id, nombre_componente),
                    width=120,
                    height=32,
                    fg_color="#191919",
                    hover_color="#676767").pack(side="right", padx=20)
        

    def mostrar_sesiones_componente_promocion(self, tratamiento_id, nombre_componente):
        self.ventana_sesiones = ctk.CTkToplevel(self.root)
        self.ventana_sesiones.title(f"Sesiones de {nombre_componente}")
        self.ventana_sesiones.geometry("900x600")
        self.ventana_sesiones.wm_attributes("-topmost", True)  # Mostrar siempre delante

        main_frame = ctk.CTkFrame(self.ventana_sesiones, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Obtener información del componente
        query = """
            SELECT
                pd.cantidad_sesiones,
                pc.id as componente_id,
                p.nombre as nombre_paciente,
                t.nombre as nombre_promocion,
                pd.precio_componente,
                (
                    SELECT COUNT(*)
                    FROM sesiones_realizadas sr
                    WHERE sr.tratamiento_asignado_id = pc.tratamiento_asignado_id
                    AND sr.nombre_componente = pd.nombre_componente
                ) as sesiones_realizadas
            FROM promocion_componentes pc
            JOIN tratamientos_asignados ta ON pc.tratamiento_asignado_id = ta.id
            JOIN tratamientos t ON ta.tratamiento_id = t.id
            JOIN promocion_detalles pd ON pd.promocion_id = t.id
            JOIN pacientes p ON ta.paciente_id = p.id
            WHERE pc.tratamiento_asignado_id = ?
            AND pd.nombre_componente = ?
        """
        info_componente = execute_query(query, (tratamiento_id, nombre_componente), fetch=True)[0]

        if not info_componente:
            raise Exception("No se encontró información del componente")

        # Panel de información mejorado
        info_frame = ctk.CTkFrame(main_frame, fg_color="#F0F0F0", border_width=1)
        info_frame.pack(fill="x", pady=(0,20))

        # Header con nombre del paciente
        header_frame = ctk.CTkFrame(info_frame, fg_color="transparent", border_width=1)
        header_frame.pack(fill="x", padx=20, pady=(15,5))

        ctk.CTkLabel(header_frame,
                    text=info_componente[2],  # nombre_paciente
                    font=("Helvetica", 20, "bold")).pack(side="left")

        ctk.CTkLabel(header_frame,
                    text=nombre_componente,
                    font=("Helvetica", 14)).pack(side="right")

        # Stats grid
        stats_frame = ctk.CTkFrame(info_frame, fg_color="#FFFFFF")
        stats_frame.pack(fill="x", padx=20, pady=(5,15))

        # Crear grid de estadísticas
        stats = [
            ("Sesiones Realizadas", f"{info_componente[5]}/{info_componente[0]}"),
            ("Sesiones Restantes", str(info_componente[0]-info_componente[5])),
            ("Precio por Sesión", f"${info_componente[4]:.2f}")
        ]

        for i, (label, value) in enumerate(stats):
            stat_box = ctk.CTkFrame(stats_frame, fg_color="transparent")
            stat_box.pack(side="left", expand=True, padx=10, pady=10)

            ctk.CTkLabel(stat_box, text=label,
                        font=("Helvetica", 12)).pack()
            ctk.CTkLabel(stat_box, text=value,
                        font=("Helvetica", 16, "bold")).pack()

        # Botones de acción
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0,20))

        btn_style = {
            "width": 150,
            "height": 32,
            "corner_radius": 8,
            "fg_color": "#191919",
            "hover_color": "#676767",
            "font": ("Helvetica", 12)
        }


        ctk.CTkButton(btn_frame,
                    text="Nueva Sesión",
                    command=lambda: self.registrar_nueva_sesion_promocion(
                        tratamiento_id, tree_sesiones, self.ventana_sesiones,
                        info_componente[1], nombre_componente, precio_componente=info_componente[4]),
                    **btn_style).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame,
                    text="Modificar Sesión",
                    command=lambda: self.modificar_sesion_promocion(
                        tratamiento_id, tree_sesiones,
                        info_componente[1], nombre_componente, info_componente[4]),
                    **btn_style).pack(side="left", padx=5)

        # Tabla mejorada
        table_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", border_width=1)
        table_frame.pack(fill="both", expand=True, pady=(0,10))
        # Frame para la tabla y los scrollbars
        tree_container = ctk.CTkFrame(table_frame)
        tree_container.pack(fill="both", expand=True)

        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#ffffff",
            fieldbackground="#ffffff",
            rowheight=30,
            font=('Helvetica', 10)
        )
        style.configure(
            "Treeview.Heading",
            font=('Helvetica', 10, 'bold'),
            padding=5
        )

        tree_sesiones = ttk.Treeview(
            tree_container,
            columns=("Sesion", "Fecha", "Esteticista", "Estado", "Pago"),
            show="headings"
        )
        tree_sesiones.heading("Sesion", text="Sesión")
        tree_sesiones.heading("Fecha", text="Fecha")
        tree_sesiones.heading("Esteticista", text="Esteticista")
        tree_sesiones.heading("Estado", text="Estado")
        tree_sesiones.heading("Pago", text="Pago")

        # Scrollbars
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=tree_sesiones.yview)
        hsb = ttk.Scrollbar(tree_container, orient="horizontal", command=tree_sesiones.xview)
        tree_sesiones.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout de los elementos
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree_sesiones.pack(side="top", fill="both", expand=True)


        # Modificar la llamada a cargar_sesiones_promocion
        self.cargar_sesiones_promocion(tree_sesiones, tratamiento_id,
                                 info_componente[1], nombre_componente)

    def cargar_sesiones_promocion(self, tree_sesiones, tratamiento_id, componente_id, nombre_componente, external_conn=None):
        conn = external_conn
        should_close_conn = False

        try:
            if conn is None:
                conn = sqlite3.connect('spa_database.db', timeout=10)
                should_close_conn = True
                
            c = conn.cursor()
            for item in tree_sesiones.get_children():
                tree_sesiones.delete(item)
            c.execute("""
                SELECT sr.numero_sesion, sr.fecha_sesion, a.nombre, sr.estado_pago, sr.realizada
                FROM sesiones_realizadas sr
                JOIN asistentes a ON sr.asistente_id = a.id
                WHERE sr.tratamiento_asignado_id = ? AND sr.nombre_componente = ?
                ORDER BY sr.numero_sesion
            """, (tratamiento_id, nombre_componente))
            sesiones = c.fetchall()

            for sesion in sesiones:
                tree_sesiones.insert("", "end", values=(
                    f"Sesión {sesion[0]}",
                    sesion[1],
                    sesion[2],
                    "PAGADO" if sesion[3] else "Pendiente",
                    "Realizada" if sesion[4] else "Pendiente",
                    sesion[4]
                ))

            # Verificar si todas las sesiones están realizadas Y pagadas
            c.execute("""
                SELECT COUNT(*) as total_sesiones,
                    SUM(CASE WHEN realizada = 1 AND estado_pago = 'PAGADO' THEN 1 ELSE 0 END) as sesiones_completas
                FROM sesiones_realizadas
                WHERE tratamiento_asignado_id = ? AND nombre_componente = ?
            """, (tratamiento_id, nombre_componente))
            total_sesiones, sesiones_completas = c.fetchone()

            if total_sesiones == sesiones_completas:
                c.execute("""
                    UPDATE promocion_componentes
                    SET sesiones_restantes = 0
                    WHERE tratamiento_asignado_id = ? AND tratamiento_id = ?
                """, (tratamiento_id, componente_id))

            if should_close_conn:
                conn.commit()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error en la base de datos: {str(e)}", parent=self.root)
        finally:
            if should_close_conn and conn:
                conn.close()

    def get_db_connection(self):
        try:
            conn = sqlite3.connect('spa_database.db')
            return conn
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error al conectar con la base de datos: {str(e)}", parent=self.root)
            return None

    def modificar_sesion_promocion(self, tratamiento_id, tree_sesiones, componente_id, nombre_componente, precio_componente ):
        try:
            selected_item = tree_sesiones.selection()[0]
            sesion_data = tree_sesiones.item(selected_item)['values']

            window = ctk.CTkToplevel(self.root)
            window.title(f"Modificar Sesión - {nombre_componente}")
            window.geometry("400x600")
            window.wm_attributes("-topmost", True)

            frame = ctk.CTkFrame(window, fg_color="#FFFFFF")
            frame.pack(padx=20, pady=20, fill="both", expand=True)

            conn = None
            try:
                conn = self.get_db_connection()
                if not conn:
                    return
                c = conn.cursor()
                
                c.execute("SELECT id, nombre FROM asistentes ORDER BY nombre")
                esteticistas = c.fetchall()

                c.execute("""
                    SELECT
                        sr.asistente_id,
                        sr.porcentaje_asistente,
                        sr.estado_pago,
                        sr.fecha_sesion,
                        sr.realizada,
                        sr.monto_abonado
                    FROM sesiones_realizadas sr
                    WHERE sr.tratamiento_asignado_id = ? AND sr.numero_sesion = ?
                """, (tratamiento_id, int(sesion_data[0].split()[1])))
                detalles_sesion = c.fetchone()
                conn.close()


                if not detalles_sesion:
                    raise Exception("No se encontraron los detalles de la sesión")

                # Información de la sesión
                ctk.CTkLabel(frame, text=f"Modificar {sesion_data[0]}", font=("Helvetica", 20, "bold")).pack(pady=10)
                # Fecha
                ctk.CTkLabel(frame, text="Fecha de la sesión:").pack(pady=5)
                fecha_sesion = DateEntry(frame, width=12, background='black', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
                fecha_sesion.pack(pady=5)
                fecha_sesion.set_date(datetime.strptime(detalles_sesion[3], '%Y-%m-%d').date())

                # Esteticista
                ctk.CTkLabel(frame, text="Esteticista:").pack(pady=5)
                esteticista_var = ctk.StringVar()
                esteticista_combo = ctk.CTkComboBox(frame, values=[e[1] for e in esteticistas], variable=esteticista_var)
                esteticista_combo.pack(pady=5)
                esteticista_actual = next(e[1] for e in esteticistas if e[0] == detalles_sesion[0])
                esteticista_var.set(esteticista_actual)

                # Porcentaje del asistente
                ctk.CTkLabel(frame, text="Porcentaje para el asistente:").pack(pady=5)
                porcentaje_entry = ctk.CTkEntry(frame)
                porcentaje_entry.pack(pady=5)
                porcentaje_entry.insert(0, str(detalles_sesion[1]))

                # Estado de pago
                ctk.CTkLabel(frame, text="Estado de pago:").pack(pady=5)
                estado_pago_var = ctk.StringVar(value=detalles_sesion[2])
                estado_pago_combo = ctk.CTkComboBox(frame, values=["PAGADO", "Pendiente"], variable=estado_pago_var)
                estado_pago_combo.pack(pady=5)

                # Checkbox para marcar si la sesión fue realizada
                realizada_var = ctk.BooleanVar(value=detalles_sesion[4])
                realizada_check = ctk.CTkCheckBox(frame, text="Sesión realizada", variable=realizada_var)
                realizada_check.pack(pady=5)

                # Monto 
                ctk.CTkLabel(frame, text="Monto de la sesión:").pack(pady=5)
                monto_label = ctk.CTkLabel(frame, text=f"${precio_componente:.2f}", font=("Arial",22, "bold"))
                monto_label.pack(pady=5)  
            
            except Exception as e:
                messagebox.showerror("Error", f"Error en la base de datos: {str(e)}", parent=self.root)
            finally:
                if conn:
                    conn.close()

                def guardar_cambios():
                    conn = None
                    try:
                        conn = self.get_db_connection()
                        if not conn:
                            return

                        c = conn.cursor()

                        # Obtener ID del esteticista
                        esteticista_nombre = esteticista_var.get()
                        asistente_id = next(e[0] for e in esteticistas if e[1] == esteticista_nombre)

                        # Validar porcentaje
                        porcentaje = float(porcentaje_entry.get())
                        if porcentaje < 0 or porcentaje > 100:
                            raise ValueError("El porcentaje debe estar entre 0 y 100")

                        # Realizar la actualización
                        query = """
                            UPDATE sesiones_realizadas
                            SET fecha_sesion = ?,
                                asistente_id = ?,
                                estado_pago = ?,
                                porcentaje_asistente = ?,
                                monto_abonado = ?,
                                proxima_cita = ?,
                                realizada = ?,
                                estado_sesion = ?
                            WHERE tratamiento_asignado_id = ?
                            AND nombre_componente = ?
                            AND numero_sesion = ?
                        """
                        params = (
                            fecha_sesion.get_date().strftime('%Y-%m-%d'),
                            asistente_id,
                            estado_pago_var.get(),
                            porcentaje,
                            precio_componente,
                            (datetime.strptime(fecha_sesion.get_date().strftime('%Y-%m-%d'), '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'),
                            1 if realizada_var.get() else 0,
                            'Realizada' if realizada_var.get() else 'Pendiente',
                            tratamiento_id,
                            nombre_componente,
                            int(sesion_data[0].split()[1])
                        )
                        
                        c.execute(query, params)
                        conn.commit()

                        # Verificar si todas las sesiones están realizadas Y pagadas
                        c.execute("""
                            SELECT COUNT(*) as total_sesiones,
                                SUM(CASE WHEN realizada = 1 AND estado_pago = 'PAGADO' THEN 1 ELSE 0 END) as sesiones_completas
                            FROM sesiones_realizadas
                            WHERE tratamiento_asignado_id = ? AND nombre_componente = ?
                        """, (tratamiento_id, nombre_componente))
                        
                        total_sesiones, sesiones_completas = c.fetchone()

                        if total_sesiones == sesiones_completas:
                            c.execute("""
                                UPDATE promocion_componentes
                                SET sesiones_restantes = 0
                                WHERE tratamiento_asignado_id = ? AND tratamiento_id = ?
                            """, (tratamiento_id, componente_id))
                            conn.commit()

                        self.cargar_sesiones_promocion(tree_sesiones, tratamiento_id, componente_id, nombre_componente)
                        window.destroy()
                        self.ventana_detalle.withdraw()
                        self.ventana_sesiones.withdraw()
                        messagebox.showinfo("Éxito", "Sesión modificada correctamente", parent=self.root)

                    except Exception as e:
                        if conn:
                            conn.rollback()
                        messagebox.showerror("Error", f"Error al modificar la sesión: {str(e)}", parent=self.root)
                    finally:
                        if conn:
                            conn.close()

                btn_style = {
                    "corner_radius": 10,
                    "fg_color": "#000000",
                    "hover_color": "#676767",
                    "border_width": 2,
                    "text_color": "white"
                }

                ctk.CTkButton(frame, text="Guardar cambios", command=guardar_cambios, **btn_style).pack(pady=10)
                ctk.CTkButton(frame, text="Cancelar", command=window.destroy, **btn_style).pack(pady=5)

        except IndexError:
            self.ventana_detalle.withdraw()
            messagebox.showwarning("Advertencia", "Por favor seleccione una sesión para modificar", parent=self.root)
        except Exception as e:
            self.ventana_detalle.withdraw()
            messagebox.showerror("Error", f"Error al preparar la modificación: {str(e)}", parent=self.root)

    def registrar_nueva_sesion_promocion(self, tratamiento_id, tree_sesiones, ventana_parent, componente_id, nombre_componente, precio_componente):
        try:
            query = """
                SELECT
                    pd.nombre_componente,
                    pd.cantidad_sesiones,
                    COALESCE(pc.sesiones_restantes, pd.cantidad_sesiones) as sesiones_restantes,
                    COUNT(sr.id) AS sesiones_realizadas,
                    pc.id as componente_id
                FROM promocion_detalles pd
                JOIN tratamientos_asignados ta ON pd.promocion_id = ta.tratamiento_id
                LEFT JOIN promocion_componentes pc ON ta.id = pc.tratamiento_asignado_id
                    AND pd.nombre_componente = pc.tratamiento_id
                LEFT JOIN sesiones_realizadas sr ON sr.tratamiento_asignado_id = ta.id
                    AND sr.nombre_componente = pd.nombre_componente
                WHERE ta.id = ? AND pd.nombre_componente = ?
                GROUP BY pd.nombre_componente
            """
            componente_info = execute_query(query, (tratamiento_id, nombre_componente), fetch=True)[0]

            if not componente_info:
                raise Exception("No se encontró información del componente")

            nombre_componente = componente_info[0]
            sesiones_asignadas = componente_info[1]
            sesiones_restantes = componente_info[2]
            sesiones_realizadas = componente_info[3]
            componente_id = componente_info[4]

            window = ctk.CTkToplevel(self.root)
            window.title(f"Registrar Nueva Sesión - {nombre_componente}")
            window.geometry("400x600")
            window.wm_attributes("-topmost", True)
            window.transient(ventana_parent)

            frame = ctk.CTkFrame(window, fg_color="#FFFFFF")
            frame.pack(padx=20, pady=20, fill="both", expand=True)
            title = ctk.CTkLabel(frame, text=f"Registrar Nueva Sesión - {nombre_componente}", font=("Helvetica", 20, "bold"))
            title.pack(pady=10)
            # Obtener lista de esteticistas
            query = "SELECT id, nombre FROM asistentes ORDER BY nombre"
            esteticistas = execute_query(query, fetch=True)

            # Selector de esteticista
            ctk.CTkLabel(frame, text="Esteticista:").pack(pady=5)
            esteticista_var = ctk.StringVar()
            esteticista_combo = ctk.CTkComboBox(frame,
                                                values=[e[1] for e in esteticistas],
                                                variable=esteticista_var)
            esteticista_combo.pack(pady=5)

            # Porcentaje del asistente
            ctk.CTkLabel(frame, text="Porcentaje para el asistente:").pack(pady=5)
            porcentaje_entry = ctk.CTkEntry(frame)
            porcentaje_entry.pack(pady=5)

            # Fecha de la sesión
            ctk.CTkLabel(frame, text="Fecha de la sesión:").pack(pady=5)
            fecha_sesion = DateEntry(frame, width=12, background='black',
                                     foreground='white', borderwidth=2,
                                     date_pattern='yyyy-mm-dd')
            fecha_sesion.pack(pady=5)

            # Estado de pago
            ctk.CTkLabel(frame, text="Estado de pago:").pack(pady=5)
            estado_pago_var = ctk.StringVar(value="Pendiente")
            estado_pago_combo = ctk.CTkComboBox(frame,
                                                values=["PAGADO", "Pendiente"],
                                                variable=estado_pago_var)
            estado_pago_combo.pack(pady=5)

            # Checkbox para marcar si la sesión fue realizada
            realizada_var = ctk.BooleanVar()
            realizada_check = ctk.CTkCheckBox(frame, text="Sesión realizada", variable=realizada_var)
            realizada_check.pack(pady=5)

            # Monto abonado
            ctk.CTkLabel(frame, text="Monto de la sesión:").pack(pady=5)
            monto_label = ctk.CTkLabel(frame, text=f"${precio_componente:.2f}", font=("Helvetica", 22, "bold"))
            monto_label.pack(pady=5) 

            def guardar_sesion():
                try:
                    if sesiones_restantes <= 0:
                        raise ValueError("No quedan sesiones disponibles para este componente")

                    # Validaciones básicas
                    if not esteticista_var.get():
                        raise ValueError("Debe seleccionar un esteticista")

                    porcentaje = float(porcentaje_entry.get())

                    # Obtener ID del esteticista
                    esteticista_nombre = esteticista_var.get()
                    asistente_id = next(e[0] for e in esteticistas if e[1] == esteticista_nombre)

                    fecha = fecha_sesion.get_date().strftime('%Y-%m-%d')

                    query = """
                        INSERT INTO sesiones_realizadas (
                            tratamiento_asignado_id,
                            nombre_componente,
                            asistente_id,
                            fecha_sesion,
                            numero_sesion,
                            monto_abonado,
                            estado_pago,
                            estado_sesion,
                            porcentaje_asistente,
                            proxima_cita,
                            realizada
                        ) VALUES (?, ?, ?, ?, (
                            SELECT COALESCE(MAX(numero_sesion), 0) + 1
                            FROM sesiones_realizadas
                            WHERE tratamiento_asignado_id = ? AND nombre_componente = ?
                        ), ?, ?, ?, ?, ?, ?)
                    """
                    params = (
                        tratamiento_id,
                        nombre_componente,
                        asistente_id,
                        fecha,
                        tratamiento_id,
                        nombre_componente,
                        precio_componente,
                        estado_pago_var.get(),
                        'Realizada' if realizada_var.get() else 'Pendiente',
                        porcentaje,
                        (datetime.strptime(fecha, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'),
                        realizada_var.get()
                    )
                    execute_query(query, params)
                    self.cargar_sesiones_promocion(tree_sesiones, tratamiento_id, componente_id, nombre_componente)
                    window.destroy()
                    self.ventana_sesiones.withdraw()
                    self.ventana_detalle.withdraw()
                    messagebox.showinfo("Éxito", "Sesión registrada correctamente", parent=self.root)

                except Exception as e:
                    messagebox.showerror("Error", f"Error al guardar la sesión: {str(e)}", parent=self.root)

            btn_style = {"corner_radius": 10, "fg_color": "#000000", "hover_color": "#676767",
                         "border_width": 2, "text_color": "white"}

            ctk.CTkButton(frame, text="Guardar", command=guardar_sesion, **btn_style).pack(pady=10)
            ctk.CTkButton(frame, text="Cancelar", command=window.destroy, **btn_style).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Error", f"Error al preparar el formulario: {str(e)}", parent=self.root)

    def mostrar_lista_sesiones(self, parent_frame, tratamiento_id, ventana_parent, componente_id=None):
        # Frame para la lista de sesiones
        sesiones_frame = ctk.CTkFrame(parent_frame)
        sesiones_frame.pack(fill="both", expand=True, pady=10)

        # Crear Treeview para las sesiones
        columns = ("Sesión #", "Fecha", "Esteticista", "Monto Abonado",
                  "Estado de Pago", "Próxima Cita", "Estado")
        tree_sesiones = ttk.Treeview(sesiones_frame, columns=columns,
                                   show="headings", height=5)

        # Configurar columnas
        for col in columns:
            tree_sesiones.heading(col, text=col)
            tree_sesiones.column(col, width=100)

        # Agregar scrollbars
        vsb = ttk.Scrollbar(sesiones_frame, orient="vertical",
                           command=tree_sesiones.yview)
        hsb = ttk.Scrollbar(sesiones_frame, orient="horizontal",
                           command=tree_sesiones.xview)
        tree_sesiones.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree_sesiones.pack(side="left", fill="both", expand=True)

        # Frame para botones
        btn_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)

        btn_style = {
            "corner_radius": 10,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white"
        }

        # Botones de acción
        ctk.CTkButton(btn_frame,
                     text="Agregar Sesión",
                     command=lambda: self.registrar_nueva_sesion(
                         tratamiento_id, tree_sesiones,
                         ventana_parent, componente_id),
                     **btn_style).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame,
                     text="Modificar Sesión",
                     command=lambda: self.modificar_sesion_seleccionada(
                         tratamiento_id, tree_sesiones, componente_id),
                     **btn_style).pack(side="left", padx=5)

        # Cargar las sesiones
        self.cargar_sesiones(tree_sesiones, tratamiento_id, componente_id)
        ventana_parent.lift()  # Mantener ventana detalle al frente

    def modificar_sesion_seleccionada(self, tratamiento_id, tree_sesiones, componente_id=None):
        try:
            selected_item = tree_sesiones.selection()[0]
            sesion_data = tree_sesiones.item(selected_item)['values']
            self.ventana_modificar_sesion(tratamiento_id, sesion_data,
                                        tree_sesiones, componente_id)
        except IndexError:
            self.ventana_detalle.withdraw()
            messagebox.showwarning("Advertencia",
                                 "Por favor seleccione una sesión para modificar", parent=self.root)

    def ventana_modificar_sesion(self, tratamiento_id, sesion_data, tree_sesiones, componente_id=None):
        window = ctk.CTkToplevel(self.root)
        window.title("Modificar Sesión")
        window.geometry("400x600")
        window.wm_attributes("-topmost", True)

        frame = ctk.CTkFrame(window, fg_color="#FFFFFF")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Obtener lista de esteticistas
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM asistentes ORDER BY nombre")
        esteticistas = c.fetchall()

        # Obtener el estado actual de la sesión
        c.execute("""
            SELECT realizada, porcentaje_asistente, comision_sumada, id, asistente_id
            FROM sesiones_realizadas
            WHERE tratamiento_asignado_id = ? AND numero_sesion = ?
        """, (tratamiento_id, int(sesion_data[0].split()[1])))
        sesion_actual = c.fetchone()
        esta_realizada = sesion_actual[0]
        porcentaje_anterior = sesion_actual[1]
        comision_sumada = sesion_actual[2]
        sesion_id = sesion_actual[3]

        # Obtener información del tratamiento asignado
        c.execute("""
            SELECT
                p.nombre,
                t.nombre,
                ta.sesiones_restantes,
                ta.costo_total / ta.sesiones_asignadas as costo_por_sesion,
                ta.costo_total
            FROM tratamientos_asignados ta
            JOIN pacientes p ON ta.paciente_id = p.id
            JOIN tratamientos t ON ta.tratamiento_id = t.id
            WHERE ta.id = ?
        """, (tratamiento_id,))
        info_tratamiento = c.fetchone()
        monto = info_tratamiento[3]

        conn.close()

        # Campos de modificación
        ctk.CTkLabel(frame, text=f"Modificar {sesion_data[0]}",
                    font=("Helvetica", 20, "bold")).pack(pady=10)

        # Fecha
        ctk.CTkLabel(frame, text="Fecha de la sesión:").pack(pady=5)
        fecha_sesion = DateEntry(frame, width=12, background='black',
                            foreground='white', borderwidth=2,
                            date_pattern='yyyy-mm-dd')
        fecha_sesion.pack(pady=5)
        fecha_sesion.set_date(datetime.strptime(sesion_data[1], '%Y-%m-%d').date())

        # Esteticista
        ctk.CTkLabel(frame, text="Esteticista:").pack(pady=5)
        esteticista_var = ctk.StringVar(value=sesion_data[2])
        esteticista_combo = ctk.CTkComboBox(frame,
                                        values=[e[1] for e in esteticistas],
                                        variable=esteticista_var)
        esteticista_combo.pack(pady=5)

    
        # Estado de pago
        ctk.CTkLabel(frame, text="Estado de pago:").pack(pady=5)
        estado_pago_var = ctk.StringVar(value=sesion_data[4])
        estado_pago_combo = ctk.CTkComboBox(frame,
                                        values=["PAGADO", "Pendiente"],
                                        variable=estado_pago_var)
        estado_pago_combo.pack(pady=5)

        # Porcentaje del asistente
        ctk.CTkLabel(frame, text="Porcentaje para este asistente:").pack(pady=5)
        porcentaje_asistente_entry = ctk.CTkEntry(frame)
        porcentaje_asistente_entry.insert(0, str(porcentaje_anterior))
        porcentaje_asistente_entry.pack(pady=5)

        # Checkbox para marcar si la sesión fue realizada
        realizada_var = ctk.BooleanVar(value=esta_realizada)
        realizada_check = ctk.CTkCheckBox(frame, text="Sesión realizada",
                                        variable=realizada_var)
        realizada_check.pack(pady=5)
        
        # Monto
        ctk.CTkLabel(frame, text="Monto de la sesión:").pack(pady=5)
        monto_label = ctk.CTkLabel(frame, text=f"${monto:.2f}", font=("Helvetica", 22, "bold"))
        monto_label.pack(pady=5)
    
        def guardar_cambios():
            try:
                conn = sqlite3.connect('spa_database.db')
                c = conn.cursor()

                # Obtener ID del esteticista
                esteticista_nombre = esteticista_var.get()
                asistente_id = next(e[0] for e in esteticistas if e[1] == esteticista_nombre)

                # Obtener el monto actual
                porcentaje_asistente = float(porcentaje_asistente_entry.get())

                # Determinar si se debe sumar o restar la comisión
                estado_sesion = 'Realizada' if realizada_var.get() else 'Pendiente'
                estado_pago = estado_pago_var.get()
                debe_sumar_comision = estado_sesion == 'Realizada' and estado_pago == 'PAGADO'

                # Si hay cambio en la comisión, actualizar tratamientos_asignados
                comision_calculada = monto * porcentaje_asistente / 100 if debe_sumar_comision else 0

                if comision_sumada and not debe_sumar_comision:
                    # Restar la comisión anterior
                    c.execute("""
                        UPDATE tratamientos_asignados
                        SET comision_asistente = comision_asistente - ?
                        WHERE id = ?
                    """, (comision_calculada, tratamiento_id))

                elif not comision_sumada and debe_sumar_comision:
                    # Sumar la nueva comisión
                    c.execute("""
                        UPDATE tratamientos_asignados
                        SET comision_asistente = comision_asistente + ?
                        WHERE id = ?
                    """, (comision_calculada, tratamiento_id))

                # Registrar el pago de comisión si corresponde
                if debe_sumar_comision and not comision_sumada:
                    c.execute("""
                        INSERT INTO pagos_asistentes (
                            asistente_id,
                            tratamiento_asignado_id,
                            sesion_id,
                            monto,
                            fecha_pago,
                            tipo_comision,
                            detalle
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        asistente_id,
                        tratamiento_id,
                        sesion_id,
                        comision_calculada,
                        fecha_sesion.get_date().strftime('%Y-%m-%d'),
                        'Sesion',
                        f'Comisión por sesión {sesion_data[0]}'
                    ))

                sesion_anterior_completada = comision_sumada == 1
                sesion_nueva_completada = estado_pago == "PAGADO" and realizada_var.get()
                
                # Actualizar sesiones_restantes solo si hay un cambio real en el estado
                if not sesion_anterior_completada and sesion_nueva_completada:
                    # La sesión pasa de no completada a completada
                    c.execute("""
                        UPDATE tratamientos_asignados
                        SET sesiones_restantes = sesiones_restantes - 1
                        WHERE id = ?
                    """, (tratamiento_id,))
                elif sesion_anterior_completada and not sesion_nueva_completada:
                    # La sesión pasa de completada a no completada
                    c.execute("""
                        UPDATE tratamientos_asignados
                        SET sesiones_restantes = sesiones_restantes + 1
                        WHERE id = ?
                    """, (tratamiento_id,))

                # Actualizar la sesión
                c.execute("""
                    UPDATE sesiones_realizadas
                    SET fecha_sesion = ?,
                        asistente_id = ?,
                        monto_abonado = ?,
                        estado_pago = ?,
                        realizada = ?,
                        estado_sesion = ?,
                        porcentaje_asistente = ?,
                        comision_sumada = ?
                    WHERE tratamiento_asignado_id = ? AND numero_sesion = ?
                """, (
                    fecha_sesion.get_date().strftime('%Y-%m-%d'),
                    asistente_id,
                    monto,
                    estado_pago_var.get(),
                    realizada_var.get(),
                    estado_sesion,
                    porcentaje_asistente,
                    1 if debe_sumar_comision else 0,
                    tratamiento_id,
                    int(sesion_data[0].split()[1])
                ))

                conn.commit()
                conn.close()

                self.cargar_sesiones(tree_sesiones, tratamiento_id, componente_id)
                window.destroy()
                messagebox.showinfo("Éxito", "Sesión modificada correctamente", parent=self.root)

            except Exception as e:
                print(f"Debug - Error detallado: {str(e)}")
                messagebox.showerror("Error", f"Error al modificar la sesión: {str(e)}", parent=self.root)



        btn_style = {
            "corner_radius": 10,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white"
        }

        ctk.CTkButton(frame, text="Guardar cambios",
                    command=guardar_cambios, **btn_style).pack(pady=10)
        ctk.CTkButton(frame, text="Cancelar",
                    command=window.destroy, **btn_style).pack(pady=5)

        def agregar_sesion(self):
            self.registrar_nueva_sesion(tratamiento_id, tree_sesiones, self.ventana_detalle)

            btn_style = {
                "corner_radius": 10,
                "fg_color": "#000000",
                "hover_color": "#676767",
                "border_width": 2,
                "text_color": "white"
            }

            ctk.CTkButton(btn_style, text="Agregar Sesión",
                        command=agregar_sesion, **btn_style).pack(side="left", padx=5)
            ctk.CTkButton(btn_style, text="Cerrar",
                        command=self.ventana_detalle.destroy, **btn_style).pack(side="right", padx=5)

            # Cargar sesiones existentes
            self.cargar_sesiones(tree_sesiones, tratamiento_id)

    def registrar_nueva_sesion(self, tratamiento_id, tree_sesiones, ventana_detalle, componente_id=None):
        # Primero verificar si quedan sesiones disponibles
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()

        # Verificar si es una promoción
        c.execute("""
            SELECT t.es_promocion
            FROM tratamientos t
            JOIN tratamientos_asignados ta ON t.id = ta.tratamiento_id
            WHERE ta.id = ?
        """, (tratamiento_id,))
        es_promocion = c.fetchone()[0]

        if es_promocion:
            pass
        else:
            # Verificar sesiones restantes en tratamiento normal
            c.execute("""
                SELECT sesiones_restantes
                FROM tratamientos_asignados
                WHERE id = ?
            """, (tratamiento_id,))
            sesiones_restantes = c.fetchone()[0]

            if sesiones_restantes <= 0:
                conn.close()
                self.ventana_detalle.withdraw()
                messagebox.showwarning("Aviso", "Todas las sesiones del tratamiento han sido completadas.", parent=self.root)
                return


        # Crear ventana para nueva sesión
        window = ctk.CTkToplevel(self.root)
        window.title("Registrar Nueva Sesión")
        window.geometry("400x700")
        window.wm_attributes("-topmost", True)  # Mostrar siempre delante

        frame = ctk.CTkFrame(window, fg_color="#FFFFFF")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Obtener información del tratamiento
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()

        # Verificar si es una promoción
        c.execute("""
            SELECT t.es_promocion
            FROM tratamientos t
            JOIN tratamientos_asignados ta ON t.id = ta.tratamiento_id
            WHERE ta.id = ?
        """, (tratamiento_id,))
        es_promocion = c.fetchone()[0]

            
        # Modificada la consulta para incluir información básica del tratamiento
        c.execute("""
            SELECT
                p.nombre,
                t.nombre,
                ta.sesiones_restantes,
                ta.costo_total / ta.sesiones_asignadas as costo_por_sesion,
                ta.costo_total
            FROM tratamientos_asignados ta
            JOIN pacientes p ON ta.paciente_id = p.id
            JOIN tratamientos t ON ta.tratamiento_id = t.id
            WHERE ta.id = ?
        """, (tratamiento_id,))
        
        info_tratamiento = c.fetchone()
        monto = info_tratamiento[3]

        # Obtener lista de esteticistas
        c.execute("SELECT id, nombre FROM asistentes ORDER BY nombre")
        esteticistas = c.fetchall()
        conn.close()

        title = ctk.CTkLabel(frame, text="Registrar Nueva Sesión",
                            font=("Helvetica", 20, "bold"))
        title.pack(pady=10)
        ctk.CTkLabel(frame, text=f"Paciente: {info_tratamiento[0]}",
                    font=("Helvetica", 12, "bold")).pack(pady=5)
        ctk.CTkLabel(frame, text=f"Tratamiento: {info_tratamiento[1]}").pack(pady=5)
        

        # Selector de esteticista
        ctk.CTkLabel(frame, text="Esteticista:").pack(pady=5)
        esteticista_var = ctk.StringVar()
        esteticista_combo = ctk.CTkComboBox(frame,
                                        values=[e[1] for e in esteticistas],
                                        variable=esteticista_var)
        esteticista_combo.pack(pady=5)

        # Campo para porcentaje del asistente
        ctk.CTkLabel(frame, text="Porcentaje para este asistente:").pack(pady=5)
        porcentaje_asistente_entry = ctk.CTkEntry(frame)
        porcentaje_asistente_entry.pack(pady=5)

        # Fecha de la sesión
        ctk.CTkLabel(frame, text="Fecha de la sesión:").pack(pady=5)
        fecha_sesion = DateEntry(frame, width=12, background='black',
                            foreground='white', borderwidth=2,
                            date_pattern='yyyy-mm-dd')
        fecha_sesion.pack(pady=5)

        # Estado de pago
        ctk.CTkLabel(frame, text="Estado de pago:").pack(pady=5)
        estado_pago_var = ctk.StringVar(value="Pendiente")
        estado_pago_combo = ctk.CTkComboBox(frame,
                                        values=["PAGADO", "Pendiente"],
                                        variable=estado_pago_var)
        estado_pago_combo.pack(pady=5)
        
        # Monto abonado
        ctk.CTkLabel(frame, text="Monto de la sesión:").pack(pady=5)
        monto_label = ctk.CTkLabel(frame, text=f"${info_tratamiento[3]:.2f}", font=("Helvetica", 22, "bold"))
        monto_label.pack(pady=5) 

        # Checkbox para marcar si la sesión fue realizada
        realizada_var = ctk.BooleanVar()
        realizada_check = ctk.CTkCheckBox(frame, text="Sesión realizada", variable=realizada_var)
        realizada_check.pack(pady=5)

        def confirmar_sesion():
            try:
                # Validar monto y porcentaje
                try:
                    porcentaje_asistente = float(porcentaje_asistente_entry.get())
                except ValueError:
                    raise ValueError("El porcentaje debe ser números válidos")

                # Obtener ID del esteticista seleccionado
                esteticista_nombre = esteticista_var.get()
                asistente_sesion_id = next(e[0] for e in esteticistas if e[1] == esteticista_nombre)

                conn = sqlite3.connect('spa_database.db')
                c = conn.cursor()

                fecha_actual = fecha_sesion.get_date().strftime('%Y-%m-%d')
                estado_sesion = 'Realizada' if realizada_var.get() else 'Pendiente'
                estado_pago = estado_pago_var.get()

                # Calcular si se debe sumar la comisión
                debe_sumar_comision = estado_sesion == 'Realizada' and estado_pago == 'Pagado'
                comision_calculada = (monto * porcentaje_asistente / 100) if debe_sumar_comision else 0

                if es_promocion:
                    pass

                else:
                    # Si se debe sumar la comisión, actualizar la comisión del esteticista
                    if debe_sumar_comision:
                        c.execute("""
                            UPDATE esteticistas
                            SET comision = comision + ?
                            WHERE id = ?
                        """, (comision_calculada, asistente_sesion_id))

                    # Insertar la sesión para tratamientos normales
                    c.execute("""
                        INSERT INTO sesiones_realizadas (
                            tratamiento_asignado_id,
                            asistente_id,
                            fecha_sesion,
                            numero_sesion,
                            monto_abonado,
                            estado_pago,
                            estado_sesion,
                            porcentaje_asistente,
                            proxima_cita,
                            comision_sumada,
                            realizada
                        )
                        VALUES (?, ?, ?, (
                            SELECT COUNT(*) + 1
                            FROM sesiones_realizadas
                            WHERE tratamiento_asignado_id = ?
                        ), ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        tratamiento_id,
                        asistente_sesion_id,
                        fecha_actual,
                        tratamiento_id,
                        monto,
                        estado_pago,
                        estado_sesion,
                        porcentaje_asistente,
                        (datetime.strptime(fecha_actual, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d'),
                        1 if debe_sumar_comision else 0,
                        realizada_var.get()
                    ))

                    # Actualizar el tratamiento asignado
                    estado_sesion = 'Realizada' if realizada_var.get() else 'Pendiente'
                    estado_pago = estado_pago_var.get()

                    # Solo actualizar sesiones restantes si está pagada Y realizada
                    if estado_pago == "PAGADO" and estado_sesion == "Realizada":
                        c.execute("""
                            UPDATE tratamientos_asignados
                            SET sesiones_restantes = sesiones_restantes - 1,
                                total_pagado = total_pagado + ?,
                                saldo_pendiente = saldo_pendiente - ?
                            WHERE id = ?
                        """, (monto, monto, tratamiento_id))

                

                conn.commit()
                conn.close()

                self.cargar_sesiones(tree_sesiones, tratamiento_id, componente_id if es_promocion else None)
                window.destroy()
                self.ventana_detalle.lift()  # Mantener ventana detalle al frente
                messagebox.showinfo("Éxito", "Sesión registrada correctamente", parent=self.root)
            except Exception as e:
                print(f"Debug - Error detallado: {str(e)}")
                messagebox.showerror("Error", f"Error al registrar la sesión: {str(e)}", parent=self.root)
    #...

        btn_style = {
            "corner_radius": 10,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white"
        }

        ctk.CTkButton(frame, text="Confirmar",
                    command=confirmar_sesion, **btn_style).pack(pady=10)
        ctk.CTkButton(frame, text="Cancelar",
                    command=window.destroy, **btn_style).pack(pady=5)
    
            
    def marcar_como_completado(self, tratamiento_id):
        # Actualizar el estado del tratamiento a INACTIVO
        execute_query("UPDATE tratamientos_asignados SET estado = 'INACTIVO' WHERE id = ?", (tratamiento_id,))

        # Obtener información del tratamiento para registrar en reportes
        tratamiento_info = execute_query("SELECT p.nombre, t.nombre, t.precio FROM tratamientos_asignados ta JOIN pacientes p ON ta.paciente_id = p.id JOIN tratamientos t ON ta.tratamiento_id = t.id WHERE ta.id = ?", (tratamiento_id,), fetch=True)[0]

        # Registrar en reportes
        execute_query("""
            INSERT INTO reportes (
                fecha,
                concepto,
                ingreso,
                egreso,
                detalle
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().strftime("%Y-%m-%d"),
            "Tratamiento completado",
            tratamiento_info[2],  # Precio del tratamiento
            0,  # Egreso (puedes ajustar esto si hay algún costo asociado)
            f"Tratamiento completado - {tratamiento_info[1]} - {tratamiento_info[0]}"
        ))

        # Actualizar la lista para reflejar los cambios
        self.actualizar_lista()

    def volver_menu_principal(self):
        self.main_system.show_main_menu()