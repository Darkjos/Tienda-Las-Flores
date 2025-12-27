import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

# Librerías para PDF
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Conexión y cursor
conn = sqlite3.connect("tienda.db")
cursor = conn.cursor()

# -----------------------------
# FUNCIONES DE BASE DE DATOS
# -----------------------------
def crear_tablas():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        codigo_producto TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio_unitario REAL NOT NULL,
        stock_actual INTEGER NOT NULL,
        categoria TEXT
    )""")
    conn.commit()

def agregar_producto():
    try:
        precio = float(entry_precio.get())
        stock = int(entry_stock.get())
        cursor.execute("""
            INSERT INTO productos (codigo_producto, nombre, descripcion, precio_unitario, stock_actual, categoria)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry_codigo.get(),
            entry_nombre.get(),
            entry_descripcion.get(),
            precio,
            stock,
            entry_categoria.get()
        ))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto agregado correctamente")
        limpiar_campos()
        actualizar_inventario()
    except ValueError:
        messagebox.showerror("Error", "Precio y stock deben ser valores numéricos")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def actualizar_producto():
    try:
        precio = float(entry_precio.get())
        stock = int(entry_stock.get())
        cursor.execute("""
            UPDATE productos SET
                nombre = ?,
                descripcion = ?,
                precio_unitario = ?,
                stock_actual = ?,
                categoria = ?
            WHERE codigo_producto = ?
        """, (
            entry_nombre.get(),
            entry_descripcion.get(),
            precio,
            stock,
            entry_categoria.get(),
            entry_codigo.get()
        ))
        conn.commit()
        messagebox.showinfo("Éxito", "Producto actualizado correctamente")
        entry_codigo.config(state='normal')
        limpiar_campos()
        actualizar_inventario()
    except ValueError:
        messagebox.showerror("Error", "Precio y stock deben ser valores numéricos")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def buscar_producto():
    nombre = entry_buscar.get()
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM productos WHERE nombre LIKE ?", ('%' + nombre + '%',))
    for row in cursor.fetchall():
        tree.insert('', tk.END, values=row)

def limpiar_campos():
    for e in entries:
        e.delete(0, tk.END)
    entry_codigo.config(state='normal')

def actualizar_inventario():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM productos")
    for row in cursor.fetchall():
        tree.insert('', tk.END, values=row)

def cargar_producto(event):
    item = tree.selection()
    if item:
        valores = tree.item(item, "values")
        entry_codigo.config(state='normal')
        entry_codigo.delete(0, tk.END)
        entry_codigo.insert(0, valores[0])
        entry_nombre.delete(0, tk.END)
        entry_nombre.insert(0, valores[1])
        entry_descripcion.delete(0, tk.END)
        entry_descripcion.insert(0, valores[2])
        entry_precio.delete(0, tk.END)
        entry_precio.insert(0, valores[3])
        entry_stock.delete(0, tk.END)
        entry_stock.insert(0, valores[4])
        entry_categoria.delete(0, tk.END)
        entry_categoria.insert(0, valores[5])
        entry_codigo.config(state='disabled')

# -----------------------------
# EXPORTAR PDF HOJA HORIZONTAL
# -----------------------------
def exportar_pdf():
    # Crear carpeta si no existe
    carpeta_export = "Export Inventario"
    if not os.path.exists(carpeta_export):
        os.makedirs(carpeta_export)

    # Nombre del archivo con fecha y hora
    nombre_archivo = f"Inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    archivo = os.path.join(carpeta_export, nombre_archivo)

    # Verificar si hay datos
    cursor.execute("SELECT * FROM productos")
    datos = cursor.fetchall()
    if not datos:
        messagebox.showwarning("Advertencia", "No hay productos para exportar")
        return

    # Documento PDF en horizontal
    doc = SimpleDocTemplate(archivo, pagesize=landscape(letter))
    elementos = []

    # Estilos
    styles = getSampleStyleSheet()
    estilo_titulo = styles["Title"]
    estilo_normal = styles["Normal"]

    # Título y fecha
    titulo = Paragraph("Inventario - Tienda Las Flores", estilo_titulo)
    fecha = Paragraph(f"Fecha de exportación: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", estilo_normal)
    elementos.append(titulo)
    elementos.append(fecha)
    elementos.append(Spacer(1, 20))

    # Encabezados
    encabezados = ["Código", "Nombre", "Descripción", "Precio", "Stock", "Categoría"]

    # Formatear precios
    datos_formateados = []
    for fila in datos:
        fila_lista = list(fila)
        fila_lista[3] = f"${fila_lista[3]:.2f}"  # Precio con dos decimales
        datos_formateados.append(fila_lista)

    # Crear tabla
    tabla_datos = [encabezados] + datos_formateados
    tabla = Table(tabla_datos, repeatRows=1)

    # Estilos de tabla
    estilo = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#007bff")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ])

    # Filas alternas
    for i in range(1, len(tabla_datos)):
        if i % 2 == 0:
            estilo.add('BACKGROUND', (0,i), (-1,i), colors.whitesmoke)
        else:
            estilo.add('BACKGROUND', (0,i), (-1,i), colors.lightgrey)

    tabla.setStyle(estilo)
    elementos.append(tabla)

    # Generar PDF
    doc.build(elementos)
    messagebox.showinfo("Exportado", f"Inventario exportado correctamente a:\n{archivo}")

