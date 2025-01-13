import customtkinter as ctk
from tkinter import simpledialog, ttk, messagebox
import sqlite3
from datetime import datetime
from database import execute_query
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class AsistentesManagement:
    def __init__(self, root, main_system):
        self.root = root
        self.main_system = main_system
        self.tree = ttk.Treeview(self.root)
        self.window = None
        
    def cargar_datos_asistente(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item = self.tree.item(selected_item)
            asistente = item['values']
            self.nombre_entry.delete(0, 'end')
            self.nombre_entry.insert(0, asistente[1])
            self.telefono_entry.delete(0, 'end')
            self.telefono_entry.insert(0, asistente[2])


    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título con fuente más grande
        title = ctk.CTkLabel(main_frame, text="Control de Esteticista", font=("Helvetica", 36, "bold"))
        title.pack(pady=(50, 40))

        # Formulario principal
        form_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        form_frame.pack(fill="x", padx=20, pady=10)

        # Crear contenedor para campos en dos columnas
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.pack(fill="x", padx=40)

        # Campos del formulario en línea horizontal
        field_style = {"width": 200, "height": 32}
        
        # Container para Nombre
        nombre_container = ctk.CTkFrame(fields_frame, fg_color="transparent")
        nombre_container.pack(padx=(0, 40))
        ctk.CTkLabel(nombre_container, text="Nombre:", font=("Helvetica", 12)).pack(side="left")
        self.nombre_entry = ctk.CTkEntry(nombre_container, placeholder_text="Ingrese nombre", **field_style)
        self.nombre_entry.pack(padx=(10, 0))

        # Container para Teléfono
        telefono_container = ctk.CTkFrame(fields_frame, fg_color="transparent")
        telefono_container.pack(padx=(0, 40), pady=10)
        ctk.CTkLabel(telefono_container, text="Teléfono:", font=("Helvetica", 12)).pack(side="left")
        self.telefono_entry = ctk.CTkEntry(telefono_container, placeholder_text="Ingrese teléfono", **field_style)
        self.telefono_entry.pack(padx=(10, 0))

        # Botones de acción
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=30, fill="y")

        btn_style = {
            "width": 150,
            "height": 40,
            "corner_radius": 8,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white",
        }
        
        close_btn_style = btn_style.copy()
        close_btn_style.update(
            {
                "fg_color": "#e74c3c",
                "hover_color": "#c0392b",
                "border_color": "#c0392b",
            }
        )

        # Primera fila de botones
        buttons_container = ctk.CTkFrame(btn_frame, fg_color="transparent")
        buttons_container.pack(fill="x")

        ctk.CTkButton(buttons_container, text="Agregar", command=self.agregar_asistente, 
                    **btn_style).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(buttons_container, text="Modificar", command=self.modificar_asistente, 
                    **btn_style).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(buttons_container, text="Volver al Menú Principal", command=self.volver_menu_principal, 
                    **close_btn_style).pack(side="left", padx=5, expand=True)

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

        # Tabla de asistentes
        table_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", border_width=1)
        table_frame.pack(fill="both", expand=True, pady=(10, 20), padx=40)

        columns = ("ID", "Nombre", "Teléfono", "Ingresos Totales")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")

        # Configurar columnas con anchos específicos
        column_widths = {
            "ID": 80, 
            "Nombre": 200, 
            "Teléfono": 150, 
            "Ingresos Totales": 150
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

        self.tree.bind("<Double-1>", self.ver_detalle_asistente)
        self.tree.bind("<ButtonRelease-1>", self.cargar_datos_asistente)

        # Frame para los botones de pago (si se necesitan)
        self.buttons_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        self.buttons_frame.pack(fill="x", pady=(0, 10))

        self.actualizar_lista_asistentes()
        
        
    def limpiar_campos(self):
        self.nombre_entry.delete(0, 'end')
        self.telefono_entry.delete(0, 'end')
        
    def agregar_asistente(self):
        try:
            nombre = self.nombre_entry.get().strip()
            telefono = self.telefono_entry.get().strip()
            
            # Validaciones más específicas
            if not nombre:
                raise ValueError("El nombre es obligatorio")
            if not telefono:
                raise ValueError("El teléfono es obligatorio")

            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()

            # Verificar si ya existe un asistente con el mismo nombre y teléfono
            c.execute("""
                SELECT COUNT(*) FROM asistentes 
                WHERE nombre = ? AND telefono = ?
            """, (nombre, telefono))
            
            if c.fetchone()[0] > 0:
                conn.close()
                raise ValueError("Ya existe un Esteticista con estos datos")

            c.execute("""
                INSERT INTO asistentes (nombre, telefono)
                VALUES (?, ?)
            """, (nombre, telefono))
            
            conn.commit()
            conn.close()

            self.actualizar_lista_asistentes()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", "Esteticista agregado correctamente", parent=self.root)
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al agregar Esteticista: {str(e)}", parent=self.root)
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e), parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error inesperado: {str(e)}", parent=self.root)

    def modificar_asistente(self):
        try:
            item = self.tree.selection()[0]
            asistente_id = self.tree.item(item)["values"][0]

            nombre = self.nombre_entry.get()
            telefono = self.telefono_entry.get()

            if not nombre or not telefono:
                raise ValueError("El nombre y teléfono son obligatorios.")

            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()

            c.execute("""
                UPDATE asistentes 
                SET nombre = ?, telefono = ?
                WHERE id = ?
            """, (nombre, telefono, asistente_id))
            
            conn.commit()
            conn.close()

            self.actualizar_lista_asistentes()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", "Esteticista modificado correctamente", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el Esteticista: {e}", parent=self.root)


        
    def actualizar_lista_asistentes(self):
        # Limpiar la tabla y el frame de botones
        self.tree.delete(*self.tree.get_children())
        for widget in self.buttons_frame.winfo_children():
            widget.destroy() 
        
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        # Consulta modificada para calcular solo comisiones de sesiones realizadas y pagadas
        # Consulta modificada para calcular solo comisiones de sesiones realizadas y pagadas que no han sido pagadas al esteticista
        c.execute("""
            SELECT 
                a.id, 
                a.nombre,
                a.telefono,
                COALESCE(
                    (SELECT SUM(ROUND(sr.monto_abonado * sr.porcentaje_asistente / 100.0, 2))
                    FROM sesiones_realizadas sr
                    WHERE sr.asistente_id = a.id
                    AND sr.estado_sesion = 'Realizada'
                    AND sr.estado_pago = 'PAGADO'
                    AND sr.id NOT IN (
                        SELECT sesion_id 
                        FROM pagos_asistentes 
                        WHERE asistente_id = a.id 
                        AND tipo_comision = 'SESION'
                    )
                    ) 
                , 0) as ingresos_sesiones,
                (SELECT COUNT(*)
                FROM sesiones_realizadas sr
                WHERE sr.asistente_id = a.id
                AND sr.estado_sesion = 'Realizada'
                AND sr.estado_pago = 'PAGADO'
                AND sr.id NOT IN (
                    SELECT sesion_id 
                    FROM pagos_asistentes 
                    WHERE asistente_id = a.id 
                    AND tipo_comision = 'SESION'
                    AND monto IS NOT NULL
                )) as total_sesiones,
                COALESCE(
                    (SELECT SUM(ROUND(ta.costo_total * ta.porcentaje_vendedor / 100.0, 2))
                    FROM tratamientos_asignados ta
                    WHERE ta.vendedor_id = a.id
                    AND ta.total_pagado >= ta.costo_total
                    AND ta.id NOT IN (
                        SELECT tratamiento_asignado_id 
                        FROM pagos_asistentes 
                        WHERE asistente_id = a.id 
                        AND tipo_comision = 'VENTA'
                        AND monto IS NOT NULL
                    ))
                , 0) as ingresos_ventas
            FROM asistentes a
            GROUP BY a.id, a.nombre, a.telefono
            ORDER BY a.nombre
        """)
        
        asistentes = c.fetchall()
        conn.close()

        # Crear un contenedor horizontal para los botones
        buttons_container = ctk.CTkFrame(self.buttons_frame, fg_color="transparent")
        buttons_container.pack(fill="x", padx=5)

        for asistente in asistentes:
            total_ingresos = asistente[3] + asistente[5]
            self.tree.insert("", "end", values=(
                asistente[0],  # ID
                asistente[1],  # Nombre
                asistente[2],  # Teléfono
                f"${total_ingresos:.2f}" 
            ))
            
    def ver_detalle_asistente(self, event_or_id=None, nombre_asistente=None):
        try:
            # Determinar el ID del asistente según el tipo de entrada
            if isinstance(event_or_id, int):
                asistente_id = event_or_id
            else:
                item = self.tree.identify('item', event_or_id.x, event_or_id.y)
                if not item:
                    messagebox.showwarning("Advertencia", "Por favor seleccione un Esteticista para ver el detalle", parent=self.root)
                    return
                asistente_id = self.tree.item(item)["values"][0]
                nombre_asistente = self.tree.item(item)["values"][1]

            self.window = ctk.CTkToplevel(self.root)
            self.window.title("Detalle del Esteticista")
            self.window.geometry("1200x1000")
            self.window.wm_attributes("-topmost", True)

            main_frame = ctk.CTkFrame(self.window, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Título
            title_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
            title_frame.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(title_frame, 
                        text=f"Detalle del Esteticista: {nombre_asistente}", 
                        font=("Helvetica", 24, "bold")).pack(side="left")

            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()

            ## Obtener totales
            c.execute("""
                SELECT 
                    COALESCE(SUM(ROUND(sr.monto_abonado * sr.porcentaje_asistente / 100.0, 2)), 0) as total_sesiones,
                    (SELECT COALESCE(SUM(ROUND(ta.costo_total * ta.porcentaje_vendedor / 100.0, 2)), 0)
                    FROM tratamientos_asignados ta
                    WHERE ta.vendedor_id = ?
                    AND ta.total_pagado >= ta.costo_total
                    AND ta.id NOT IN (
                        SELECT tratamiento_asignado_id 
                        FROM pagos_asistentes 
                        WHERE asistente_id = ? 
                        AND tipo_comision = 'VENTA'
                    )) as total_ventas
                FROM sesiones_realizadas sr
                WHERE sr.asistente_id = ?
                AND sr.estado_sesion = 'Realizada'
                AND sr.estado_pago = 'PAGADO'
                AND sr.id NOT IN (SELECT sesion_id FROM pagos_asistentes WHERE asistente_id = ? AND tipo_comision = 'SESION')
            """, (asistente_id, asistente_id, asistente_id, asistente_id))
            
            totales = c.fetchone()
            total_sesiones = totales[0]
            total_ventas = totales[1]
            total_general = total_sesiones + total_ventas

            totales_frame = ctk.CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
            totales_frame.pack(fill="x", pady=(0, 20), padx=5)
            
            total_label_style = {
                "font": ("Helvetica", 14, "bold"),
                "fg_color": "#F0F0F0",
                "corner_radius": 8
            }

            # Contenedor para los totales
            totales_container = ctk.CTkFrame(totales_frame, fg_color="transparent")
            totales_container.pack(pady=15)

            ctk.CTkLabel(totales_container, 
                        text=f"Total por Sesiones: ${total_sesiones:.2f}",
                        **total_label_style).pack(side="left", padx=30)
            ctk.CTkLabel(totales_container,
                        text=f"Total por Ventas: ${total_ventas:.2f}",
                        **total_label_style).pack(side="left", padx=30)
            ctk.CTkLabel(totales_container,
                        text=f"Total General: ${total_general:.2f}",
                        **total_label_style).pack(side="left", padx=30)
            
            
           # Estilo común para las tablas
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
            style.map(
                "Treeview",
                background=[("selected", "#E0E0E0")],
                foreground=[("selected", "#000000")]
            )

            # Frame para las tablas
            tables_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            tables_frame.pack(fill="both", expand=True)

            # Frame para sesiones
            sesiones_frame = ctk.CTkFrame(tables_frame, fg_color="#FFFFFF")
            sesiones_frame.pack(fill="both", expand=True, pady=(0, 10))

            ctk.CTkLabel(sesiones_frame, 
                        text="Sesiones Realizadas", 
                        font=("Helvetica", 16, "bold")).pack(pady=(0, 10))

            # Crear frame contenedor para tabla y scrollbars de sesiones
            table_container_sesiones = ctk.CTkFrame(sesiones_frame, fg_color="transparent")
            table_container_sesiones.pack(fill="both", expand=True, padx=5)

            # Crear la tabla de sesiones
            columns_sesiones = ("Paciente", "Tratamiento", "Fecha", "Sesión", "Porcentaje", "Monto", "Estado")
            tree_sesiones = ttk.Treeview(table_container_sesiones, columns=columns_sesiones, show="headings", height=8)

            # Configurar scrollbars para sesiones
            y_scroll_sesiones = ttk.Scrollbar(table_container_sesiones, orient="vertical", command=tree_sesiones.yview)
            x_scroll_sesiones = ttk.Scrollbar(table_container_sesiones, orient="horizontal", command=tree_sesiones.xview)
            tree_sesiones.configure(yscrollcommand=y_scroll_sesiones.set, xscrollcommand=x_scroll_sesiones.set)

            # Empaquetar scrollbars y tabla de sesiones
            y_scroll_sesiones.pack(side="right", fill="y")
            x_scroll_sesiones.pack(side="bottom", fill="x")
            tree_sesiones.pack(fill="both", expand=True)

            # Configurar columnas de sesiones
            for col in columns_sesiones:
                tree_sesiones.heading(col, text=col)
                tree_sesiones.column(col, width=110)

            
            
         

            # Insertar datos en sesiones
            c.execute("""
                SELECT 
                    p.nombre,
                    t.nombre,
                    sr.fecha_sesion,
                    sr.numero_sesion,
                    sr.porcentaje_asistente,
                    sr.monto_abonado,
                    sr.estado_pago,
                    sr.estado_sesion
                FROM sesiones_realizadas sr
                JOIN tratamientos_asignados ta ON sr.tratamiento_asignado_id = ta.id
                JOIN pacientes p ON ta.paciente_id = p.id
                JOIN tratamientos t ON ta.tratamiento_id = t.id
                WHERE sr.asistente_id = ?
                AND sr.estado_sesion = 'Realizada'
                AND sr.estado_pago = 'PAGADO'
                AND sr.id NOT IN (
                    SELECT sesion_id 
                    FROM pagos_asistentes 
                    WHERE asistente_id = ? 
                    AND tipo_comision = 'SESION'
                )
                ORDER BY sr.fecha_sesion DESC
            """, (asistente_id, asistente_id))
            
            for row in c.fetchall():
                monto_comision = (row[5] * row[4] / 100.0) if row[5] and row[4] else 0
                tree_sesiones.insert("", "end", values=(
                    row[0],  # Paciente
                    row[1],  # Tratamiento
                    row[2],  # Fecha
                    f"Sesión {row[3]}",  # Número de sesión
                    f"{row[4]}%",  # Porcentaje
                    f"${monto_comision:.2f}",  # Monto de comisión
                    f"{row[6]} ({row[7]})"  # Estado
                ))

            # Tabla de ventas realizadas
            ventas_frame = ctk.CTkFrame(tables_frame, fg_color="#FFFFFF")
            ventas_frame.pack(fill="both", expand=True, pady=(10, 0))

            ctk.CTkLabel(ventas_frame, 
                        text="Tratamientos Vendidos", 
                        font=("Helvetica", 16, "bold")).pack(pady=(0, 10))

            # Crear frame contenedor para tabla y scrollbars de ventas
            table_container_ventas = ctk.CTkFrame(ventas_frame, fg_color="transparent")
            table_container_ventas.pack(fill="both", expand=True, padx=5)

            # Crear la tabla de ventas
            columns_ventas = ("Paciente", "Tratamiento", "Fecha", "Porcentaje", "Monto Total", "Comisión", "Estado")
            tree_ventas = ttk.Treeview(table_container_ventas, columns=columns_ventas, show="headings", height=8)

            # Configurar scrollbars para ventas
            y_scroll_ventas = ttk.Scrollbar(table_container_ventas, orient="vertical", command=tree_ventas.yview)
            x_scroll_ventas = ttk.Scrollbar(table_container_ventas, orient="horizontal", command=tree_ventas.xview)
            tree_ventas.configure(yscrollcommand=y_scroll_ventas.set, xscrollcommand=x_scroll_ventas.set)

            # Empaquetar scrollbars y tabla de ventas
            y_scroll_ventas.pack(side="right", fill="y")
            x_scroll_ventas.pack(side="bottom", fill="x")
            tree_ventas.pack(fill="both", expand=True)

            # Configurar columnas de ventas
            for col in columns_ventas:
                tree_ventas.heading(col, text=col)
                tree_ventas.column(col, width=110)

            c.execute("""
                SELECT 
                    p.nombre,
                    t.nombre,
                    ta.fecha_asignacion,
                    ta.porcentaje_vendedor,
                    ta.costo_total,
                    ROUND(ta.costo_total * ta.porcentaje_vendedor / 100.0, 2) as comision,
                    CASE 
                        WHEN ta.total_pagado >= ta.costo_total THEN 'PAGADO'
                        WHEN ta.total_pagado > 0 THEN 'PARCIAL'
                        ELSE 'PENDIENTE'
                    END as estado
                FROM tratamientos_asignados ta
                JOIN pacientes p ON ta.paciente_id = p.id
                JOIN tratamientos t ON ta.tratamiento_id = t.id
                WHERE ta.vendedor_id = ?
                AND ta.total_pagado >= ta.costo_total
                AND ta.id NOT IN (
                    SELECT tratamiento_asignado_id 
                    FROM pagos_asistentes 
                    WHERE asistente_id = ? 
                    AND tipo_comision = 'VENTA'
                )
                ORDER BY ta.fecha_asignacion DESC
            """, (asistente_id, asistente_id))
            
            for row in c.fetchall():
                tree_ventas.insert("", "end", values=(
                    row[0],  # Paciente
                    row[1],  # Tratamiento
                    row[2],  # Fecha
                    f"{row[3]}%",  # Porcentaje
                    f"${row[4]:.2f}",  # Monto total
                    f"${row[5]:.2f}",  # Comisión
                    row[6]  # Estado
                ))

            # Botones de acción
            btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            btn_frame.pack(pady=20)

            btn_style = {
                "width": 150,
                "height": 35,
                "corner_radius": 8,
                "fg_color": "#191919",
                "hover_color": "#676767",
                "font": ("Helvetica", 12, "bold")
            }
            
            def realizar_pago_desde_detalle():
                self.pagar_asistente(asistente_id)
                self.actualizar_lista_asistentes()

            ctk.CTkButton(btn_frame, 
                        text="Registrar Pago",
                        command=realizar_pago_desde_detalle,
                        **btn_style).pack(side="left", padx=10)
            
            ctk.CTkButton(btn_frame, 
                        text="Cerrar",
                        command=self.window.destroy,
                        **btn_style).pack(side="left", padx=10)

            conn.close()

        except Exception as e:
            self.window.withdraw()
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}", parent=self.root)
            
            
            
    def pagar_asistente(self, asistente_id):
        # Creamos la conexión aquí y la pasaremos a las funciones que la necesiten
        conn = None
        try:
            # Usar un `with` para manejar la conexión automáticamente
            with sqlite3.connect('spa_database.db') as conn:
                c = conn.cursor()

                # Obtener información del asistente
                c.execute("SELECT nombre FROM asistentes WHERE id = ?", (asistente_id,))
                nombre_asistente = c.fetchone()[0]

                # Obtener pagos pendientes con detalles para el reporte
                c.execute("""
                    SELECT 
                        'SESION' as tipo,
                        p.nombre as paciente,
                        t.nombre as tratamiento,
                        sr.fecha_sesion as fecha,
                        sr.numero_sesion,
                        (sr.monto_abonado * sr.porcentaje_asistente / 100.0) as monto
                    FROM sesiones_realizadas sr
                    JOIN tratamientos_asignados ta ON sr.tratamiento_asignado_id = ta.id
                    JOIN pacientes p ON ta.paciente_id = p.id
                    JOIN tratamientos t ON ta.tratamiento_id = t.id
                    WHERE sr.asistente_id = ?
                    AND sr.estado_pago = 'PAGADO'
                    AND sr.estado_sesion = 'Realizada'
                    AND sr.id NOT IN (
                        SELECT sesion_id FROM pagos_asistentes 
                        WHERE asistente_id = ? AND tipo_comision = 'SESION'
                    )
                    
                    UNION ALL
                    
                    SELECT 
                        'VENTA' as tipo,
                        p.nombre as paciente,
                        t.nombre as tratamiento,
                        ta.fecha_asignacion as fecha,
                        NULL as numero_sesion,
                        (ta.costo_total * ta.porcentaje_vendedor / 100.0) as monto
                    FROM tratamientos_asignados ta
                    JOIN pacientes p ON ta.paciente_id = p.id
                    JOIN tratamientos t ON ta.tratamiento_id = t.id
                    WHERE ta.vendedor_id = ?
                    AND ta.total_pagado >= ta.costo_total
                    AND ta.id NOT IN (
                        SELECT tratamiento_asignado_id FROM pagos_asistentes 
                        WHERE asistente_id = ? AND tipo_comision = 'VENTA'
                    )
                    ORDER BY fecha
                """, (asistente_id, asistente_id, asistente_id, asistente_id))
                
                detalles_pago = c.fetchall()

                if not detalles_pago:
                    self.window.withdraw()
                    messagebox.showinfo("Info", "No hay pagos pendientes", parent=self.root)
                    return

                total_pendiente = sum(detalle[5] for detalle in detalles_pago if detalle[5] is not None)

                # Crear ventana de confirmación de pago
                ventana_pago = ctk.CTkToplevel(self.root)
                ventana_pago.title("Confirmar Pago")
                ventana_pago.geometry("400x250")
                ventana_pago.wm_attributes("-topmost", True)
                ventana_pago.grab_set()

                frame = ctk.CTkFrame(ventana_pago, fg_color="#FFFFFF")
                frame.pack(fill="both", expand=True, padx=20, pady=20)

                ctk.CTkLabel(frame, 
                            text=f"Total a pagar: ${total_pendiente:.2f}",
                            font=("Helvetica", 16, "bold")).pack(pady=20)

                detalle_entry = ctk.CTkEntry(frame, placeholder_text="Detalle del pago (opcional)")
                detalle_entry.pack(pady=20, fill="x")

                def confirmar_pago():
                    try:
                        fecha_actual = datetime.now().strftime('%Y-%m-%d')
                        detalle = detalle_entry.get()

                        # Registrar pagos de sesiones
                        c.execute("""
                            INSERT INTO pagos_asistentes 
                                (asistente_id, tratamiento_asignado_id, sesion_id, monto, fecha_pago, detalle, tipo_comision)
                            SELECT 
                                ?, 
                                ta.id, 
                                sr.id,
                                (sr.monto_abonado * sr.porcentaje_asistente / 100.0),
                                ?,
                                ?,
                                'SESION'
                            FROM sesiones_realizadas sr
                            JOIN tratamientos_asignados ta ON sr.tratamiento_asignado_id = ta.id
                            WHERE sr.asistente_id = ?
                            AND sr.estado_pago = 'PAGADO'
                            AND sr.estado_sesion = 'Realizada'
                            AND sr.id NOT IN (
                                SELECT sesion_id FROM pagos_asistentes 
                                WHERE asistente_id = ? AND tipo_comision = 'SESION'
                            )
                        """, (asistente_id, fecha_actual, detalle, asistente_id, asistente_id))

                        # Registrar pagos de ventas
                        c.execute("""
                            INSERT INTO pagos_asistentes 
                                (asistente_id, tratamiento_asignado_id, sesion_id, monto, fecha_pago, detalle, tipo_comision)
                            SELECT 
                                ?, 
                                id, 
                                NULL,
                                (costo_total * porcentaje_vendedor / 100.0),
                                ?,
                                ?,
                                'VENTA'
                            FROM tratamientos_asignados
                            WHERE vendedor_id = ?
                            AND total_pagado >= costo_total
                            AND id NOT IN (
                                SELECT tratamiento_asignado_id FROM pagos_asistentes 
                                WHERE asistente_id = ? AND tipo_comision = 'VENTA'
                            )
                        """, (asistente_id, fecha_actual, detalle, asistente_id, asistente_id))

                        conn.commit()
                    
                        
                        # Generar reporte PDF
                        nombre_archivo = self.generar_reporte_pdf(fecha_actual, detalle, detalles_pago, total_pendiente, nombre_asistente)
                        
                        ventana_pago.destroy()
                        self.window.withdraw()
                        messagebox.showinfo("Éxito", 
                                        f"Pago total de ${total_pendiente:.2f} registrado correctamente.\n"
                                        f"Se ha generado el reporte: {nombre_archivo}", parent=self.root)
                        self.actualizar_lista_asistentes()
                    except Exception as e:
                        messagebox.showerror("Error", f"Error al registrar el pago: {e}", parent=self.root)
        

                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.pack(pady=20)
                def cerrar_ventanas():
                    ventana_pago.destroy()
                    self.window.withdraw()
                ctk.CTkButton(btn_frame, text="Confirmar Pago", 
                            command=confirmar_pago).pack(side="left", padx=10)
                ctk.CTkButton(btn_frame, text="Cancelar", 
                            command=cerrar_ventanas).pack(side="left", padx=10)

        except Exception as e:
            self.window.withdraw()
            messagebox.showerror("Error", f"Error al procesar el pago: {e}", parent=self.root)


    def generar_reporte_pdf(self, fecha_pago, detalle, detalles_pago, total_pendiente, nombre_asistente):
        fecha_formateada = datetime.strptime(fecha_pago, '%Y-%m-%d').strftime('%d-%m-%Y')
        nombre_archivo = f"reporte_pago_{nombre_asistente}_{fecha_formateada}.pdf"
        
        doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30
        )
        elements.append(Paragraph(f"Reporte de Pago - {nombre_asistente}", title_style))
        
        # Información general
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20
        )
        elements.append(Paragraph(f"Fecha de pago: {fecha_formateada}", info_style))
        if detalle:
            elements.append(Paragraph(f"Detalle: {detalle}", info_style))
        
        # Tabla de sesiones
        sesiones = [detalle for detalle in detalles_pago if detalle[0] == 'SESION']
        if sesiones:
            elements.append(Paragraph("Detalle de Sesiones:", styles['Heading2']))
            data = [['Paciente', 'Tratamiento', 'Fecha', 'Sesión', 'Monto']]
            for sesion in sesiones:
                fecha = datetime.strptime(sesion[3], '%Y-%m-%d').strftime('%d-%m-%Y')
                data.append([
                    sesion[1],  # Paciente
                    sesion[2],  # Tratamiento
                    fecha,      # Fecha
                    f"Sesión {sesion[4]}", # Número de sesión
                    f"${sesion[5]:.2f}"    # Monto
                ])
            
            table = Table(data, colWidths=[2*inch, 2*inch, 1.2*inch, 0.8*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        # Tabla de ventas
        ventas = [detalle for detalle in detalles_pago if detalle[0] == 'VENTA']
        if ventas:
            elements.append(Paragraph("Detalle de Ventas:", styles['Heading2']))
            data = [['Paciente', 'Tratamiento', 'Fecha', 'Comisión']]
            for venta in ventas:
                fecha = datetime.strptime(venta[3], '%Y-%m-%d').strftime('%d-%m-%Y')
                data.append([
                    venta[1],   # Paciente
                    venta[2],   # Tratamiento
                    fecha,      # Fecha
                    f"${venta[5]:.2f}"  # Monto
                ])
            
            table = Table(data, colWidths=[2*inch, 2*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))
        
        # Total
        elements.append(Paragraph(f"Total pagado: ${total_pendiente:.2f}", 
                    ParagraphStyle('Total', 
                                parent=styles['Heading2'],
                                fontSize=14,
                                alignment=2)))
        
        doc.build(elements)
        return nombre_archivo

    def limpiar_campos(self):
        self.nombre_entry.delete(0, 'end')
        self.telefono_entry.delete(0, 'end')

    def realizar_pago(self, asistente_id, tratamiento_id):
        # Ventana emergente para ingresar detalles del pago
        monto_pagado = simpledialog.askfloat("Pago", "Ingrese el monto pagado:")
        if monto_pagado is None:
            return  # Cancelado

        detalle = simpledialog.askstring("Detalle", "Ingrese un detalle del pago (opcional):")
        if detalle is None:
            detalle = ""

        # Llamar a la función de pago
        self.pagar_asistente(asistente_id, tratamiento_id, monto_pagado, detalle)
 

    def volver_menu_principal(self):
        self.main_system.show_main_menu()