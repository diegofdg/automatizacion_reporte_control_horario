import matplotlib.pyplot as plt
import tempfile
import pandas as pd

dias_map = {
  'Monday': 'Lunes',
  'Tuesday': 'Martes',
  'Wednesday': 'Miércoles',
  'Thursday': 'Jueves',
  'Friday': 'Viernes',
  'Saturday': 'Sábado',
  'Sunday': 'Domingo'
}
orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

def grafico_barras(grupo):

    df = grupo.sort_values('Día')
    # FILTRAR días con horas > 0
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    horas = df['Trabajó'].dt.total_seconds() / 3600

    # Detectar faltas
    faltas_mask = df['Detalle'].str.contains(
        'FALTA REGISTRO DE ENTRADA O SALIDA',
        case=False,
        na=False
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()
    plt.bar(df['Día'].dt.strftime('%d/%m'), horas)
    # PUNTOS ROJOS (CLAVE)
    plt.scatter(
        df['Día'][faltas_mask].dt.strftime('%d/%m'),
        horas[faltas_mask],
        color='red'
    )
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_semana(grupo):

    df = grupo.copy()
    # ✅ eliminar días 0
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    df['dia_semana'] = df['Día'].dt.day_name().map(dias_map)

    resumen = df.groupby('dia_semana')['Trabajó'].mean()
    resumen = resumen.reindex(orden_dias)

    horas = resumen.dt.total_seconds() / 3600

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()
    plt.bar(resumen.index, horas)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_histograma(grupo):
    df = grupo.copy()
    # ✅ eliminar ceros
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    horas = grupo['Trabajó'].dt.total_seconds() / 3600

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()
    plt.hist(horas, bins=10)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_cumplimiento(cumplimiento):

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()
    plt.barh(['Cumplimiento'], [cumplimiento * 100])
    plt.xlim(0, 120)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_linea(grupo):
    import matplotlib.pyplot as plt
    import tempfile
    import pandas as pd

    df = grupo.sort_values('Día')

    # filtrar días válidos
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    horas = df['Trabajó'].dt.total_seconds() / 3600
    horas_min = grupo['Horas minimas'].iloc[0]
    objetivo = horas_min.total_seconds() / 3600 / 20

    # detectar faltas
    faltas_mask = df['Detalle'].str.contains(
        'FALTA REGISTRO DE ENTRADA O SALIDA',
        case=False,
        na=False
    )

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()

    # línea principal
    plt.plot(df['Día'].dt.strftime('%d/%m'), horas, marker='o')

    # puntos rojos
    plt.scatter(
        df['Día'][faltas_mask].dt.strftime('%d/%m'),
        horas[faltas_mask],
        color='red'
    )

    plt.axhline(y=objetivo, linestyle='--', label=f'Objetivo ({objetivo:.1f}h)')
    plt.legend()

    plt.xticks(rotation=45)
    plt.title("Horas trabajadas por día")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_semana_pro(grupo):
    
    import matplotlib.pyplot as plt
    import tempfile
    import pandas as pd

    dias_map = {
        'Monday': 'Lunes',
        'Tuesday': 'Martes',
        'Wednesday': 'Miércoles',
        'Thursday': 'Jueves',
        'Friday': 'Viernes'
    }

    orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']

    df = grupo.copy()
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    df['dia_semana'] = df['Día'].dt.day_name().map(dias_map)

    resumen = df.groupby('dia_semana')['Trabajó'].mean().reindex(orden)
    resumen = resumen.fillna(pd.Timedelta(0))

    horas = resumen.dt.total_seconds() / 3600
    horas_min = grupo['Horas minimas'].iloc[0]
    objetivo = horas_min.total_seconds() / 3600 / 20

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()

    plt.bar(resumen.index, horas)

    plt.axhline(y=objetivo, linestyle='--', label=f'Objetivo ({objetivo:.1f}h)')
    plt.legend()

    plt.title("Promedio por día de la semana")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_boxplot(grupo):
    import matplotlib.pyplot as plt
    import tempfile
    import pandas as pd

    df = grupo.copy()
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    horas = df['Trabajó'].dt.total_seconds() / 3600

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()

    plt.boxplot(horas, vert=False)

    plt.title("Distribución de horas trabajadas")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_cumplimiento_pro(cumplimiento):
    import matplotlib.pyplot as plt
    import tempfile

    valor = cumplimiento * 100

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    plt.figure()

    # color según nivel
    if valor < 90:
        color = 'red'
    elif valor <= 100:
        color = 'orange'
    else:
        color = 'green'

    plt.barh(['Cumplimiento'], [valor])

    plt.xlim(0, 120)
    plt.title(f"{valor:.1f}%")
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_semanal(grupo):
    import matplotlib.pyplot as plt
    import tempfile
    import pandas as pd

    df = grupo.copy()
    df['Día'] = pd.to_datetime(df['Día'])

    # =========================
    # 🧠 CALENDARIO COMPLETO
    # =========================

    primer_dia = df['Día'].min().replace(day=1)
    ultimo_dia = (primer_dia + pd.offsets.MonthEnd(0))

    calendario = pd.DataFrame({
        'Día': pd.date_range(primer_dia, ultimo_dia, freq='D')
    })

    # =========================
    # 🔗 MERGE con datos reales
    # =========================

    df['horas'] = df['Trabajó'].dt.total_seconds() / 3600

    df = calendario.merge(df[['Día', 'horas']], on='Día', how='left')
    df['horas'] = df['horas'].fillna(0)

    # =========================
    # 📆 SEMANAS CUSTOM
    # =========================

    def calcular_semana(fecha):
        delta = (fecha - primer_dia).days
        offset = primer_dia.weekday()
        primer_tramo = 6 - offset

        if delta <= primer_tramo:
            return 0
        else:
            return 1 + (delta - primer_tramo - 1) // 7

    df['semana'] = df['Día'].apply(calcular_semana)

    # =========================
    # 📊 AGRUPAR
    # =========================

    resumen = df.groupby('semana').agg({
        'horas': 'sum',
        'Día': ['min', 'max']
    })

    resumen.columns = ['horas', 'fecha_inicio', 'fecha_fin']

    # ✅ etiquetas REALES (no dependen de datos)
    resumen['label'] = resumen.apply(
        lambda x: f"{x['fecha_inicio'].strftime('%d')}–{x['fecha_fin'].strftime('%d')}",
        axis=1
    )

    # =========================
    # 🎯 OBJETIVO
    # =========================

    horas_min = grupo['Horas minimas'].iloc[0]
    objetivo = horas_min.total_seconds() / 3600 / 4

    # =========================
    # 📁 ARCHIVO
    # =========================

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    # =========================
    # 📈 GRÁFICO
    # =========================

    plt.figure()

    plt.bar(resumen['label'], resumen['horas'])

    plt.axhline(
        y=objetivo,
        linestyle='--',
        label=f'Objetivo ({objetivo:.1f}h)'
    )

    plt.xticks(rotation=45)
    plt.ylabel("Horas trabajadas")
    plt.title("Horas trabajadas por semana")

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path