import sys
import os
import customtkinter as ctk
from control_sesiones import ControlSesiones
from pacientes import PacientesManagement
from tratamientos import TratamientosManagement
from reportes import ReportesManagement
from database import create_database
from asistentes import AsistentesManagement
from PIL import Image

# Función para obtener la ruta base de recursos
def resource_path(relative_path):
    """Obtiene la ruta absoluta del recurso, considerando si está empaquetado o no."""
    if getattr(sys, 'frozen', False):  # Si está empaquetado
        base_path = sys._MEIPASS
    else:  # Durante el desarrollo
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

create_database()

class SpaManagementSystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sistema de Gestión - Spa")
        ctk.set_appearance_mode("light")
        self.root.resizable(False, False)
        self.root.after(0, lambda: self.root.state("zoomed")) 
        self.show_main_menu()
    
    def show_main_menu(self):
        # Eliminar widgets existentes
        for widget in self.root.winfo_children():
            widget.destroy()

        # Contenedor principal
        main_container = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_container.pack(fill="both", expand=True)

        # Cargar y configurar la imagen de fondo
        try:
            bg_image_path = resource_path("assets/prueba.jpg")
            bg_image = Image.open(bg_image_path)
            bg_image = bg_image.resize((1200, 2400), Image.Resampling.LANCZOS)
            ctk_image_bg = ctk.CTkImage(light_image=bg_image, dark_image=bg_image, size=(1600,1200))

            # Etiqueta para la imagen de fondo
            bg_label = ctk.CTkLabel(main_container, image=ctk_image_bg, text="")
            bg_label.place(relx=1, rely=0, anchor="ne", relheight=1)  # Ocupa toda la ventana
        except Exception as e:
            print(f"Error al cargar la imagen de fondo: {e}")

        # Contenedor para widgets encima del fondo
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.place(relx=0.1, rely=0.5, anchor="w")

        # Logotipo
        try:
            logo_image_path = resource_path("assets/logotipo.png")
            logo_image = Image.open(logo_image_path)
            ctk_image_logo = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(150, 150))

            logo_label = ctk.CTkLabel(content_frame, image=ctk_image_logo, text="")
            logo_label.pack(pady=20)
        except Exception as e:
            print(f"Error al cargar el logo: {e}")

        # Título
        title_label = ctk.CTkLabel(
            content_frame,
            text="Sistema de Gestión - Spa",
            font=ctk.CTkFont(family="Helvetica", size=25, weight="bold"),
            text_color=("black", "white"),
        )
        title_label.pack(pady=20, padx=60)

        # Frame para botones
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=20)

        # Estilo de botones
        btn_style = {
            "width": 300,
            "height": 50,
            "corner_radius": 10,
            "fg_color": "#676767",
            "hover_color": "#000000",
            "border_width": 2,
            "border_color": "#9e8d59",
            "text_color": "white",
        }

        # Botones del menú
        buttons = [
            ("Control de Pacientes", self.show_pacientes_menu),
            ("Control de Tratamientos", self.show_tratamientos_menu), 
            ("Esteticista", self.show_asistentes_menu),
            ("Sesiones Control", self.show_sesiones_menu),
            ("Reportes", self.show_reportes_menu),
        ]

        for text, command in buttons:
            btn = ctk.CTkButton(button_frame, text=text, command=command, **btn_style)
            btn.pack(pady=10)

        # Botón de cerrar
        close_btn_style = btn_style.copy()
        close_btn_style.update(
            {
                "fg_color": "#e74c3c",
                "hover_color": "#c0392b",
            }
        )

        ctk.CTkButton(button_frame, text="Cerrar Programa", command=self.cerrar_sesion, **close_btn_style).pack(pady=20)

    def show_pacientes_menu(self):
        pacientes = PacientesManagement(self.root, self)
        pacientes.show_menu()

    def show_tratamientos_menu(self):
        tratamientos = TratamientosManagement(self.root, self)
        tratamientos.show_menu()

    def show_reportes_menu(self):
        reportes = ReportesManagement(self.root, self)
        reportes.show_menu()

    def show_asistentes_menu(self):
        self.asistentes_management = AsistentesManagement(self.root, self)
        self.asistentes_management.show_menu()

    def show_sesiones_menu(self):
        sesiones = ControlSesiones(self.root, self)
        sesiones.show_menu()

    def run(self):
        self.root.mainloop()

    def cerrar_sesion(self):
        self.root.destroy()


if __name__ == "__main__":
    app = SpaManagementSystem()
    app.run()
