import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import subprocess
import sys
import os
from estilos import aplicar_estilos  # <-- Importamos los estilos

# Diccionario de usuarios y contraseñas para cada módulo
CREDENCIALES = {
    "administrador": {"user": "Admin", "password": "$Admin1010$"},
    "ventas": {"user": "Ventas", "password": "$Ventas1010$"},
}

# ----------------------------
# DIALOGO DE LOGIN PERSONALIZADO
# ----------------------------
class LoginDialog(simpledialog.Dialog):
    def __init__(self, parent, title, tipo):
        self.tipo = tipo
        super().__init__(parent, title=title)

    def body(self, master):
        master.configure(bg="#f0f4f7")
        ttk.Label(master, text="Usuario:", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", padx=10, pady=10)
        ttk.Label(master, text="Contraseña:", font=("Arial", 12, "bold")).grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.entry_user = ttk.Entry(master, font=("Arial", 12))
        self.entry_pass = ttk.Entry(master, show="*", font=("Arial", 12))

        self.entry_user.grid(row=0, column=1, padx=10, pady=10)
        self.entry_pass.grid(row=1, column=1, padx=10, pady=10)

        return self.entry_user  # foco inicial

    def apply(self):
        self.user = self.entry_user.get()
        self.password = self.entry_pass.get()

# ----------------------------
# APLICACIÓN PRINCIPAL
# ----------------------------
class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema Principal - Tienda")
        self.geometry("450x250")
        self.resizable(False, False)
        self.configure(bg="#e6f2ff")  # fondo suave
        self.iconbitmap("StoreImg.ico")

        # Aplicar estilos desde estilos.py
        aplicar_estilos(self)

        # ----------------------------
        # HEADER
        # ----------------------------
        ttk.Label(self, text="Bienvenido al Sistema de Tienda", style="Header.TLabel").pack(pady=(20,10))
        ttk.Label(self, text="Selecciona una opción", font=("Arial", 14), background="#e6f2ff").pack(pady=(0,20))

        # ----------------------------
        # BOTONES DE MÓDULOS
        # ----------------------------
        btn_admin = ttk.Button(self, text="Administrador de Inventario", style="Module.TButton",
                               command=self.login_administrador)
        btn_admin.pack(fill="x", padx=50, pady=10)

        btn_vendedor = ttk.Button(self, text="Vendedor - Punto de Venta", style="Module.TButton",
                                  command=self.login_ventas)
        btn_vendedor.pack(fill="x", padx=50, pady=10)

    # ----------------------------
    # FUNCIONES DE LOGIN
    # ----------------------------
    def login_administrador(self):
        if self.pedir_credenciales("administrador"):
            self.abrir_administrador()

    def login_ventas(self):
        if self.pedir_credenciales("ventas"):
            self.abrir_vendedor()

    def pedir_credenciales(self, tipo):
        dlg = LoginDialog(self, f"Login {tipo.capitalize()}", tipo)
        user = getattr(dlg, "user", None)
        password = getattr(dlg, "password", None)

        if user == CREDENCIALES[tipo]["user"] and password == CREDENCIALES[tipo]["password"]:
            return True
        else:
            if user is not None or password is not None:
                messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            return False

    # ----------------------------
    # EJECUCIÓN DE MÓDULOS
    # ----------------------------
    def abrir_administrador(self):
        self.withdraw()
        self.run_script("administrador_inventario.py")
        self.deiconify()

    def abrir_vendedor(self):
        self.withdraw()
        self.run_script("vendedor_ventas.py")
        self.deiconify()

    def run_script(self, script_name):
        python_executable = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        subprocess.run([python_executable, script_path])

# ----------------------------
# EJECUCIÓN
# ----------------------------
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
