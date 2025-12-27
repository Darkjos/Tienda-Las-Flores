import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

# ---------------------------------------------
# CONEXIÓN A BASE DE DATOS
# ---------------------------------------------
conn = sqlite3.connect("tienda.db")
cursor = conn.cursor()
productos_en_venta = []

# ---------------------------------------------
# FUNCIONES DE UTILIDAD
# ---------------------------------------------
def generar_codigo_venta():
    cursor.execute("SELECT codigo_venta FROM ventas ORDER BY codigo_venta DESC LIMIT 1")
    resultado = cursor.fetchone()
    if resultado is None:
        return "VT0001"
    else:
        numero = int(resultado[0][2:]) + 1
        return f"VT{numero:04d}"

def actualizar_combo():
    cursor.execute("SELECT codigo_producto, nombre FROM productos")
    productos = cursor.fetchall()
    codigos = [p[0] for p in productos]
    combo_codigo['values'] = codigos

def buscar_por_nombre(event=None):
    nombre = entry_buscar_nombre.get().strip()
    listbox_resultados.delete(0, tk.END)
    if nombre == "":
        combo_codigo.set("")
        return
    cursor.execute("SELECT codigo_producto, nombre FROM productos WHERE nombre LIKE ?", ('%' + nombre + '%',))
    resultados = cursor.fetchall()
    if resultados:
        for codigo, nombre in resultados:
            listbox_resultados.insert(tk.END, f"{codigo} - {nombre}")
    else:
        listbox_resultados.insert(tk.END, "No se encontraron coincidencias")

def seleccionar_producto(event):
    seleccion = listbox_resultados.curselection()
    if seleccion:
        valor = listbox_resultados.get(seleccion[0])
        combo_codigo.set(valor.split(" - ")[0])

# ---------------------------------------------
# FUNCIONES DE VENTA
# ---------------------------------------------
def agregar_a_venta():
    codigo = combo_codigo.get()
    if not codigo:
        messagebox.showerror("Error", "Seleccione un producto válido")
        return
    try:
        cantidad = int(entry_cantidad.get())
        if cantidad <= 0:
            messagebox.showerror("Error", "Cantidad debe ser mayor que cero")
            return
        cursor.execute("SELECT nombre, precio_unitario, stock_actual FROM productos WHERE codigo_producto = ?", (codigo,))
        producto = cursor.fetchone()
        if producto:
            nombre, precio, stock = producto
            if cantidad > stock:
                messagebox.showwarning("Stock insuficiente", f"Stock disponible: {stock}")
                return
            subtotal = round(precio * cantidad, 2)
            productos_en_venta.append((codigo, nombre, cantidad, precio, subtotal))
            actualizar_tree()
            actualizar_total()
            entry_cantidad.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Producto no encontrado")
    except ValueError:
        messagebox.showerror("Error", "Cantidad no válida")

def actualizar_tree():
    tree.delete(*tree.get_children())
    for i, (codigo, nombre, cantidad, precio, subtotal) in enumerate(productos_en_venta, start=1):
        tree.insert("", "end", values=(i, codigo, nombre, cantidad, f"${precio:.2f}", f"${subtotal:.2f}"))

def actualizar_total():
    total = sum(x[4] for x in productos_en_venta)
    label_total.config(text=f"Total: ${total:.2f}")
    actualizar_cambio()

def actualizar_cambio(event=None):
    try:
        pago = float(entry_pago.get())
    except ValueError:
        pago = 0
    total = sum(x[4] for x in productos_en_venta)
    cambio = round(pago - total, 2) if pago >= total else 0
    label_cambio.config(text=f"Cambio: ${cambio:.2f}")

def eliminar_item():
    item = tree.selection()
    if item:
        index = tree.index(item[0])
        productos_en_venta.pop(index)
        actualizar_tree()
        actualizar_total()

def cancelar_venta():
    productos_en_venta.clear()
    actualizar_tree()
    actualizar_total()
    codigo_venta_var.set(generar_codigo_venta())
    entry_cantidad.delete(0, tk.END)
    combo_codigo.set("")
    entry_buscar_nombre.delete(0, tk.END)
    listbox_resultados.delete(0, tk.END)
    entry_pago.delete(0, tk.END)
    label_cambio.config(text="Cambio: $0.00")

