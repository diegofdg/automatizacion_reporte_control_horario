import matplotlib.pyplot as plt
import tempfile
import pandas as pd

from utils.text_utils import es_falta

# =========================
# 🧰 HELPERS
# =========================

def crear_temp_png():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()
    return path


def a_horas(series):
    return series.dt.total_seconds() / 3600


def calcular_objetivo(grupo, divisor):
    if grupo.empty:
        return 0
    horas_min = grupo['Horas minimas'].iloc[0]
    return horas_min.total_seconds() / 3600 / divisor


def preparar_df(grupo, eliminar_ceros=True):
    df = grupo.copy()
    df = df.sort_values('Día')

    if eliminar_ceros:
        df = df[df['Trabajó'] > pd.Timedelta(0)]

    return df


# =========================
# 📊 GRAFICO LINEA (principal)
# =========================

def grafico_linea(grupo):
    df = preparar_df(grupo)

    if df.empty:
        return None

    horas = a_horas(df['Trabajó'])
    objetivo = calcular_objetivo(grupo, 20)

    faltas_mask = df['Detalle'].apply(es_falta)

    path = crear_temp_png()

    plt.figure()

    plt.plot(df['Día'].dt.strftime('%d/%m'), horas, marker='o')

    plt.scatter(
        df['Día'][faltas_mask].dt.strftime('%d/%m'),
        horas[faltas_mask],
        color='red'
    )

    plt.axhline(y=objetivo, linestyle='--', label=f'Objetivo ({objetivo:.1f}h)')
    plt.legend()

    plt.title("Horas trabajadas por día")
    plt.ylabel("Horas")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


# =========================
# 📊 GRAFICO SEMANA (promedio)
# =========================

dias_map = {
    'Monday': 'Lunes',
    'Tuesday': 'Martes',
    'Wednesday': 'Miércoles',
    'Thursday': 'Jueves',
    'Friday': 'Viernes'
}

orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']


def grafico_semana_pro(grupo):
    df = preparar_df(grupo)

    if df.empty:
        return None

    df['dia_semana'] = df['Día'].dt.day_name().map(dias_map)

    resumen = (
        df.groupby('dia_semana')['Trabajó']
        .mean()
        .reindex(orden_dias)
        .fillna(pd.Timedelta(0))
    )

    horas = a_horas(resumen)
    objetivo = calcular_objetivo(grupo, 20)

    path = crear_temp_png()

    plt.figure()

    plt.bar(resumen.index, horas)

    plt.axhline(y=objetivo, linestyle='--', label=f'Objetivo ({objetivo:.1f}h)')
    plt.legend()

    plt.title("Promedio por día de la semana")
    plt.ylabel("Horas")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


# =========================
# 📊 HISTOGRAMA
# =========================

def grafico_histograma(grupo):
    df = preparar_df(grupo)

    if df.empty:
        return None

    horas = a_horas(df['Trabajó'])

    path = crear_temp_png()

    plt.figure()

    plt.hist(horas, bins=10)

    plt.title("Distribución de horas trabajadas")
    plt.xlabel("Horas")
    plt.ylabel("Frecuencia")

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


# =========================
# 📊 BOXPLOT
# =========================

def grafico_boxplot(grupo):
    df = preparar_df(grupo)

    if df.empty:
        return None

    horas = a_horas(df['Trabajó'])

    path = crear_temp_png()

    plt.figure()

    plt.boxplot(horas, vert=False)

    plt.title("Distribución de horas trabajadas")

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


# =========================
# 📊 CUMPLIMIENTO PRO
# =========================

def grafico_cumplimiento_pro(cumplimiento):
    valor = cumplimiento * 100

    path = crear_temp_png()

    plt.figure()

    if valor < 90:
        color = 'red'
    elif valor <= 100:
        color = 'orange'
    else:
        color = 'green'

    plt.barh(['Cumplimiento'], [valor], color=color)

    plt.xlim(0, 120)
    plt.title(f"{valor:.1f}%")

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path


# =========================
# 📊 GRAFICO SEMANAL (CALENDARIO REAL)
# =========================

def grafico_semanal(grupo):
    df = grupo.copy()
    df['Día'] = pd.to_datetime(df['Día'])

    # 📅 calendario completo del mes
    primer_dia = df['Día'].min().replace(day=1)
    ultimo_dia = primer_dia + pd.offsets.MonthEnd(0)

    calendario = pd.DataFrame({
        'Día': pd.date_range(primer_dia, ultimo_dia, freq='D')
    })

    df['horas'] = a_horas(df['Trabajó'])

    df = calendario.merge(df[['Día', 'horas']], on='Día', how='left')
    df['horas'] = df['horas'].fillna(0)

    # 🧠 semanas custom
    def calcular_semana(fecha):
        delta = (fecha - primer_dia).days
        offset = primer_dia.weekday()
        primer_tramo = 6 - offset

        if delta <= primer_tramo:
            return 0
        return 1 + (delta - primer_tramo - 1) // 7

    df['semana'] = df['Día'].apply(calcular_semana)

    resumen = df.groupby('semana').agg({
        'horas': 'sum',
        'Día': ['min', 'max']
    })

    resumen.columns = ['horas', 'fecha_inicio', 'fecha_fin']

    resumen['label'] = resumen.apply(
        lambda x: f"{x['fecha_inicio'].strftime('%d')}–{x['fecha_fin'].strftime('%d')}",
        axis=1
    )

    objetivo = calcular_objetivo(grupo, 4)

    path = crear_temp_png()

    plt.figure()

    plt.bar(resumen['label'], resumen['horas'])

    plt.axhline(y=objetivo, linestyle='--', label=f'Objetivo ({objetivo:.1f}h)')

    plt.title("Horas trabajadas por semana")
    plt.ylabel("Horas")
    plt.xticks(rotation=45)

    plt.legend()

    plt.tight_layout()
    plt.savefig(path)
    plt.close()

    return path