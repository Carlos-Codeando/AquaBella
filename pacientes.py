from unittest import result
import customtkinter as ctk
from tkinter import ttk, Tk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry


class PacientesManagement:
    def __init__(self, root, main_system):
        self.root = root
        self.setup_database()
        self.main_system = main_system
        self.componentes_data = {}


        
    def filtrar_pacientes(self, *args):
        search_term = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        # Búsqueda en tiempo real que incluye tratamientos
        c.execute("""
            SELECT p.*, GROUP_CONCAT(t.nombre) as tratamientos
            FROM pacientes p
            LEFT JOIN tratamientos_asignados ta ON p.id = ta.paciente_id
            LEFT JOIN tratamientos t ON ta.tratamiento_id = t.id
            WHERE LOWER(p.nombre) LIKE ? OR 
                  LOWER(p.telefono) LIKE ? OR 
                  LOWER(p.correo) LIKE ? OR
                  LOWER(COALESCE(t.nombre, '')) LIKE ?
            GROUP BY p.id
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        for row in c.fetchall():
            self.tree.insert("", "end", values=row)
        
        conn.close()

    def setup_database(self):
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        # Asegurarse que existan todas las tablas necesarias
        c.execute("""
            CREATE TABLE IF NOT EXISTS tratamientos_asignados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER,
                tratamiento_id INTEGER,
                asistente_id INTEGER,
                porcentaje_asistente REAL,
                sesiones_totales INTEGER,
                sesiones_restantes INTEGER,
                costo_total REAL,
                fecha_asignacion DATE,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (tratamiento_id) REFERENCES tratamientos (id),
                FOREIGN KEY (asistente_id) REFERENCES asistentes (id)
            )
        """)
        conn.commit()
        conn.close()
        

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title = ctk.CTkLabel(main_frame, text="Control de Pacientes", font=("Helvetica", 36, "bold"))
        title.pack(pady=(50,40))

        # Frame de búsqueda
        search_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        search_frame.pack(fill="x",  padx=20, pady=10)
        btn_style = {"width": 120, "height": 32, "corner_radius": 8,
                    "fg_color": "#191919", "hover_color": "#676767"}
        
        ctk.CTkLabel(search_frame, text="Buscar:").pack(side="left", padx=20)
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=400)
        search_entry.pack(side="left", padx=5)

        # Agregar botón de búsqueda
        btn_buscar = ctk.CTkButton(search_frame, text="Buscar", command=self.buscar_pacientes, **btn_style)
        btn_buscar.pack(side="left", padx=5)


        # Formulario de pacientes
        form_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        form_frame.pack(fill="x", padx=20, pady=10)

        # Crear dos columnas para los campos
        left_column = ctk.CTkFrame(form_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(40, 20))
        right_column = ctk.CTkFrame(form_frame, fg_color="transparent")
        right_column.pack(side="left", fill="both", expand=True, padx=(20, 40))

        # Distribuir los campos en dos columnas
        labels = ["Nombre:", "Sexo:", "Fecha de Nacimiento:", "Edad:", "Teléfono:", "Correo:"]
        self.paciente_entries = {}
        self.edad_entry = None

        def calcular_edad(event=None):
            try:
                fecha_nacimiento = self.paciente_entries["Fecha de Nacimiento:"].get_date()
                hoy = datetime.now()
                edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
                if self.edad_entry:
                    self.edad_entry.configure(state="normal")  # Permitir la edición para actualizar el valor
                    self.edad_entry.delete(0, 'end')
                    self.edad_entry.insert(0, str(edad))
                    self.edad_entry.configure(state="readonly")  # Volver a deshabilitar la edición
            except Exception as e:
                print(f"Error al calcular la edad: {e}")  # Mostrar el error en consola sin interr

        # Primera columna
        for label in labels[:3]:
            row = ctk.CTkFrame(left_column, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=label, font=("Helvetica", 12), width=120).pack(side="left")
            if label == "Sexo:":
                self.paciente_entries[label] = ctk.CTkComboBox(row, values=["Masculino", "Femenino"],
                                                            width=200,
                                                            height=32)
            elif label == "Fecha de Nacimiento:":
                # Configuración del DateEntry con año base
                self.paciente_entries[label] = DateEntry(row, width=20, 
                                                    background='black',
                                                    foreground='white', 
                                                    borderwidth=2,
                                                    year=1990,  # Año base razonable
                                                    date_pattern='dd/mm/yyyy')  # Patrón de fecha
                self.paciente_entries[label].bind("<<DateEntrySelected>>", calcular_edad)
            else:
                self.paciente_entries[label] = ctk.CTkEntry(row, width=200, height=32,
                                                        placeholder_text=f"Ingrese {label.lower()[:-1]}")
            self.paciente_entries[label].pack(side="left", padx=(10, 0))

        # Segunda columna
        for label in labels[3:]:
            row = ctk.CTkFrame(right_column, fg_color="transparent")
            row.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row, text=label, font=("Helvetica", 12), width=120).pack(side="left")
            self.paciente_entries[label] = ctk.CTkEntry(row, width=200, height=32,
                                                    placeholder_text=f"Ingrese {label.lower()[:-1]}")
            if label == "Edad:":
                self.edad_entry = self.paciente_entries[label]
                self.paciente_entries[label].configure(state="readonly")
            self.paciente_entries[label].pack(side="left", padx=(10, 0))

        # Botones de acción en una barra lateral derecha
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", padx=(20, 40), pady=(20, 40)) 

        btn_style = {
            "height": 40,
            "corner_radius": 8,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white"
        }
        close_btn_style = btn_style.copy()
        close_btn_style.update(
            {
                "fg_color": "#e74c3c",
                "hover_color": "#c0392b",
                "border_color": "#c0392b",
            }
        )
        add_btn_style = btn_style.copy()
        add_btn_style.update(
            {
                "fg_color": "#3b83bd",
                "hover_color": "#275c87",
                "border_width":0,
            }
        )
        # Botones en columna vertical
        buttons = [
            ("Agregar", self.agregar_paciente),
            ("Modificar", self.modificar_paciente),
            ("Eliminar", self.eliminar_paciente),
            ("Limpiar", self.limpiar_formulario),
        ]

        for text, command in buttons:
            ctk.CTkButton(btn_frame, text=text, command=command, **btn_style).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Asignar Tratamiento", command=self.mostrar_ventana_asignar_tratamiento, **add_btn_style).pack(side="left", padx=5)    
        ctk.CTkButton(btn_frame, text="Volver al menú principal", command=self.volver_menu_principal, **close_btn_style).pack(side="left", padx=5)
            
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
            background=[("selected", "#D3D3D3")],  # Fondo gris claro al seleccionar
            foreground=[("selected", "#000000")],  # Texto negro al seleccionar
        )
        
        # Tabla de pacientes
        table_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF" , border_width=1)
        table_frame.pack(fill="both", expand=True, pady=(10, 20), padx= 40)

        columns = ("ID", "Nombre", "Sexo", "Fecha Nac.", "Edad", "Teléfono", "Correo", "Tratamientos")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")

        column_widths = {"ID" :1, "Nombre": 150, "Sexo": 50, "Fecha Nac.": 100, "Edad": 50, "Teléfono": 100, "Correo":150, "Tratamientos": 100}
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
        
        self.tree.bind("<Double-1>", self.mostrar_opciones_paciente)
        self.tree.bind("<ButtonRelease-1>", self.cargar_datos_paciente)
    

        self.actualizar_lista_pacientes()

    def buscar_pacientes(self):
        # Obtener el nombre a buscar desde la variable de búsqueda
        nombre_buscado = self.search_var.get().strip()

        # Limpiar el Treeview antes de mostrar los resultados
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Si la búsqueda está vacía, se muestran todos los pacientes
        if not nombre_buscado:
            self.actualizar_lista_pacientes()
            return

        # Conexión a la base de datos y búsqueda de coincidencias
        try:
            conn = sqlite3.connect("spa_database.db")
            c = conn.cursor()

            # Consulta SQL para buscar nombres que contengan la cadena ingresada
            c.execute("SELECT * FROM pacientes WHERE nombre LIKE ?", ('%' + nombre_buscado + '%',))
            resultados = c.fetchall()

            # Insertar los resultados en el Treeview
            for row in resultados:
                self.tree.insert("", "end", values=row)

            conn.close()
        except Exception as e:
            print("Error al buscar pacientes:", e)

    def actualizar_lista_pacientes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        c.execute("""
            SELECT p.*, GROUP_CONCAT(t.nombre) as tratamientos
            FROM pacientes p
            LEFT JOIN tratamientos_asignados ta ON p.id = ta.paciente_id
            LEFT JOIN tratamientos t ON ta.tratamiento_id = t.id
            GROUP BY p.id
        """)
        
        for row in c.fetchall():
            self.tree.insert("", "end", values=row)
            
        conn.close()

    def cargar_datos_paciente(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item = self.tree.item(selected_item[0])
        valores = item['values']
        
        campos = ["ID:", "Nombre:", "Sexo:", "Fecha de Nacimiento:", "Edad:", "Teléfono:", "Correo:"]
        for campo, valor in zip(campos, valores):
            if campo in self.paciente_entries:
                if isinstance(self.paciente_entries[campo], ctk.CTkComboBox):
                    self.paciente_entries[campo].set(valor)
                elif isinstance(self.paciente_entries[campo], DateEntry):
                    try:
                        fecha = datetime.strptime(valor, '%Y-%m-%d')
                        self.paciente_entries[campo].set_date(fecha)
                    except ValueError:
                        pass
                else:
                    self.paciente_entries[campo].delete(0, 'end')
                    self.paciente_entries[campo].insert(0, str(valor))

    def validar_datos_paciente(self):
        campos_requeridos = ["Nombre:", "Sexo:", "Fecha de Nacimiento:", "Edad:", "Teléfono:"]
        for campo in campos_requeridos:
            valor = self.paciente_entries[campo].get()
            if not valor:
                messagebox.showerror("Error", f"El campo {campo.strip(':')} es requerido")
                return False
                
        try:
            edad = int(self.paciente_entries["Edad:"].get())
            if edad < 0 or edad > 120:
                messagebox.showerror("Error", "La edad debe estar entre 15 y 120 años")
                return False
        except ValueError:
            messagebox.showerror("Error", "La edad debe ser un número válido")
            return False
            
        return True

    def get_tratamientos(self):
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        if self.tipo_var.get() == "Promoción":
            c.execute("SELECT nombre FROM tratamientos WHERE es_promocion = 1")
        else:
            c.execute("SELECT nombre FROM tratamientos WHERE es_promocion = 0")
        tratamientos = [row[0] for row in c.fetchall()]
        conn.close()
        return tratamientos


    def get_asistentes(self):
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        c.execute("SELECT nombre FROM asistentes")
        asistentes = [row[0] for row in c.fetchall()]
        conn.close()
        return asistentes

    def limpiar_formulario(self):
        for entry in self.paciente_entries.values():
            if isinstance(entry, (ctk.CTkEntry, DateEntry)):
                entry.delete(0, 'end')
            elif isinstance(entry, ctk.CTkComboBox):
                entry.set("")

    def agregar_paciente(self):
        if not self.validar_datos_paciente():
            return
            
        try:
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            
            data = {
                "nombre": self.paciente_entries["Nombre:"].get(),
                "sexo": self.paciente_entries["Sexo:"].get(),
                "fecha_nacimiento": self.paciente_entries["Fecha de Nacimiento:"].get(),
                "edad": self.paciente_entries["Edad:"].get(),
                "telefono": self.paciente_entries["Teléfono:"].get(),
                "correo": self.paciente_entries["Correo:"].get(),
            }
            
            c.execute("""
                INSERT INTO pacientes (nombre, sexo, fecha_nacimiento, edad, telefono, correo)
                VALUES (:nombre, :sexo, :fecha_nacimiento, :edad, :telefono, :correo)
            """, data)
            
            conn.commit()
            conn.close()
            
            self.actualizar_lista_pacientes()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Paciente agregado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el paciente: {e}")

    def modificar_paciente(self):
        if not self.tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un paciente para modificar")
            return
        # Obtener el ID directamente del item seleccionado en el tree
        selected_item = self.tree.selection()[0]
        paciente_id = self.tree.item(selected_item)['values'][0]  # Asumiendo que el ID es la primera columna
        
        if not self.validar_datos_paciente():
            return
            
        try:
            
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            
            data = {
                "id": paciente_id,
                "nombre": self.paciente_entries["Nombre:"].get(),
                "sexo": self.paciente_entries["Sexo:"].get(),
                "fecha_nacimiento": self.paciente_entries["Fecha de Nacimiento:"].get(),
                "edad": self.paciente_entries["Edad:"].get(),
                "telefono": self.paciente_entries["Teléfono:"].get(),
                "correo": self.paciente_entries["Correo:"].get(),
            }
            
            c.execute("""
                UPDATE pacientes 
                SET nombre=:nombre, sexo=:sexo, fecha_nacimiento=:fecha_nacimiento,
                    edad=:edad, telefono=:telefono, correo=:correo
                WHERE id=:id
            """, data)
            
            conn.commit()
            conn.close()
            
            self.actualizar_lista_pacientes()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Paciente modificado correctamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el paciente: {e}")

    def eliminar_paciente(self):
        if not self.tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un paciente para eliminar")
            return
            
        if not messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este paciente?"):
            return
            
        try:
            selected_item = self.tree.selection()[0]
            paciente_id = self.tree.item(selected_item)['values'][0]
                
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            
            # Verificar si el paciente tiene tratamientos asignados
            c.execute("SELECT COUNT(*) FROM tratamientos_asignados WHERE paciente_id = ?", 
                     (paciente_id,))
            if c.fetchone()[0] > 0:
                messagebox.showerror("Error", 
                    "No se puede eliminar el paciente porque tiene tratamientos asignados")
                return
            
            c.execute("DELETE FROM pacientes WHERE id = ?", (paciente_id,))
            conn.commit()
            conn.close()
            
            self.actualizar_lista_pacientes()
            self.limpiar_formulario()
            messagebox.showinfo("Éxito", "Paciente eliminado correctamente")
             
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el paciente: {e}")
            
    def mostrar_opciones_paciente(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item = self.tree.item(selected_item[0])
        # Aquí puedes hacer lo que desees con la selección
        valores = item['values']
        messagebox.showinfo("Información del paciente", f"Se seleccionó al paciente: {valores[1]}")
    
        
    def mostrar_ventana_asignar_tratamiento(self):
        if not self.tree.selection():
            messagebox.showwarning("Advertencia", "Por favor seleccione un paciente para asignar tratamiento")
            return
        
        # Obtener el ID directamente del item seleccionado en el TreeView
        selected_item = self.tree.selection()[0]
        valores = self.tree.item(selected_item)['values']
        paciente_id = valores[0] 
        
        
        if not paciente_id:
            messagebox.showerror("Error", "No se pudo obtener el ID del paciente")
            return

        
        # Ventana principal
        self.ventana = ctk.CTkToplevel(self.root)
        self.ventana.title("Asignar Tratamiento")
        self.ventana.geometry("800x800")
        self.ventana.wm_attributes("-topmost", True)
        
        # Obtener el nombre del paciente de los valores del TreeView
        nombre_paciente = valores[1]  # El nombre es el segundo valor en la lista
        ctk.CTkLabel(self.ventana, text=f"Asignar tratamiento a: {nombre_paciente}", 
                    font=("Helvetica", 20, "bold")).pack(pady=10)
        
        # Frame tipo de asignación
        frame_tipo = ctk.CTkFrame(self.ventana)
        frame_tipo.pack(fill="x", padx=20, pady=5)
        
        self.tipo_var = ctk.StringVar(value="Tratamiento")
        tipo_radio_1 = ctk.CTkRadioButton(frame_tipo, text="Tratamiento", 
                                        variable=self.tipo_var, value="Tratamiento")
        tipo_radio_2 = ctk.CTkRadioButton(frame_tipo, text="Promoción", 
                                        variable=self.tipo_var, value="Promoción")
        tipo_radio_1.pack(side="left", padx=20)
        tipo_radio_2.pack(side="left", padx=20)
        
        
        # Frame selección tratamiento
        frame_tratamiento = ctk.CTkFrame(self.ventana)
        frame_tratamiento.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_tratamiento, text="Seleccione:").pack(side="left")

        self.tratamiento_var = ctk.StringVar()
        self.tratamiento_entry = ctk.CTkEntry(frame_tratamiento, textvariable=self.tratamiento_var, state="readonly")
        self.tratamiento_entry.pack(side="left", fill="x", expand=True, padx=10)

        btn_seleccionar_tratamiento = ctk.CTkButton(frame_tratamiento, text="Seleccionar", command=self.abrir_seleccion_tratamiento, fg_color="black",
        hover_color="#1f6aa8")
        btn_seleccionar_tratamiento.pack(side="left", padx=10)

        # Frame para tratamientos normales
        self.frame_tratamiento_normal = ctk.CTkFrame(self.ventana)
        self.frame_tratamiento_normal.pack(fill="x", padx=20, pady=5)

        
        # Costo
        frame_costo = ctk.CTkFrame(self.frame_tratamiento_normal)
        frame_costo.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_costo, text="Costo:").pack(side="left")
        self.costo_entry = ctk.CTkEntry(frame_costo)
        self.costo_entry.pack(side="right")
        
        # Sesiones a asignar
        frame_sesiones = ctk.CTkFrame(self.frame_tratamiento_normal)
        frame_sesiones.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_sesiones, text="Sesiones a asignar:").pack(side="left")
        self.sesiones_entry = ctk.CTkEntry(frame_sesiones)
        self.sesiones_entry.pack(side="right")

        # Sesiones a pagar
        frame_sesiones_pagar = ctk.CTkFrame(self.frame_tratamiento_normal)
        frame_sesiones_pagar.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_sesiones_pagar, text="Sesiones a realizar:").pack(side="left")
        self.sesiones_pagar_entry = ctk.CTkEntry(frame_sesiones_pagar)
        self.sesiones_pagar_entry.pack(side="right")

        # Frame para vendedor
        frame_vendedor = ctk.CTkFrame(self.frame_tratamiento_normal)
        frame_vendedor.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_vendedor, text="¿Hay vendedor?").pack(side="left")
        self.hay_vendedor_var = ctk.BooleanVar(value=False)
        hay_vendedor_check = ctk.CTkCheckBox(frame_vendedor, text="", 
                                            variable=self.hay_vendedor_var)
        hay_vendedor_check.pack(side="right")

        # Frame selección vendedor
        self.frame_seleccion_vendedor = ctk.CTkFrame(self.frame_tratamiento_normal)
        ctk.CTkLabel(self.frame_seleccion_vendedor, text="Vendedor:").pack(side="left")
        self.vendedor_var = ctk.StringVar()
        self.vendedor_combo = ctk.CTkComboBox(self.frame_seleccion_vendedor, 
                                            variable=self.vendedor_var,
                                            values=self.get_asistentes())
        self.vendedor_combo.pack(side="right")

        # Porcentaje vendedor
        self.frame_porcentaje_vendedor = ctk.CTkFrame(self.frame_tratamiento_normal)
        ctk.CTkLabel(self.frame_porcentaje_vendedor, text="Porcentaje vendedor:").pack(side="left")
        self.porcentaje_vendedor_entry = ctk.CTkEntry(self.frame_porcentaje_vendedor)
        self.porcentaje_vendedor_entry.pack(side="right")

        # Asistente
        frame_asistente = ctk.CTkFrame(self.frame_tratamiento_normal)
        frame_asistente.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_asistente, text="Esteticista:").pack(side="left")
        self.asistente_var = ctk.StringVar()
        self.asistente_combo = ctk.CTkComboBox(frame_asistente,
                                            variable=self.asistente_var,
                                            values=self.get_asistentes())
        self.asistente_combo.pack(side="right")

        # Porcentaje asistente
        frame_porcentaje = ctk.CTkFrame(self.frame_tratamiento_normal)
        frame_porcentaje.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_porcentaje, text="Porcentaje Esteticista:").pack(side="left")
        self.porcentaje_entry = ctk.CTkEntry(frame_porcentaje)
        self.porcentaje_entry.pack(side="right")

        # Frame para promociones
        self.frame_promocion = ctk.CTkFrame(self.ventana)

            # Estado de pago
        frame_estado_pago = ctk.CTkFrame(self.frame_promocion)
        frame_estado_pago.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_estado_pago, text="Pagado por adelantado:").pack(side="left")
        self.pagado_adelantado_var = ctk.BooleanVar(value=False)
        pagado_adelantado_check = ctk.CTkCheckBox(frame_estado_pago, text="", 
                                                    variable=self.pagado_adelantado_var)
        pagado_adelantado_check.pack(side="right")

        # Vendedor para promociones
        frame_vendedor_promo = ctk.CTkFrame(self.frame_promocion)
        frame_vendedor_promo.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_vendedor_promo, text="¿Hay vendedor?").pack(side="left")
        self.hay_vendedor_promo_var = ctk.BooleanVar(value=False)
        hay_vendedor_promo_check = ctk.CTkCheckBox(frame_vendedor_promo, text="", 
                                                    variable=self.hay_vendedor_promo_var)
        hay_vendedor_promo_check.pack(side="right")

        # Frame para selección de esteticistas por componente
        self.frame_esteticistas_componentes = ctk.CTkFrame(self.frame_promocion)
        self.frame_esteticistas_componentes.pack(fill="x", padx=20, pady=5)

        # Selección vendedor promoción
        self.frame_seleccion_vendedor_promo = ctk.CTkFrame(self.frame_promocion)
        ctk.CTkLabel(self.frame_seleccion_vendedor_promo, text="Vendedor:").pack(side="left")
        self.vendedor_promo_var = ctk.StringVar()
        self.vendedor_promo_combo = ctk.CTkComboBox(self.frame_seleccion_vendedor_promo, 
                                                    variable=self.vendedor_promo_var,
                                                    values=self.get_asistentes())
        self.vendedor_promo_combo.pack(side="right")

        # Porcentaje vendedor promoción
        self.frame_porcentaje_vendedor_promo = ctk.CTkFrame(self.frame_promocion)
        ctk.CTkLabel(self.frame_porcentaje_vendedor_promo, text="Porcentaje vendedor:").pack(side="left")
        self.porcentaje_vendedor_promo_entry = ctk.CTkEntry(self.frame_porcentaje_vendedor_promo)
        self.porcentaje_vendedor_promo_entry.pack(side="right")



        # Fecha primera sesión
        frame_fecha = ctk.CTkFrame(self.ventana)
        frame_fecha.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(frame_fecha, text="Fecha primera sesión:").pack(side="left")
        self.fecha_primera_sesion = DateEntry(frame_fecha, width=12, background='black',
                                            foreground='white', borderwidth=2,
                                            date_pattern='yyyy-mm-dd')
        self.fecha_primera_sesion.pack(side="right")

        # Frame resultados
        self.frame_resultados = ctk.CTkFrame(self.ventana)
        self.frame_resultados.pack(fill="x", padx=20, pady=10)

        # Etiquetas resultados
        self.total_label = ctk.CTkLabel(self.frame_resultados, text="Total: $0.00")
        self.total_label.pack(pady=2)
        self.pagado_label = ctk.CTkLabel(self.frame_resultados, text="Pagado: $0.00")
        self.pagado_label.pack(pady=2)
        self.saldo_label = ctk.CTkLabel(self.frame_resultados, text="Saldo: $0.00")
        self.saldo_label.pack(pady=2)
        self.comision_vendedor_label = ctk.CTkLabel(self.frame_resultados, text="Comisión Vendedor: $0.00")
        self.comision_vendedor_label.pack(pady=2)
        self.comision_asistente_label = ctk.CTkLabel(self.frame_resultados, text="Comisión Esteticista: $0.00")
        self.comision_asistente_label.pack(pady=2)
        
        # Eventos para cálculos
        self.costo_entry.bind("<KeyRelease>", self.calcular_totales)
        self.sesiones_entry.bind("<KeyRelease>", self.calcular_totales)
        self.sesiones_pagar_entry.bind("<KeyRelease>", self.calcular_totales)
        self.porcentaje_vendedor_entry.bind("<KeyRelease>", self.calcular_totales)
        self.porcentaje_vendedor_promo_entry.bind("<KeyRelease>", self.calcular_totales)
        self.porcentaje_entry.bind("<KeyRelease>", self.calcular_totales)


        # Configurar eventos
        self.tipo_var.trace_add("write", self.on_tipo_change)
        self.tratamiento_var.trace_add("write", self.on_tratamiento_change)
        self.hay_vendedor_var.trace_add("write", self.toggle_vendedor)
        self.hay_vendedor_promo_var.trace_add("write", self.toggle_vendedor)
        self.pagado_adelantado_var.trace_add("write", self.calcular_totales)
        
        # Botón guardar dentro del frame
        self.boton_guardar = ctk.CTkButton(
        self.ventana,
        text="Guardar",
        command=lambda: self.guardar_asignacion(paciente_id),
        fg_color="black",
        hover_color="#1f6aa8",
        height=40
    )
        self.boton_guardar.pack(pady=10)


    
    def toggle_vendedor(self, *args):
        if self.tipo_var.get() == "Promoción":
            if self.hay_vendedor_promo_var.get():
                self.frame_seleccion_vendedor_promo.pack(fill="x", padx=20, pady=5)
                self.frame_porcentaje_vendedor_promo.pack(fill="x", padx=20, pady=5)
            else:
                self.frame_seleccion_vendedor_promo.pack_forget()
                self.frame_porcentaje_vendedor_promo.pack_forget()
                self.vendedor_promo_var.set("")
                self.porcentaje_vendedor_promo_entry.delete(0, 'end')
        else:
            if self.hay_vendedor_var.get():
                self.frame_seleccion_vendedor.pack(fill="x", padx=20, pady=5)
                self.frame_porcentaje_vendedor.pack(fill="x", padx=20, pady=5)
            else:
                self.frame_seleccion_vendedor.pack_forget()
                self.frame_porcentaje_vendedor.pack_forget()
                self.vendedor_var.set("")
                self.porcentaje_vendedor_entry.delete(0, 'end')
        self.calcular_totales()
            
    def calcular_totales(self, *args):
        try:
            if self.tipo_var.get() == "Promoción":
                # Inicializar totales
                total = 0
                comision_asistente_total = 0

                # Calcular total sumando todos los componentes
                for componente in self.componentes_data.values():
                    # El subtotal ya está calculado (precio * sesiones)
                    subtotal_componente = componente['subtotal']
                    total += subtotal_componente

                    # Calcular comisión para este componente específico
                    try:
                        porcentaje = float(componente['porcentaje'].get() or 0)
                        comision_componente = (subtotal_componente * porcentaje) / 100
                        comision_asistente_total += comision_componente
                    except ValueError:
                        continue

                # Si está pagado por adelantado, el pagado es igual al total
                pagado = total if self.pagado_adelantado_var.get() else 0
                saldo = total - pagado

                # Calcular comisión del vendedor sobre el total de la promoción
                comision_vendedor = 0
                if self.hay_vendedor_promo_var.get():
                    try:
                        porcentaje_vendedor = float(self.porcentaje_vendedor_promo_entry.get() or 0)
                        comision_vendedor = (total * porcentaje_vendedor) / 100
                    except ValueError:
                        comision_vendedor = 0

            else:
                # Cálculos para tratamientos normales (código existente)
                try:
                    costo = float(self.costo_entry.get() or 0)
                    sesiones = int(self.sesiones_entry.get() or 0)
                    sesiones_pagar = int(self.sesiones_pagar_entry.get() or 0)
                    
                    total = costo * sesiones
                    pagado = costo * sesiones_pagar
                    saldo = total - pagado
                    
                    # Calcular comisión del vendedor
                    comision_vendedor = 0
                    if self.hay_vendedor_var.get():
                        try:
                            porcentaje_vendedor = float(self.porcentaje_vendedor_entry.get() or 0)
                            comision_vendedor = (total * porcentaje_vendedor) / 100
                        except ValueError:
                            comision_vendedor = 0
                    
                    # Calcular comisión del asistente
                    comision_asistente_total = 0
                    try:
                        porcentaje_asistente = float(self.porcentaje_entry.get() or 0)
                        comision_asistente_total = (pagado * porcentaje_asistente) / 100
                    except ValueError:
                        comision_asistente_total = 0
                except ValueError:
                    return

            # Actualizar etiquetas
            self.total_label.configure(text=f"Total: ${total:.2f}")
            self.pagado_label.configure(text=f"Pagado: ${pagado:.2f}")
            self.saldo_label.configure(text=f"Saldo: ${saldo:.2f}")
            self.comision_vendedor_label.configure(text=f"Comisión Vendedor: ${comision_vendedor:.2f}")
            self.comision_asistente_label.configure(text=f"Comisión Esteticista: ${comision_asistente_total:.2f}")

        except Exception as e:
            print(f"Error en calcular_totales: {str(e)}")




            
    def actualizar_costo(self):
        if not self.tratamiento_var.get():
            return

        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        try:
            # Obtener información del tratamiento
            c.execute("""
                SELECT id, costo, es_promocion 
                FROM tratamientos 
                WHERE nombre = ?
            """, (self.tratamiento_var.get(),))
            result = c.fetchone()
            
            if result:
                tratamiento_id, costo, es_promocion = result
                
                if es_promocion:
                    # Obtener detalles de la promoción
                    c.execute("""
                        SELECT pd.nombre_componente, pd.cantidad_sesiones, 
                            pd.precio_componente
                        FROM promocion_detalles pd
                        WHERE pd.promocion_id = ?
                    """, (tratamiento_id,))
                    
                    componentes = c.fetchall()
                    self.componentes_data = {}
                    total_promocion = 0
                    
                    for nombre, sesiones, precio in componentes:
                        precio_total = precio * sesiones
                        total_promocion += precio_total
                        
                        self.componentes_data[nombre] = {
                            'nombre': nombre,
                            'sesiones': sesiones,
                            'precio': precio_total,
                            'precio_por_sesion': precio,
                            'asistente_var': ctk.StringVar(),
                            'porcentaje_var': ctk.StringVar(value="0")
                        }
                    
                    self.actualizar_componentes_promocion()
                    self.calcular_totales()
                    
                else:
                    # Tratamiento normal
                    self.costo_entry.delete(0, 'end')
                    self.costo_entry.insert(0, str(costo))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar costo: {str(e)}")
        finally:
            conn.close()




        
    def on_tipo_change(self, *args):
        tratamientos, promociones = self.get_tratamientos_y_promociones()
        valores = promociones if self.tipo_var.get() == "Promoción" else tratamientos
        self.tratamiento_var.set("")
        self.tratamiento_entry.delete(0, 'end')

        # Simplemente mostrar/ocultar los frames correspondientes
        if self.tipo_var.get() == "Promoción":
            self.frame_tratamiento_normal.pack_forget()
            self.frame_promocion.pack(fill="x", padx=20, pady=5)
        else:
            self.frame_promocion.pack_forget()
            self.frame_tratamiento_normal.pack(fill="x", padx=20, pady=5)

    def guardar_asignacion(self, paciente_id):
        if self.tipo_var.get() == "Promoción":
            self.guardar_promocion(paciente_id)
        else:
            self.guardar_tratamiento_normal(paciente_id)

    def guardar_promocion(self, paciente_id):
        # Validar que todos los componentes tengan asistente asignado
        for comp_data in self.componentes_data.values():
            if not comp_data['asistente_var'].get():
                messagebox.showerror("Error", f"Debe asignar un asistente para {comp_data['nombre']}")
                return
            if not comp_data['porcentaje'].get():
                messagebox.showerror("Error", f"Debe asignar un porcentaje para {comp_data['nombre']}")
                return
            
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
         
        try:
            # Obtener información de la promoción
            c.execute("""
                SELECT id FROM tratamientos 
                WHERE nombre = ? AND es_promocion = 1
            """, (self.tratamiento_var.get(),))
            promocion_id = c.fetchone()[0]
            
            # Calcular totales
            total_promocion = sum(comp['subtotal'] for comp in self.componentes_data.values())
            total_pagado = total_promocion if self.pagado_adelantado_var.get() else 0
            saldo_pendiente = total_promocion - total_pagado
            
            # Manejar vendedor
            vendedor_id = None
            porcentaje_vendedor = 0
            comision_vendedor = 0
            
            if self.hay_vendedor_promo_var.get():
                if not self.vendedor_promo_var.get():
                    messagebox.showerror("Error", "Debe seleccionar un vendedor")
                    return
                c.execute("SELECT id FROM asistentes WHERE nombre = ?",
                        (self.vendedor_promo_var.get(),))
                vendedor_id = c.fetchone()[0]
                porcentaje_vendedor = float(self.porcentaje_vendedor_promo_entry.get() or 0)
                comision_vendedor = (total_promocion * porcentaje_vendedor) / 100
            
            # Calcular promedio de porcentajes de asistentes para el registro principal
            porcentaje_promedio = sum(float(comp['porcentaje'].get() or 0) 
                                    for comp in self.componentes_data.values()) / len(self.componentes_data)

            # Insertar registro principal
            c.execute("""
                INSERT INTO tratamientos_asignados 
                (paciente_id, tratamiento_id, vendedor_id, porcentaje_vendedor,
                porcentaje_asistente, sesiones_asignadas, sesiones_pagadas, 
                sesiones_restantes, costo_total, total_pagado, saldo_pendiente, 
                comision_vendedor, fecha_asignacion, fecha_primera_sesion, estado, es_promocion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), ?, 'ACTIVO', '1')
            """, (
                paciente_id, promocion_id, vendedor_id, porcentaje_vendedor,
                porcentaje_promedio, 1, 1 if total_pagado > 0 else 0, 1,
                total_promocion, total_pagado, saldo_pendiente, comision_vendedor,
                self.fecha_primera_sesion.get_date().strftime('%Y-%m-%d')
            ))
            
            tratamiento_asignado_id = c.lastrowid
            
            # Insertar componentes en promocion_componentes
            for comp_id, comp_data in self.componentes_data.items():
                # Insertar en promocion_componentes con el total de sesiones planificadas
                c.execute("""
                    INSERT INTO promocion_componentes 
                    (tratamiento_asignado_id, tratamiento_id, sesiones_asignadas, 
                    sesiones_restantes)
                    VALUES (?, ?, ?, ?)
                """, (
                    tratamiento_asignado_id, comp_id, 
                    comp_data['cantidad_sesiones'], 
                    comp_data['cantidad_sesiones']
                ))

                # Obtener el ID del asistente
                c.execute("SELECT id FROM asistentes WHERE nombre = ?", 
                        (comp_data['asistente_var'].get(),))
                asistente_id = c.fetchone()[0]
                porcentaje = float(comp_data['porcentaje'].get() or 0)

                # Crear solo la primera sesión para cada componente
                c.execute("""
                    INSERT INTO sesiones_realizadas
                    (tratamiento_asignado_id, fecha_sesion, numero_sesion,
                    asistente_id, estado_sesion, estado_pago, 
                    porcentaje_asistente, nombre_componente, comision_sumada)
                    VALUES (?, ?, ?, ?, 'PENDIENTE', ?, ?, ?, 0)
                """, (
                    tratamiento_asignado_id,
                    self.fecha_primera_sesion.get_date().strftime('%Y-%m-%d'),
                    1,  # Solo la primera sesión
                    asistente_id,
                    'PAGADO' if self.pagado_adelantado_var.get() else 'PENDIENTE',
                    porcentaje,
                    comp_data['nombre']
                ))

            conn.commit()
            self.ventana.withdraw()
            messagebox.showinfo("Éxito", "Promoción asignada correctamente")
            self.ventana.destroy()
            self.actualizar_lista_pacientes()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar la promoción: {str(e)}")
            raise  # Para ver el error completo en la consola
        finally:
            conn.close()

    def guardar_tratamiento_normal(self, paciente_id):
        # Validaciones básicas
        if not self.asistente_var.get():
            messagebox.showerror("Error", "Debe seleccionar un asistente")
            return
            
        try:
            sesiones = int(self.sesiones_entry.get())
            costo = float(self.costo_entry.get())
            sesiones_pagadas = int(self.sesiones_pagar_entry.get())
            porcentaje_asistente = float(self.porcentaje_entry.get())
            
            # Calcular los totales
            costo_total = costo * sesiones
            total_pagado = costo * sesiones_pagadas
            saldo_pendiente = costo_total - total_pagado
            comision_asistente = (costo_total * porcentaje_asistente / 100)
            
            # Manejar vendedor si existe
            vendedor_id = None
            porcentaje_vendedor = None
            comision_vendedor = None
            
            if self.hay_vendedor_var.get():
                if not self.vendedor_var.get():
                    messagebox.showerror("Error", "Debe seleccionar un vendedor")
                    return
                try:
                    porcentaje_vendedor = float(self.porcentaje_vendedor_entry.get())
                    comision_vendedor = (costo_total * porcentaje_vendedor / 100)
                except ValueError:
                    messagebox.showerror("Error", "El porcentaje del vendedor debe ser un número válido")
                    return
        except ValueError:
            messagebox.showerror("Error", "Los valores numéricos ingresados no son válidos")
            return

        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        try:
            # Obtener IDs necesarios
            c.execute("SELECT id FROM tratamientos WHERE nombre = ? AND es_promocion = 0",
                    (self.tratamiento_var.get(),))
            tratamiento_id = c.fetchone()[0]
            
            c.execute("SELECT id FROM asistentes WHERE nombre = ?",
                    (self.asistente_var.get(),))
            asistente_id = c.fetchone()[0]
            
            if self.hay_vendedor_var.get():
                c.execute("SELECT id FROM asistentes WHERE nombre = ?",
                        (self.vendedor_var.get(),))
                vendedor_id = c.fetchone()[0]
            
            # Insertar tratamiento asignado con todos los campos requeridos
            c.execute("""
                INSERT INTO tratamientos_asignados 
                (paciente_id, tratamiento_id, asistente_id, vendedor_id, 
                porcentaje_asistente, porcentaje_vendedor, sesiones_asignadas,
                sesiones_pagadas, sesiones_restantes, costo_total, total_pagado,
                saldo_pendiente, comision_vendedor, comision_asistente,
                fecha_asignacion, fecha_primera_sesion, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, DATE('now'), ?, 'ACTIVO')
            """, (
                paciente_id, tratamiento_id, asistente_id, vendedor_id,
                porcentaje_asistente, porcentaje_vendedor, sesiones,
                sesiones_pagadas, sesiones, costo_total, total_pagado,
                saldo_pendiente, comision_vendedor, comision_asistente,
                self.fecha_primera_sesion.get_date().strftime('%Y-%m-%d')
            ))
            tratamiento_asignado_id = c.lastrowid
            
            # Crear solo la primera sesión
            c.execute("""
                INSERT INTO sesiones_realizadas
                (tratamiento_asignado_id, fecha_sesion, numero_sesion,
                asistente_id, estado_sesion, estado_pago, porcentaje_asistente, proxima_cita)
                VALUES (?, ?, ?, ?, 'PENDIENTE', ?, ?, ?)
            """, (
                tratamiento_asignado_id,
                self.fecha_primera_sesion.get_date().strftime('%Y-%m-%d'),
                1,  # Solo la primera sesión
                asistente_id,
                'PAGADO' if sesiones_pagadas > 0 else 'PENDIENTE',
                porcentaje_asistente,
                self.fecha_primera_sesion.get_date().strftime('%Y-%m-%d')  # Agregamos la próxima cita
            ))
            
            conn.commit()
            self.ventana.withdraw()
            messagebox.showinfo("Éxito", "Tratamiento asignado correctamente")
            self.actualizar_lista_pacientes()
            
        except Exception as e: 
            conn.rollback()
            messagebox.showerror("Error", f"Error al guardar el tratamiento: {str(e)}")
        finally:
            conn.close()


        

    def get_tratamientos_y_promociones(self):
        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        c.execute("SELECT nombre, es_promocion FROM tratamientos ORDER BY nombre")
        resultados = c.fetchall()
        conn.close()
        
        tratamientos = [nombre for nombre, es_promo in resultados if not es_promo]
        promociones = [nombre for nombre, es_promo in resultados if es_promo]
        return tratamientos, promociones

    def on_tratamiento_change(self, *args):
        if not self.tratamiento_var.get():
            return

        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()

        try:
            c.execute("""
                SELECT es_promocion, costo
                FROM tratamientos 
                WHERE nombre = ?
            """, (self.tratamiento_var.get(),))
            result = c.fetchone()
            if not result:
                return
            
            es_promocion, costo = result

            # Limpiar costo anterior
            self.costo_entry.delete(0, 'end')
            self.costo_entry.insert(0, str(costo if costo else 0))

            if es_promocion:
                # Actualizar componentes de la promoción
                self.actualizar_componentes_promocion()
            else:
                # Actualizar campos de tratamiento normal
                self.actualizar_campos_tratamiento()

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el tratamiento: {str(e)}")
        finally:
            conn.close()


    def actualizar_campos_tratamiento(self):
        # Actualizar campos específicos de tratamiento normal
        self.sesiones_entry.delete(0, 'end')
        self.sesiones_pagar_entry.delete(0, 'end')
        self.porcentaje_entry.delete(0, 'end')
        self.calcular_totales()

    def actualizar_componentes_promocion(self):
        # Limpiar componentes anteriores
        for widget in self.frame_esteticistas_componentes.winfo_children():
            widget.destroy()

        conn = sqlite3.connect('spa_database.db')
        c = conn.cursor()
        
        try:
            # Primero obtener el ID de la promoción
            c.execute("""
                SELECT id
                FROM tratamientos
                WHERE nombre = ? AND es_promocion = 1
            """, (self.tratamiento_var.get(),))
            
            promocion_id = c.fetchone()[0]
            
            # Ahora obtener todos los componentes de esta promoción
            c.execute("""
                SELECT pd.nombre_componente, pd.precio_componente, pd.id, pd.cantidad_sesiones
                FROM promocion_detalles pd
                WHERE pd.promocion_id = ?
            """, (promocion_id,))
            
            componentes = c.fetchall()
            self.componentes_data = {}
            
            total_promocion = 0

            for nombre, precio, componente_id, cantidad_sesiones in componentes:
                frame = ctk.CTkFrame(self.frame_esteticistas_componentes)
                frame.pack(fill="x", pady=5)

                # Calcular subtotal de este componente
                subtotal_componente = precio * cantidad_sesiones
                total_promocion += subtotal_componente
                
                # Label con nombre, precio, sesiones y subtotal
                ctk.CTkLabel(frame, 
                           text=f"{nombre} (${precio:.2f} x {cantidad_sesiones} sesiones = ${subtotal_componente:.2f})").pack(side="left")

                asistente_var = ctk.StringVar()
                asistente_combo = ctk.CTkComboBox(frame, variable=asistente_var,
                                                values=self.get_asistentes())
                asistente_combo.pack(side="left", padx=10)

                porcentaje_var = ctk.StringVar(value="0")
                porcentaje_entry = ctk.CTkEntry(frame, textvariable=porcentaje_var,
                                            placeholder_text="% comisión")
                porcentaje_entry.pack(side="right", padx=10)

                # Agregar eventos para recalcular
                asistente_var.trace_add("write", self.calcular_totales)
                porcentaje_var.trace_add("write", self.calcular_totales)

                self.componentes_data[componente_id] = {
                    'nombre': nombre,
                    'precio': precio,
                    'cantidad_sesiones': cantidad_sesiones,
                    'subtotal': subtotal_componente,
                    'asistente_var': asistente_var,
                    'porcentaje': porcentaje_var,
                    'frame': frame
                }

            # Actualizar el costo total en la entrada
            self.costo_entry.delete(0, 'end')
            self.costo_entry.insert(0, str(total_promocion))
            
            self.calcular_totales()

        finally:
            conn.close()

    def abrir_seleccion_tratamiento(self):
        self.ventana_seleccion = ctk.CTkToplevel(self.root)
        self.ventana_seleccion.title("Seleccionar Tratamiento")
        self.ventana_seleccion.geometry("400x400")
        self.ventana_seleccion.wm_attributes("-topmost", True)
        self.ventana_seleccion.grab_set()

        frame_lista = ctk.CTkFrame(self.ventana_seleccion)
        frame_lista.pack(fill="both", expand=True, padx=20, pady=20)

        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side="right", fill="y")

        self.lista_tratamientos = ttk.Treeview(frame_lista, columns=("Tratamiento"), show="headings", height=5, yscrollcommand=scrollbar.set)
        self.lista_tratamientos.heading("Tratamiento", text="Tratamiento")
        self.lista_tratamientos.pack(fill="both", expand=True)

        scrollbar.config(command=self.lista_tratamientos.yview)
        self.lista_tratamientos.configure(yscrollcommand=scrollbar.set)

        tratamientos, promociones = self.get_tratamientos_y_promociones()
        if self.tipo_var.get() == "Promoción":
            items = promociones
        else:
            items = tratamientos

        for item in items:
            self.lista_tratamientos.insert("", "end", values=(item,))

        btn_seleccionar = ctk.CTkButton(self.ventana_seleccion, text="Seleccionar", command=self.seleccionar_tratamiento, fg_color="black", hover_color="#1f6aa8")
        btn_seleccionar.pack(pady=(5,5))

    def seleccionar_tratamiento(self):
        seleccion = self.lista_tratamientos.item(self.lista_tratamientos.selection())['values'][0]
        self.tratamiento_var.set(seleccion)
        self.ventana_seleccion.destroy()
        self.on_tratamiento_change()

  
        
    def volver_menu_principal(self):
        # Llamar al método show_main_menu() de la clase principal
        self.main_system.show_main_menu()