def confirmar_venta():
    codigo_venta = codigo_venta_var.get()
    if not codigo_venta or not productos_en_venta:
        messagebox.showwarning("Aviso", "Ingrese código de venta y al menos un producto")
        return
    total = sum(x[4] for x in productos_en_venta)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("INSERT INTO ventas VALUES (?, ?, ?)", (codigo_venta, fecha, total))
        for i, (codigo, _, cantidad, precio, subtotal) in enumerate(productos_en_venta):
            cursor.execute("INSERT INTO detalle_venta VALUES (?, ?, ?, ?, ?, ?)",
                           (f"{codigo_venta}-D{i+1:02}", codigo_venta, codigo, cantidad, precio, subtotal))
            cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE codigo_producto = ?", (cantidad, codigo))
        conn.commit()
        generar_recibo(codigo_venta, fecha, total)
        messagebox.showinfo("Éxito", "Venta registrada correctamente")
        cancelar_venta()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def generar_recibo(codigo, fecha, total):
    carpeta = "recibos"
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)
    with open(f"{carpeta}/recibo_{codigo}.txt", "w") as f:
        f.write(f"RECIBO DE VENTA\n\nFecha: {fecha}\nVenta: {codigo}\n\n")
        f.write("Producto\tCant.\tP.Unit\tSubtotal\n")
        for _, nombre, cantidad, precio, subtotal in productos_en_venta:
            f.write(f"{nombre}\t{cantidad}\t${precio:.2f}\t${subtotal:.2f}\n")
        f.write("\n------------------------\n")
        f.write(f"TOTAL: ${total:.2f}\n")

# ---------------------------------------------
# MODIFICAR CANTIDAD (VENTANA EMERGENTE)
# ---------------------------------------------
def modificar_cantidad(event=None):
    item = tree.selection()
    if not item:
        return
    index = tree.index(item[0])
    codigo, nombre, cantidad, precio, subtotal = productos_en_venta[index]

    # Ventana emergente con estilo
    top = tk.Toplevel(root)
    top.title("Modificar Cantidad")
    top.geometry("300x160")
    top.configure(bg="#f0f8ff")
    top.grab_set()

    tk.Label(top, text=f"Producto: {nombre}", font=("Arial", 12, "bold"), bg="#f0f8ff").pack(pady=5)
    tk.Label(top, text="Nueva cantidad:", font=("Arial", 11), bg="#f0f8ff").pack()

    entry_nueva_cantidad = tk.Entry(top, font=("Arial", 12), justify="center")
    entry_nueva_cantidad.insert(0, str(cantidad))
    entry_nueva_cantidad.pack(pady=5)

    def guardar():
        try:
            nueva_cant = int(entry_nueva_cantidad.get())
            if nueva_cant <= 0:
                messagebox.showerror("Error", "La cantidad debe ser mayor que cero")
                return
            subtotal_nuevo = nueva_cant * precio
            productos_en_venta[index] = (codigo, nombre, nueva_cant, precio, subtotal_nuevo)
            actualizar_tree()
            actualizar_total()
            top.destroy()
        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida")

    ttk.Button(top, text="Guardar", command=guardar, style="Accion.TButton").pack(pady=10)

# ---------------------------------------------
# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA
# ---------------------------------------------
root = tk.Tk()
root.title("Vendedor - Tienda Las Flores")
root.geometry("1280x800")
root.resizable(False, False)

# -----------------------------
# ESTILOS
# -----------------------------
style = ttk.Style()
style.theme_use("clam")

# Botones
style.configure("Agregar.TButton", font=("Arial", 12, "bold"), foreground="white",
                background="#28a745", padding=12, relief="raised")
style.map("Agregar.TButton", background=[('active', '#218838')])

style.configure("Accion.TButton", font=("Arial", 12, "bold"), foreground="white",
                background="#007bff", padding=12, relief="raised")
style.map("Accion.TButton", background=[('active', '#0056b3')])

# Labels destacados
style.configure("Destacado.TLabel", font=("Arial", 14, "bold"),
                foreground="#ffffff", background="#007bff", padding=5, relief="ridge")

# Entradas llamativas
style.configure("TEntry", font=("Arial", 12, "bold"),
                foreground="#000000", fieldbackground="#e6f2ff",
                borderwidth=2, relief="solid")

# -----------------------------
# FRAME PRINCIPAL DE DATOS
# -----------------------------
frame = ttk.Frame(root)
frame.pack(fill="x", padx=15, pady=15)

