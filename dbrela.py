import tkinter as tk
from tkinter import messagebox
import pyodbc
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import networkx as nx

def conectar_base_datos():
    instancia = entry_instancia.get()
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()
    base_datos = entry_base_datos.get()

    try:
        conexion = pyodbc.connect('DRIVER={SQL Server};SERVER='+instancia+';DATABASE='+base_datos+';UID='+usuario+';PWD='+contrasena)
        messagebox.showinfo("Conexión exitosa", "La conexión a la base de datos se estableció correctamente.")
        generar_esquema_xml(conexion)
        generar_diagrama_er()
    except pyodbc.Error as err:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos.\nError: {err}")

def generar_esquema_xml(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT name, OBJECT_NAME(parent_object_id) AS parent_table, OBJECT_NAME(referenced_object_id) AS referenced_table FROM sys.foreign_keys;")
    relaciones = cursor.fetchall()

    root = ET.Element("database")

    for relacion in relaciones:
        relationship = ET.SubElement(root, "relationship")
        relationship.set("foreign_key_name", relacion[0])
        relationship.set("parent_table", relacion[1])
        relationship.set("referenced_table", relacion[2])

    arbol_xml = ET.ElementTree(root)
    arbol_xml.write("esquema.xml")

    cursor.close()
    conexion.close()
    messagebox.showinfo("Generación exitosa", "El esquema XML se generó correctamente.")

def generar_diagrama_er():
    tree = ET.parse("esquema.xml")
    root = tree.getroot()

    G = nx.DiGraph()

    for relationship in root.findall('relationship'):
        parent_table = relationship.get('parent_table')
        referenced_table = relationship.get('referenced_table')
        G.add_edge(parent_table, referenced_table)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=12, font_weight="bold", arrows=True)
    plt.title("Diagrama de Entidad-Relación (ER)")
    plt.show()

ventana = tk.Tk()
ventana.title("Generador de Esquema XML y Diagrama ER")
ventana.geometry("400x300")

label_instancia = tk.Label(ventana, text="Instancia:")
label_usuario = tk.Label(ventana, text="Usuario:")
label_contrasena = tk.Label(ventana, text="Contraseña:")
label_base_datos = tk.Label(ventana, text="Base de datos:")

entry_instancia = tk.Entry(ventana)
entry_usuario = tk.Entry(ventana)
entry_contrasena = tk.Entry(ventana, show="*")
entry_base_datos = tk.Entry(ventana)

btn_conectar = tk.Button(ventana, text="Conectar", command=conectar_base_datos)

label_instancia.grid(row=0, column=0, padx=10, pady=5, sticky="e")
label_usuario.grid(row=1, column=0, padx=10, pady=5, sticky="e")
label_contrasena.grid(row=2, column=0, padx=10, pady=5, sticky="e")
label_base_datos.grid(row=3, column=0, padx=10, pady=5, sticky="e")

entry_instancia.grid(row=0, column=1, padx=10, pady=5)
entry_usuario.grid(row=1, column=1, padx=10, pady=5)
entry_contrasena.grid(row=2, column=1, padx=10, pady=5)
entry_base_datos.grid(row=3, column=1, padx=10, pady=5)

btn_conectar.grid(row=4, column=0, columnspan=2, pady=10)

ventana.mainloop()
