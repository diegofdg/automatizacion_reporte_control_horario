import matplotlib.pyplot as plt
import tempfile
import pandas as pd

def grafico_barras(grupo):

    df = grupo.sort_values('Día')
    # ✅ FILTRAR días con horas > 0
    df = df[df['Trabajó'] > pd.Timedelta(0)]

    horas = df['Trabajó'].dt.total_seconds() / 3600

    # 🔴 detectar faltas
    faltas_mask = df['Detalle'].str.contains(
        'FALTA REGISTRO DE ENTRADA O SALIDA',
        case=False,
        na=False
    )

    path = tempfile.mktemp(suffix=".png")

    plt.figure()
    plt.bar(df['Día'].dt.strftime('%d/%m'), horas)
    # 🔴 PUNTOS ROJOS (CLAVE)
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

    df['dia_semana'] = df['Día'].dt.day_name()

    resumen = df.groupby('dia_semana')['Trabajó'].mean()

    horas = resumen.dt.total_seconds() / 3600

    path = tempfile.mktemp(suffix=".png")

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

    path = tempfile.mktemp(suffix=".png")

    plt.figure()
    plt.hist(horas, bins=10)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path

def grafico_cumplimiento(cumplimiento):
    import matplotlib.pyplot as plt
    import tempfile

    path = tempfile.mktemp(suffix=".png")

    plt.figure()
    plt.barh(['Cumplimiento'], [cumplimiento * 100])
    plt.xlim(0, 120)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path