# Código de venta
ttk.Label(frame, text="Código Venta", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w", pady=5)
codigo_venta_var = tk.StringVar()
codigo_venta_var.set(generar_codigo_venta())
label_codigo_venta = ttk.Label(frame, textvariable=codigo_venta_var, font=("Arial", 12),
                               width=20, relief="sunken", background="#f0f0f0")
label_codigo_venta.grid(row=0, column=1, sticky="w", pady=5)

# Producto y cantidad
ttk.Label(frame, text="Producto (Código)", font=("Arial", 14, "bold")).grid(row=1, column=0, sticky="w", pady=5)
combo_codigo = ttk.Combobox(frame, font=("Arial", 12, "bold"), width=25)
combo_codigo.grid(row=1, column=1, sticky="w", pady=5)

ttk.Label(frame, text="Cantidad", font=("Arial", 14, "bold")).grid(row=2, column=0, sticky="w", pady=5)
entry_cantidad = ttk.Entry(frame, font=("Arial", 12, "bold"), width=10)
entry_cantidad.grid(row=2, column=1, sticky="w", pady=5)

btn_agregar = ttk.Button(frame, text="Agregar a Venta", command=agregar_a_venta, style="Agregar.TButton")
btn_agregar.grid(row=3, column=0, sticky="w", pady=10)

# Buscar producto
ttk.Label(frame, text="Buscar producto", font=("Arial", 14, "bold")).grid(row=0, column=3, sticky="w", pady=5)
entry_buscar_nombre = ttk.Entry(frame, font=("Arial", 12, "bold"), width=65)
entry_buscar_nombre.grid(row=0, column=4, sticky="w", pady=5)
entry_buscar_nombre.bind("<KeyRelease>", buscar_por_nombre)

listbox_resultados = tk.Listbox(frame, font=("Arial", 12, "bold"), width=65, height=5)
listbox_resultados.grid(row=1, column=4, rowspan=2, sticky="w", pady=5)
listbox_resultados.bind("<Double-Button-1>", seleccionar_producto)

# -----------------------------
# TREEVIEW
# -----------------------------
columns = ("#", "Código", "Nombre", "Cantidad", "Precio", "Subtotal")
tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

for col in columns:
    tree.heading(col, text=col)
    if col == "Nombre":
        tree.column(col, width=400, anchor="center")  # Ajuste de ancho para "Nombre"
    if col == "#":
        tree.column(col, width=15, anchor="center")  # Ajuste de ancho para "Nombre"
    if col == "Código":
        tree.column(col, width=25, anchor="center")  # Ajuste de ancho para "Nombre"
    else:
        tree.column(col, anchor="center")

tree.pack(fill="both", expand=True, padx=15, pady=10)

# Evento doble clic para modificar cantidad
tree.bind("<Double-1>", modificar_cantidad)

# -----------------------------
# FRAME PAGO Y TOTALES
# -----------------------------
frame_totales = ttk.Frame(root)
frame_totales.pack(fill="x", padx=15, pady=10)

ttk.Label(frame_totales, text="Paga con:", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
entry_pago = ttk.Entry(frame_totales, font=("Arial", 14, "bold"), width=15)
entry_pago.grid(row=0, column=1, sticky="w", padx=5)
entry_pago.bind("<KeyRelease>", actualizar_cambio)

frame_totales.grid_columnconfigure(2, weight=1)

label_total = ttk.Label(frame_totales, text="Total: $0.00", style="Destacado.TLabel")
label_total.grid(row=0, column=3, sticky="e", padx=10)

label_cambio = ttk.Label(frame_totales, text="Cambio: $0.00", style="Destacado.TLabel")
label_cambio.grid(row=0, column=4, sticky="e", padx=10)

# -----------------------------
# BOTONES ACCIONES
# -----------------------------
btn_frame = ttk.Frame(root)
btn_frame.pack(fill="x", padx=15, pady=10)

btn_confirmar = ttk.Button(btn_frame, text="Confirmar Venta", command=confirmar_venta, style="Accion.TButton")
btn_confirmar.pack(side="left", expand=True, fill="x", padx=5)

btn_eliminar = ttk.Button(btn_frame, text="Eliminar Producto", command=eliminar_item, style="Accion.TButton")
btn_eliminar.pack(side="left", expand=True, fill="x", padx=5)

btn_cancelar = ttk.Button(btn_frame, text="Cancelar Venta", command=cancelar_venta, style="Accion.TButton")
btn_cancelar.pack(side="left", expand=True, fill="x", padx=5)

# Inicializar combobox
actualizar_combo()

# Ejecutar GUI
root.mainloop()
conn.close()
