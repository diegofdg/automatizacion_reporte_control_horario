import pandas as pd
import shutil
import os

PATH_CARPETA = r'D:\mis_proyectos\ciencia_de_datos\reporte_asistencias\automatizacion_reporte_control_horario'
PATH_OUTPUT = PATH_CARPETA + r'\outputs'
EXCEL_EMPLEADOS_PATH = PATH_CARPETA + r'\inputs\reporte_empleados_abril_2024.xlsx'

def eliminarCrearCarpetas(path):
    if os.path.exists(path):
        shutil.rmtree(path)

    os.mkdir(path)

def main():    
    eliminarCrearCarpetas(PATH_OUTPUT)    

    excel_horas_trabajadas = pd.read_excel(EXCEL_EMPLEADOS_PATH, sheet_name='HorasTrabajadas')
    print(excel_horas_trabajadas)
        
if __name__ == '__main__':
    main()