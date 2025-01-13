import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3



class TratamientosManagement:
    def __init__(self, root, main_system):
        self.root = root
        self.main_system = main_system

    def show_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True,   padx=20, pady=20)

        # Title with better spacing
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(50, 40))
        title = ctk.CTkLabel(title_frame, text="Gestión de Tratamientos", font=("Helvetica", 36, "bold"))
        title.pack()

        # Content container with fixed width
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=40)

        # Form section
        form_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 20))

        # Fields container with fixed width
        fields_container = ctk.CTkFrame(form_frame, fg_color="transparent", width=600)
        fields_container.pack(anchor="center")
        fields_container.pack_propagate(False)  # Prevent container from shrinking

        # Nombre field with consistent spacing
        nombre_frame = ctk.CTkFrame(fields_container, fg_color="transparent")
        nombre_frame.pack(fill="x", pady=5)
        nombre_label = ctk.CTkLabel(nombre_frame, text="Nombre del Tratamiento:", width=150)
        nombre_label.pack(side="left")
        self.tratamiento_entries = {}
        self.tratamiento_entries["Nombre del Tratamiento:"] = ctk.CTkEntry(nombre_frame, width=300)
        self.tratamiento_entries["Nombre del Tratamiento:"].pack(side="left", padx=(10, 0))

        # Costo field
        self.costo_frame = ctk.CTkFrame(fields_container, fg_color="transparent")
        self.costo_frame.pack(fill="x", pady=5)
        costo_label = ctk.CTkLabel(self.costo_frame, text="Costo:", width=150)
        costo_label.pack(side="left")
        self.tratamiento_entries["Costo:"] = ctk.CTkEntry(self.costo_frame, width=300)
        self.tratamiento_entries["Costo:"].pack(side="left", padx=(10, 0))
        # Promoción checkbox
        promo_frame = ctk.CTkFrame(fields_container, fg_color="transparent")
        promo_frame.pack(fill="x", pady=5)
        self.es_promocion = ctk.CTkCheckBox(promo_frame, text="Es una promoción", command=self.toggle_costo_field)
        self.es_promocion.pack(side="left", padx=(150, 0))

        # Buttons with consistent styling
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.pack(pady=1)
        
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


        ctk.CTkButton(btn_frame, text="Agregar", command=self.agregar_tratamiento, **btn_style).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Modificar", command=self.modificar_tratamiento, **btn_style).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="Volver al Menú Principal", 
                    command=self.volver_menu_principal, 
                    width=200, 
                    **close_btn_style).pack(side="left", padx=5)

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
        
        # Table container
        table_frame = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", border_width=1)
        table_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Enhanced table
        columns = ("ID", "Nombre", "Costo", "Tipo")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")
        
        # Configure columns with better proportions
        column_widths = {"ID": 1, "Nombre": 300, "Costo": 150, "Tipo": 150}
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

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_select_tratamiento)
        self.tree.bind("<Double-1>", self.ver_detalles_tratamiento)
        
        # Initial table update
        self.actualizar_lista_tratamientos()

    def ver_detalles_tratamiento(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = self.tree.item(selected_items[0])
        tratamiento_id = item['values'][0]
        nombre = item['values'][1]
        es_promocion = item['values'][3] == "Promoción"

        try:
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            
            if es_promocion:
                # Obtener detalles de la promoción
                c.execute("""
                    SELECT nombre_componente, cantidad_sesiones, precio_componente
                    FROM promocion_detalles
                    WHERE promocion_id = ?
                """, (tratamiento_id,))
                
                componentes = c.fetchall()
                
                if componentes:
                    detalles = f"Detalles de la promoción: {nombre}\n\n"
                    total = 0
                    for comp in componentes:
                        nombre_comp, sesiones, precio = comp
                        detalles += f"Componente: {nombre_comp}\n"
                        detalles += f"Sesiones: {sesiones}\n"
                        detalles += f"Precio por sesión: ${precio:.2f}\n"
                        total += precio * sesiones  # Sumar el costo total de las sesiones
                        detalles += "-" * 40 + "\n"
                    
                    detalles += f"\nTotal de la promoción: ${total:.2f}"
                else:
                    detalles = "No se encontraron componentes para esta promoción."
            else:
                # Obtener detalles del tratamiento normal
                c.execute("""
                    SELECT nombre, costo
                    FROM tratamientos
                    WHERE id = ?
                """, (tratamiento_id,))
                
                tratamiento = c.fetchone()
                if tratamiento:
                    detalles = f"Detalles del tratamiento:\n\n"
                    detalles += f"Nombre: {tratamiento[0]}\n"
                    detalles += f"Costo: ${tratamiento[1]:.2f}"
                else:
                    detalles = "No se encontraron detalles para este tratamiento."

            conn.close()
            messagebox.showinfo("Detalles", detalles)

        except Exception as e:
            messagebox.showerror("Error", f"Error al obtener detalles: {str(e)}")

    def toggle_costo_field(self):
        """Muestra u oculta el campo de costo según el estado del checkbox de promoción"""
        if self.es_promocion.get():
            self.costo_frame.pack_forget()  # Oculta el frame de costo
            self.tratamiento_entries["Costo:"].delete(0, 'end')  # Limpia el campo de costo
        else:
            # Asegurarse de que el costo aparezca en la posición correcta
            self.costo_frame.pack(fill="x", pady=5)  # Muestra el frame de costo
            
    def agregar_tratamiento(self):
        try:
            nombre = self.tratamiento_entries["Nombre del Tratamiento:"].get()
            es_promocion = self.es_promocion.get()  # True o False
            
            # Validar nombre
            if not nombre:
                messagebox.showerror("Error", "El nombre del tratamiento es obligatorio.")
                return

            # Si no es una promoción, validar el costo
            costo = self.tratamiento_entries["Costo:"].get()
            if not es_promocion:
                if not costo or float(costo) <= 0:
                    messagebox.showerror("Error", "El costo es obligatorio para tratamientos únicos y debe ser mayor a 0.")
                    return
                costo = float(costo)  # Convertir a número para guardar
            
            # Si es promoción, llamamos directamente a la ventana de componentes
            if es_promocion:
                self.ventana_componentes_promocion(
                    nombre_promocion=nombre,
                    costo_promocion=float(costo) if costo else 0,
                    detalle_promocion=""  # Puedes agregar un campo para esto si lo necesitas
                )
            else:
                # Conexión a la base de datos
                conn = sqlite3.connect('spa_database.db')
                c = conn.cursor()
                
                # Insertar tratamiento normal
                c.execute("""
                    INSERT INTO tratamientos (nombre, costo, es_promocion)
                    VALUES (?, ?, ?)
                """, (nombre, costo, False))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Tratamiento agregado correctamente")

            # Actualizar lista y limpiar campos
            self.actualizar_lista_tratamientos()
            self.limpiar_campos()

        except ValueError:
            messagebox.showerror("Error", "El costo debe ser un número válido.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar el tratamiento: {e}")

    def ventana_componentes_promocion(self, nombre_promocion, costo_promocion, detalle_promocion):
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Componentes de la Promoción")
        ventana.geometry("800x700")

        ventana.grab_set()
        ventana.focus_force()  # Esto también asegura que la ventana reciba el foco


        frame = ctk.CTkFrame(ventana, fg_color="#FFFFFF")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        # Título y descripción
        ctk.CTkLabel(frame, text="Agregar Componentes de la Promoción", 
                    font=("Helvetica", 24, "bold"), fg_color="#FFFFFF", text_color="#000000", corner_radius=10).pack(pady=(50,15), padx=10, fill="x")

        
        # Frame para mostrar el total
        total_frame = ctk.CTkFrame(frame, fg_color="#FFFFFF", corner_radius=10, border_width=1)
        total_frame.pack(fill="x", pady=10, padx=50)
        total_label = ctk.CTkLabel(total_frame, text="Total: $0.00", font=("Helvetica", 16, "bold"), text_color="#333333")
        total_label.pack(side="right", padx=15, pady=10)

        # Frame para lista de componentes
        componentes_frame = ctk.CTkFrame(frame, fg_color="#FFFFFF", corner_radius=10, border_width=1)
        componentes_frame.pack(fill="both", expand=True, pady=10)

        # Scrollable frame para componentes
        componentes_canvas = tk.Canvas(componentes_frame, bg="#F9F9F9", highlightthickness=0)
        componentes_scroll = ctk.CTkScrollbar(componentes_frame, orientation="vertical", command=componentes_canvas.yview)
        componentes_scroll.pack(side="right", fill="y")

        scrollable_frame = ctk.CTkFrame(componentes_canvas, fg_color="#F9F9F9")
        scrollable_frame.bind("<Configure>", lambda e: componentes_canvas.configure(scrollregion=componentes_canvas.bbox("all")))

        componentes_canvas.create_window((0, 0), window=scrollable_frame, anchor="center")
        componentes_canvas.pack(fill="both", expand=True)
        componentes_canvas.configure(yscrollcommand=componentes_scroll.set)

        # Lista de componentes
        componentes = []

        
        def calcular_total():
            total = 0
            for nombre_entry, precio_entry, sesiones_entry in componentes:
                try:
                    precio = float(precio_entry.get() or 0)
                    sesiones = int(sesiones_entry.get() or 0)
                    total += precio * sesiones
                except ValueError:
                    pass
            total_label.configure(text=f"Total: ${total:.2f}")
            return total

        def agregar_componente():
            comp_frame = ctk.CTkFrame(scrollable_frame, fg_color="#FFFFFF", corner_radius=5)
            comp_frame.pack(fill="x", pady=5, padx=5, anchor="center")

            # Nombre del componente
            nombre_entry = ctk.CTkEntry(comp_frame, placeholder_text="Nombre del componente", width=250)
            nombre_entry.pack(side="left", padx=5, pady=5)

            # Precio por sesión
            precio_entry = ctk.CTkEntry(comp_frame, placeholder_text="Precio por sesión", width=120)
            precio_entry.pack(side="left", padx=5, pady=5)
            precio_entry.bind('<KeyRelease>', lambda e: calcular_total())

            # Número de sesiones
            sesiones_entry = ctk.CTkEntry(comp_frame, placeholder_text="Sesiones", width=100)
            sesiones_entry.pack(side="left", padx=5, pady=5)
            sesiones_entry.bind('<KeyRelease>', lambda e: calcular_total())

            # Botón para eliminar componente
            def eliminar():
                comp_frame.destroy()
                componentes.remove((nombre_entry, precio_entry, sesiones_entry))
                calcular_total()

            ctk.CTkButton(comp_frame, text="X", width=30, command=eliminar,
                        fg_color="#FF4D4D", hover_color="#FF6666", text_color="#FFFFFF", corner_radius=10).pack(side="right", padx=5, pady=5)

            componentes.append((nombre_entry, precio_entry, sesiones_entry))
            
        btn_style = {
            "height": 40,
            "corner_radius": 8,
            "fg_color": "#000000",
            "hover_color": "#676767",
            "border_width": 2,
            "text_color": "white"
        }

        # Botón para agregar componentes
        agregar_btn = ctk.CTkButton(frame, text="Agregar Componente", command=agregar_componente, **btn_style)
        agregar_btn.pack(side="left", pady=15)

        
        
        
        def guardar_promocion():
            try:
                if not componentes:
                    messagebox.showerror("Error", "Debe agregar al menos un componente")
                    return

                total = calcular_total()

                # Validar que todos los campos estén completos
                for nombre_entry, precio_entry, sesiones_entry in componentes:
                    if not all([nombre_entry.get(), precio_entry.get(), sesiones_entry.get()]):
                        messagebox.showerror("Error", "Todos los campos son requeridos")
                        return
 
                conn = sqlite3.connect('spa_database.db')  
                c = conn.cursor()

                # Insertar la promoción principal
                c.execute("""
                    INSERT INTO tratamientos (nombre, costo, es_promocion)
                    VALUES (?, ?, ?)
                """, (nombre_promocion, total, True))
                
                promocion_id = c.lastrowid

                # Insertar los componentes
                for nombre_entry, precio_entry, sesiones_entry in componentes:
                    nombre = nombre_entry.get()
                    precio = float(precio_entry.get())
                    sesiones = int(sesiones_entry.get())

                    c.execute("""
                        INSERT INTO promocion_detalles 
                        (promocion_id, nombre_componente, cantidad_sesiones, precio_componente)
                        VALUES (?, ?, ?, ?)
                    """, (promocion_id, nombre, sesiones, precio))

                conn.commit()
                conn.close()

                self.actualizar_lista_tratamientos()
                ventana.destroy()
                messagebox.showinfo("Éxito", "Promoción agregada correctamente")

            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar la promoción: {str(e)}")
         # Botón de guardar
        guardar_btn = ctk.CTkButton(frame, text="Guardar Promoción",command=guardar_promocion, **btn_style)
        guardar_btn.pack(side= "right", pady=10)

    def modificar_tratamiento(self):
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("Advertencia", "Por favor seleccione un tratamiento para modificar")
                return

            tratamiento_id = self.tree.item(selected_items[0])["values"][0]
            nombre = self.tratamiento_entries["Nombre del Tratamiento:"].get()
            costo = float(self.tratamiento_entries["Costo:"].get())
            es_promocion = self.es_promocion.get()

            if es_promocion:
                messagebox.showwarning("Advertencia", "No se puede modificar una promoción. Solo se puede eliminar.")
                return

            if not nombre or costo <= 0:
                messagebox.showerror("Error", "Por favor complete todos los campos correctamente")
                return

            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()

            # Actualizar tratamiento
            c.execute("""
                UPDATE tratamientos
                SET nombre = ?, costo = ?, es_promocion = ?
                WHERE id = ?
            """, (nombre, costo, es_promocion, tratamiento_id))

            conn.commit()
            conn.close()

            self.actualizar_lista_tratamientos()
            self.limpiar_campos()
            messagebox.showinfo("Éxito", "Tratamiento modificado correctamente")

        except ValueError:
            messagebox.showerror("Error", "El costo debe ser un número válido")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo modificar el tratamiento: {e}")

    
    def actualizar_lista_tratamientos(self):
        # Limpiar tabla actual
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = sqlite3.connect('spa_database.db')
            c = conn.cursor()
            
            # Obtener todos los tratamientos
            c.execute("""
                SELECT id, nombre, costo, es_promocion 
                FROM tratamientos 
                ORDER BY nombre
            """)
            
            tratamientos = c.fetchall()
            conn.close()

            # Insertar tratamientos en la tabla
            for tratamiento in tratamientos:
                id_t, nombre, costo, es_promocion = tratamiento
                tipo = "Promoción" if es_promocion else "Tratamiento"
                self.tree.insert("", "end", values=(id_t, nombre, f"${costo:.2f}", tipo))

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la lista de tratamientos: {e}")

    def on_select_tratamiento(self, event):
        try:
            selected_item = self.tree.selection()[0]
            values = self.tree.item(selected_item)['values']
            
            # Limpiar campos actuales
            self.limpiar_campos()
            
            # Llenar los campos con los valores seleccionados
            self.tratamiento_entries["Nombre del Tratamiento:"].insert(0, values[1])
            
            # Actualizar checkbox de promoción y manejar visibilidad del campo costo
            if values[3] == "Promoción":
                self.es_promocion.select()
                self.costo_frame.pack_forget()  # Ocultar campo costo
                # Deshabilitar campos de edición
                self.tratamiento_entries["Nombre del Tratamiento:"].configure(state='disabled')
                self.es_promocion.configure(state='disabled')
            else:
                self.es_promocion.deselect()
                self.costo_frame.pack(fill="x", padx=10, pady=5)  # Mostrar campo costo
                # Habilitar campos de edición
                self.tratamiento_entries["Nombre del Tratamiento:"].configure(state='normal')
                self.es_promocion.configure(state='normal')
                # Eliminar el símbolo $ y convertir a número
                costo = values[2].replace('$', '')
                self.tratamiento_entries["Costo:"].insert(0, costo)

        except IndexError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Error al seleccionar tratamiento: {e}")

    def limpiar_campos(self):
        # Limpiar entradas de texto
        for entry in self.tratamiento_entries.values():
            entry.delete(0, 'end')
            
        # Desmarcar checkbox de promoción y mostrar campo costo
        self.es_promocion.deselect()
        self.costo_frame.pack(fill="x", padx=10, pady=5)
    def volver_menu_principal(self):
        self.main_system.show_main_menu()