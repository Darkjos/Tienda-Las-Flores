import tkinter as tk
from tkinter import ttk

def aplicar_estilos(root):
    # Tema
    style = ttk.Style(root)
    style.theme_use("clam")

    # Labels
    style.configure("TLabel", font=("Arial", 12, "bold"), background=root["bg"])

    # Entradas
    style.configure("TEntry", font=("Arial", 12))

    # Botones generales
    style.configure("TButton", font=("Arial", 12, "bold"), padding=8,
                    foreground="white", background="#007bff", relief="raised")
    style.map("TButton",
              background=[('active', '#0056b3'), ('!active', '#007bff')],
              foreground=[('active', 'white'), ('!active', 'white')])

    # Treeview
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    style.configure("Treeview", font=("Arial", 11), rowheight=28)

    # Botones especiales
    style.configure("Agregar.TButton", font=("Arial", 12, "bold"), foreground="white",
                    background="#28a745", padding=12, relief="raised")
    style.map("Agregar.TButton", background=[('active', '#218838')])

    style.configure("Accion.TButton", font=("Arial", 12, "bold"), foreground="white",
                    background="#007bff", padding=12, relief="raised")
    style.map("Accion.TButton", background=[('active', '#0056b3')])

    # Labels destacados
    style.configure("Destacado.TLabel", font=("Arial", 14, "bold"),
                    foreground="#ffffff", background="#007bff", padding=5, relief="ridge")
