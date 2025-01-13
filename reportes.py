import customtkinter as ctk
from tkinter import filedialog, ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import openpyxl

class ReportesManagement:
    def __init__(self, root, main_system):
        self.root = root
        self.main_system = main_system

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title = ctk.CTkLabel(main_frame, text="Reportes de Tratamientos", font=("Helvetica", 36, "bold"))
        title.pack(pady=(50, 40))

        # Marco de filtros
        filters_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        filters_frame.pack(fill="x", padx=40, pady=10)

        # Primera fila: Fechas
        date_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)
        
        # Contenedor izquierdo para "Desde"
        desde_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        desde_frame.pack(side="left", expand=True)
        ctk.CTkLabel(desde_frame, text="Desde:", font=("Helvetica", 12)).pack(side="left")
        self.fecha_inicio = DateEntry(desde_frame, width=12, background='black',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_inicio.pack(side="left", padx=(10, 0))

        # Contenedor derecho para "Hasta"
        hasta_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        hasta_frame.pack(side="left", expand=True)
        ctk.CTkLabel(hasta_frame, text="Hasta:", font=("Helvetica", 12)).pack(side="left", padx=(20, 0))
        self.fecha_fin = DateEntry(hasta_frame, width=12, background='black',
                                foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.fecha_fin.pack(side="left", padx=(10, 0))

        # Segunda fila: Esteticista y Tratamiento
        filter_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=10)
        
        # Contenedor izquierdo para Esteticista
        esteticista_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        esteticista_frame.pack(side="left", expand=True)
        ctk.CTkLabel(esteticista_frame, text="Esteticista:", font=("Helvetica", 12), width=80).pack(side="left")
        self.asistentes = self.get_asistentes()
        self.asistente_var = ctk.StringVar(value="Todos")
        asistente_combo = ctk.CTkComboBox(esteticista_frame, values=["Todos"] + [a[1] for a in self.asistentes], 
                                        variable=self.asistente_var, width=200)
        asistente_combo.pack(side="left", padx=(10, 0))

        # Contenedor derecho para Tratamiento
        tratamiento_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        tratamiento_frame.pack(side="left", expand=True)
        ctk.CTkLabel(tratamiento_frame, text="Tratamiento:", font=("Helvetica", 12), width=80).pack(side="left", padx=(20, 0))
        self.tratamientos = self.get_tratamientos()
        self.tratamiento_var = ctk.StringVar(value="Todos")
        tratamiento_combo = ctk.CTkComboBox(tratamiento_frame, values=["Todos"] + [t[1] for t in self.tratamientos], 
                                        variable=self.tratamiento_var, width=200)
        tratamiento_combo.pack(side="left", padx=(10, 0))

        # Botones
        btn_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        btn_style = {
            "width": 150,
            "height": 35,
            "corner_radius": 8,
            "fg_color": "#191919",
            "hover_color": "#676767",
        }
        close_btn_style = btn_style.copy()
        close_btn_style.update(
            {
                "fg_color": "#e74c3c",
                "hover_color": "#c0392b",
                "border_color": "#c0392b",
            }
        )

        ctk.CTkButton(btn_frame, text="Buscar", command=self.actualizar_reporte, **btn_style).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Exportar a Excel", command=self.exportar_a_excel, **btn_style).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Exportar a PDF", command=self.exportar_a_pdf, **btn_style).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Volver al menú principal", command=self.volver_menu_principal, **close_btn_style).pack(side="left", padx=10)

        assigned_treatments_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", border_width=1)
        assigned_treatments_frame.pack(fill="both", expand=True, padx=40, pady=(20, 10))

        assigned_columns = ("ID", "Fecha", "Paciente", "Tratamiento Asignado", "Monto")
        self.assigned_tree = ttk.Treeview(assigned_treatments_frame, columns=assigned_columns, show="headings", style="Treeview")
        
        assigned_y_scroll = ttk.Scrollbar(assigned_treatments_frame, orient="vertical", command=self.assigned_tree.yview)
        assigned_x_scroll = ttk.Scrollbar(assigned_treatments_frame, orient="horizontal", command=self.assigned_tree.xview)
        
        self.assigned_tree.configure(yscrollcommand=assigned_y_scroll.set, xscrollcommand=assigned_x_scroll.set)
        
        assigned_y_scroll.pack(side="right", fill="y")
        assigned_x_scroll.pack(side="bottom", fill="x")
        self.assigned_tree.pack(fill="both", expand=True)

        for col in assigned_columns:
            self.assigned_tree.heading(col, text=col)
            self.assigned_tree.column(col, width=150, minwidth=100)

        self.assigned_tree.bind("<<TreeviewSelect>>", self.on_assigned_tree_select)

        # Tabla de resultados actuales
        results_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", border_width=1)
        results_frame.pack(fill="both", expand=True, padx=40, pady=(20, 10))

        columns = ("Fecha", "Paciente", "Tratamiento", "Esteticista", "Vendedor", "Sesión", 
                "Monto Total", "Monto Esteticista", "Monto Vendedor", "Monto Neto")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", style="Treeview")
        
        y_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=150, minwidth=100)

        # Resumen
        summary_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF", height=50)
        summary_frame.pack(fill="x", padx=40, pady=10)

        self.total_tratamientos_label = ctk.CTkLabel(summary_frame, text="Total tratamientos: 0", 
                                            font=("Helvetica", 12, "bold"))
        self.total_tratamientos_label.pack(side="left", padx=20)

        self.total_sesiones_label = ctk.CTkLabel(summary_frame, text="Total sesiones: 0", 
                                            font=("Helvetica", 12, "bold"))
        self.total_sesiones_label.pack(side="left", padx=20)

        self.total_monto_label = ctk.CTkLabel(summary_frame, text="Total montos: $0.00", 
                                            font=("Helvetica", 12, "bold"))
        self.total_monto_label.pack(side="left", padx=20)

    
    
    def get_asistentes(self):
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM asistentes ORDER BY nombre")
        asistentes = c.fetchall()
        conn.close()
        return asistentes

    def get_tratamientos(self):
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM tratamientos ORDER BY nombre")
        tratamientos = c.fetchall()
        conn.close()
        return tratamientos

    def actualizar_reporte(self):
        for item in self.assigned_tree.get_children():
            self.assigned_tree.delete(item)
        
        try:
            fecha_inicio = self.fecha_inicio.get_date().strftime('%Y-%m-%d')
            fecha_fin = self.fecha_fin.get_date().strftime('%Y-%m-%d')
        except Exception as e:
            messagebox.showerror("Error", "Por favor seleccione fechas válidas")
            return

        # Actualizar tabla de tratamientos asignados
        assigned_query = """
            SELECT 
                ta.id,
                ta.fecha_asignacion,
                p.nombre AS paciente,
                t.nombre AS tratamiento,
                ta.costo_total AS monto
            FROM tratamientos_asignados ta
            JOIN pacientes p ON ta.paciente_id = p.id
            JOIN tratamientos t ON ta.tratamiento_id = t.id
            WHERE ta.fecha_asignacion BETWEEN ? AND ?
        """
        assigned_params = [fecha_inicio, fecha_fin]

        if self.asistente_var.get() != "Todos":
            assigned_query += " AND ta.asistente_id = (SELECT id FROM asistentes WHERE nombre = ?)"
            assigned_params.append(self.asistente_var.get())

        if self.tratamiento_var.get() != "Todos":
            assigned_query += " AND t.nombre = ?"
            assigned_params.append(self.tratamiento_var.get())

        assigned_query += " ORDER BY ta.fecha_asignacion DESC"

        try:
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            c.execute(assigned_query, assigned_params)
            assigned_resultados = c.fetchall()
            conn.close()

            if assigned_resultados:
                for row in assigned_resultados:
                    self.assigned_tree.insert("", "end", values=row)
                
                # Actualizar etiquetas de resumen
                total_tratamientos = len(assigned_resultados)
                total_monto = sum(row[4] for row in assigned_resultados)
                self.total_tratamientos_label.configure(text=f"Total tratamientos: {total_tratamientos}")
                self.total_monto_label.configure(text=f"Total montos: ${total_monto:.2f}")
            else:
                messagebox.showinfo("No hay resultados", "No se encontraron tratamientos asignados en ese periodo.")
                self.total_tratamientos_label.configure(text="Total tratamientos: 0")
                self.total_monto_label.configure(text="Total montos: $0.00")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.total_tratamientos_label.configure(text="Total tratamientos: 0")
            self.total_monto_label.configure(text="Total montos: $0.00")

    def on_assigned_tree_select(self, event):
        selected_item = self.assigned_tree.selection()
        if not selected_item:
            return

        item = self.assigned_tree.item(selected_item)
        tratamiento_asignado_id = item["values"][0]

        for item in self.tree.get_children():
            self.tree.delete(item)

        query = """
            SELECT 
                sr.fecha_sesion,
                p.nombre AS paciente,
                t.nombre AS tratamiento,
                a.nombre AS asistente,
                COALESCE(v.nombre, 'No aplica') AS vendedor,
                sr.numero_sesion,
                ta.costo_total AS monto_total,
                (ta.costo_total * ta.porcentaje_asistente / 100.0 / ta.sesiones_asignadas) AS monto_asistente,
                CASE 
                    WHEN ta.vendedor_id IS NOT NULL THEN
                        (ta.costo_total * ta.porcentaje_vendedor / 100.0 / ta.sesiones_asignadas)
                    ELSE 0
                END AS monto_vendedor,
                (ta.costo_total / ta.sesiones_asignadas) - 
                (ta.costo_total * ta.porcentaje_asistente / 100.0 / ta.sesiones_asignadas) - 
                CASE 
                    WHEN ta.vendedor_id IS NOT NULL THEN
                        (ta.costo_total * ta.porcentaje_vendedor / 100.0 / ta.sesiones_asignadas)
                    ELSE 0
                END AS monto_neto
            FROM sesiones_realizadas sr
            JOIN tratamientos_asignados ta ON sr.tratamiento_asignado_id = ta.id
            JOIN pacientes p ON ta.paciente_id = p.id
            JOIN tratamientos t ON ta.tratamiento_id = t.id
            JOIN asistentes a ON ta.asistente_id = a.id
            LEFT JOIN asistentes v ON ta.vendedor_id = v.id
            WHERE sr.tratamiento_asignado_id = ?
        """
        params = [tratamiento_asignado_id]

        try:
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            c.execute(query, params)
            resultados = c.fetchall()
            conn.close()

            if resultados:
                for row in resultados:
                    self.tree.insert("", "end", values=row)
            else:
                messagebox.showinfo("No hay resultados", "No se encontraron sesiones realizadas para el tratamiento seleccionado.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def exportar_a_excel(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Files", "*.xlsx")],
                title="Guardar Reporte de Tratamientos"
            )

            if not file_path:
                return

            # Obtener datos de la primera tabla
            rows = [self.assigned_tree.item(row)["values"] for row in self.assigned_tree.get_children()]
            columns = ["ID", "Fecha", "Paciente", "Tratamiento Asignado", "Monto"]

            # Crear DataFrame
            df = pd.DataFrame(rows, columns=columns)

            # Crear un objeto Excel Writer
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Reporte', index=False, startrow=1)
                
                # Obtener el objeto workbook y worksheet
                workbook = writer.book
                worksheet = writer.sheets['Reporte']

                # Formatos
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D9D9D9',
                    'border': 1,
                    'font_size': 11
                })

                cell_format = workbook.add_format({
                    'text_wrap': True,
                    'border': 1,
                    'font_size': 10
                })

                money_format = workbook.add_format({
                    'num_format': '$#,##0.00',
                    'border': 1,
                    'font_size': 10
                })

                # Añadir título
                title_format = workbook.add_format({
                    'bold': True,
                    'font_size': 14,
                    'align': 'center'
                })
                worksheet.merge_range('A1:E1', 'Reporte de Tratamientos Asignados', title_format)

                # Aplicar formatos a las columnas
                for idx, col in enumerate(columns):
                    worksheet.write(1, idx, col, header_format)
                    if 'Monto' in col:
                        worksheet.set_column(idx, idx, 15, money_format)
                    else:
                        worksheet.set_column(idx, idx, 15, cell_format)

                # Autoajustar columnas
                for idx, col in enumerate(columns):
                    worksheet.set_column(idx, idx, max(len(col) + 2, 15))

            messagebox.showinfo("Exportación exitosa", 
                            "El reporte fue exportado a Excel con éxito:\n" + file_path)
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    def exportar_a_pdf(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Guardar Reporte de Tratamientos"
            )

            if not file_path:
                return

            # Configuración inicial del PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=(800, 600),
                rightMargin=30,
                leftMargin=30,
                topMargin=30,
                bottomMargin=30
            )

            # Estilos
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centro
            )

            # Contenido del PDF
            elements = []
            
            # Título
            title = Paragraph("Reporte de Tratamientos Asignados", title_style)
            elements.append(title)

            # Datos de la tabla
            headers = ["ID", "Fecha", "Paciente", "Tratamiento Asignado", "Monto"]
            
            data = [headers]  # Primera fila con encabezados
            total_monto = 0.0  # Inicializar el monto total
            for item in self.assigned_tree.get_children():
                row = self.assigned_tree.item(item)["values"]
                # Formatear montos a formato de moneda
                formatted_row = []
                for idx, value in enumerate(row):
                    if 'Monto' in headers[idx]:
                        monto = float(value)
                        total_monto += monto  # Sumar al monto total
                        formatted_row.append("${:.2f}".format(monto))
                    else:
                        formatted_row.append(str(value))
                data.append(formatted_row)

            # Agregar fila de total
            total_row = ["", "", "", "Total", "${:.2f}".format(total_monto)]
            data.append(total_row)

            # Estilo de la tabla
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
            ])

            # Crear tabla
            table = Table(data, repeatRows=1)
            table.setStyle(table_style)
            
            # Ajustar ancho de columnas
            col_widths = [40, 80, 80, 120, 70]
            table._argW = col_widths
            
            elements.append(table)
            
            # Generar PDF
            doc.build(elements)

            messagebox.showinfo("Exportación exitosa", 
                            "El reporte fue exportado a PDF con éxito:\n" + file_path)
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    def volver_menu_principal(self):
        self.main_system.show_main_menu()