# -----------------------------
# INICIALIZACIÓN GUI
# -----------------------------
crear_tablas()
root = tk.Tk()
root.title("Administrador Tienda Las Flores")
root.geometry("1800x900")
root.configure(bg="#f0f4f7")

# -----------------------------
# ESTILOS
# -----------------------------
style = ttk.Style()
style.theme_use("clam")

# Labels
style.configure("TLabel", font=("Arial", 12, "bold"), background="#f0f4f7")

# Entradas
style.configure("TEntry", font=("Arial", 12))

# Botones
style.configure("TButton", font=("Arial", 12, "bold"), padding=8, foreground="white", background="#007bff", relief="raised")
style.map("TButton",
          background=[('active', '#0056b3'), ('!active', '#007bff')],
          foreground=[('active', 'white'), ('!active', 'white')])

# Treeview
style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
style.configure("Treeview", font=("Arial", 11), rowheight=28)

# -----------------------------
# FRAME FORMULARIO
# -----------------------------
frame = ttk.LabelFrame(root, text="Agregar / Editar Producto", padding=20)
frame.pack(side="left", fill="y", padx=20, pady=20)

entry_codigo = ttk.Entry(frame, width=30)
entry_nombre = ttk.Entry(frame, width=30)
entry_descripcion = ttk.Entry(frame, width=30)
entry_precio = ttk.Entry(frame, width=30)
entry_stock = ttk.Entry(frame, width=30)
entry_categoria = ttk.Entry(frame, width=30)

etiquetas = ["Código", "Nombre", "Descripción", "Precio", "Stock", "Categoría"]
entries = [entry_codigo, entry_nombre, entry_descripcion, entry_precio, entry_stock, entry_categoria]

for i, (etiqueta, entrada) in enumerate(zip(etiquetas, entries)):
    ttk.Label(frame, text=etiqueta).grid(row=i, column=0, sticky="w", pady=7)
    entrada.grid(row=i, column=1, pady=7, padx=5)

btn_agregar = ttk.Button(frame, text="Agregar Producto", command=agregar_producto)
btn_actualizar = ttk.Button(frame, text="Actualizar Producto", command=actualizar_producto)
btn_agregar.grid(row=6, columnspan=2, pady=12, sticky="ew")
btn_actualizar.grid(row=7, columnspan=2, pady=12, sticky="ew")

# -----------------------------
# FRAME INVENTARIO
# -----------------------------
frame_inv = ttk.Frame(root, padding=15)
frame_inv.pack(side="right", expand=True, fill="both", padx=20, pady=20)

entry_buscar = ttk.Entry(frame_inv, font=("Arial", 12), width=35)
entry_buscar.pack(fill="x", pady=7, padx=5)

ttk.Button(frame_inv, text="Buscar Producto", command=buscar_producto).pack(pady=7)
ttk.Button(frame_inv, text="Exportar PDF", command=exportar_pdf).pack(pady=12)

tree = ttk.Treeview(frame_inv, columns=("Codigo", "Nombre", "Descripcion", "Precio", "Stock", "Categoria"), show="headings", height=28)
for col in tree["columns"]:
    tree.heading(col, text=col)
tree.pack(expand=True, fill="both", pady=7)
tree.bind("<Double-1>", cargar_producto)

# Colores alternos en filas
def colorear_filas(event):
    for i, item in enumerate(tree.get_children()):
        if i % 2 == 0:
            tree.item(item, tags=("evenrow",))
        else:
            tree.item(item, tags=("oddrow",))

tree.tag_configure("evenrow", background="#e6f2ff")
tree.tag_configure("oddrow", background="#ffffff")
tree.bind("<Map>", colorear_filas)

# -----------------------------
# Inicializar inventario
# -----------------------------
actualizar_inventario()
root.mainloop()
conn.close()
