import pandas as pd
import shutil
import os
from docxtpl import DocxTemplate
import datetime

PATH_CARPETA = r'D:\mis_proyectos\ciencia_de_datos\reporte_asistencias\automatizacion_reporte_control_horario'
PATH_OUTPUT = PATH_CARPETA + r'\outputs'
EXCEL_EMPLEADOS_PATH = PATH_CARPETA + r'\inputs\reporte_empleados_abril_2024.xlsx'
WORD_EMPLEADOS_PATH = PATH_CARPETA + r'\inputs\plantilla_horas.docx'

def eliminarCrearCarpetas(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.mkdir(path)

def normalizarNombre(nombre):
    nombre_normalizado = nombre.replace(',', '')
    nombre_normalizado = nombre_normalizado.upper()
    acentos_dict = {
        'Á': 'A',
        'É': 'E',
        'Í': 'I',
        'Ó': 'O',
        'Ú': 'U',
    }
    for key in acentos_dict:
        nombre_normalizado = nombre_normalizado.replace(key, acentos_dict[key])
    return nombre_normalizado

def cambiarMayusculas(nombre):
    return nombre.upper()

def formatearFecha(fecha):
    fecha_original = datetime.datetime.strptime(fecha, "%Y-%m-%d %H:%M:%S")
    return fecha_original.strftime('%d/%m/%Y')
    
def convertirHoras(horas):
    total_en_segundos = horas.total_seconds()
    horas = str(int(total_en_segundos // 3600)).zfill(2)
    minutos = str(int((total_en_segundos % 3600) // 60)).zfill(2)
    segundos = str(int(total_en_segundos % 60)).zfill(2)
    return f"{horas}:{minutos}:{segundos}"
    
def main():
    eliminarCrearCarpetas(PATH_OUTPUT)    
    horas_empleados = pd.read_excel(EXCEL_EMPLEADOS_PATH, sheet_name='HorasTrabajadas')
    nombres_empleados = pd.read_excel(EXCEL_EMPLEADOS_PATH, sheet_name='ListadoEmpleados')
    horas_minimas = pd.read_excel(EXCEL_EMPLEADOS_PATH, sheet_name='HorasMinimas')
    empleados_list = sorted(list(nombres_empleados['Nombre']))
    
    for nombre_empleado in empleados_list:      
        docs_tpl = DocxTemplate(WORD_EMPLEADOS_PATH)  
        filtro_horas_empleados = horas_empleados[(horas_empleados['Nombre'] == nombre_empleado)]
        nombre_normalizado = normalizarNombre(nombre_empleado)
        horas_trabajadas_list = []
        suma_horas_trabajadas = pd.Timedelta(days=0, hours=0, minutes=0)
        
        filtro_horas_minimas = horas_minimas[(horas_minimas['Nombre'] == nombre_empleado)]
        horas_minimas_a_trabajar = filtro_horas_minimas.iloc[0]['Horas Minimas']
        
        for index in range(60):
            try:
                horas_trabajadas = filtro_horas_empleados.iloc[index]['Trabajó']
                suma_horas_trabajadas = suma_horas_trabajadas + horas_trabajadas
                empleado_dict = {
                    'Fecha': formatearFecha(str(filtro_horas_empleados.iloc[index]['Fecha'])),           
                    'Nombre': nombre_normalizado,
                    'Legajo': str(filtro_horas_empleados.iloc[index]['Legajo']),
                    'Entrada': str(filtro_horas_empleados.iloc[index]['Entrada']),
                    'Salida': str(filtro_horas_empleados.iloc[index]['Salida']),
                    'Concepto': str(filtro_horas_empleados.iloc[index]['Concepto']),
                    'Trabajo': str(convertirHoras(horas_trabajadas)),
                }
                horas_trabajadas_list.append(empleado_dict)
                
            except IndexError:
                print("Error: Index out of range. Please provide a valid index.")
                break
        
        context = {
            'fecha': datetime.datetime.now().strftime("%d/%m/%Y"),
            'periodo': "ABRIL 2024",
            'nombre_empleado': nombre_normalizado,
            'horas_trabajadas': convertirHoras(suma_horas_trabajadas),
            'horas_minimas': convertirHoras(horas_minimas_a_trabajar),
            'horas_trabajadas_list' : horas_trabajadas_list
        }
        
        # Renderizamos el documento
        docs_tpl.render(context)
        titulo = 'RESUMEN_' + nombre_normalizado
        titulo = titulo.upper()
        #titulo = eliminarTildes(titulo)
        titulo = titulo.replace(" ", "_")
        titulo += '.docx'
        
        # Guardamos el documento
        docs_tpl.save(PATH_OUTPUT + '\\' + titulo)
        
if __name__ == '__main__':
    main()