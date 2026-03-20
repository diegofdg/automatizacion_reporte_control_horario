import pandas as pd
from datetime import timedelta

ZERO = pd.Timedelta(0)


def calcular_kpis(grupo, total, horas_min):
    trabajados_df = grupo[grupo['Trabajó'] > ZERO]
    trabajados = trabajados_df['Trabajó']

    dias_trabajados = trabajados_df['Día'].nunique()

    promedio = total / dias_trabajados if dias_trabajados else ZERO

    max_dia = trabajados.max() if not trabajados.empty else ZERO
    min_dia = trabajados.min() if not trabajados.empty else ZERO

    cumplimiento = (
        total / horas_min
        if horas_min > ZERO
        else 0.0
    )

    return {
        'dias_trabajados': dias_trabajados,
        'promedio': promedio,
        'max_dia': max_dia,
        'min_dia': min_dia,
        'cumplimiento_pct': cumplimiento
    }


def calcular_estado(diff):
    if diff >= timedelta(0):
        return "OK"
    elif diff >= -timedelta(hours=2):
        return "LEVE DESVÍO"
    else:
        return "CRÍTICO"


def calcular_color(diff, VERDE, AMARILLO, ROJO):
    if diff >= timedelta(0):
        return VERDE
    elif diff >= -timedelta(hours=2):
        return AMARILLO
    else:
        return ROJO


def analizar_anomalias(grupo):
    trabajo = grupo['Trabajó']

    dias_bajos = ((trabajo > ZERO) & (trabajo < pd.Timedelta(hours=4))).sum()
    dias_altos = (trabajo > pd.Timedelta(hours=10)).sum()
    dias_cero = (trabajo == ZERO).sum()

    faltas_registro = grupo['Detalle'].str.contains(
        'FALTA REGISTRO DE ENTRADA O SALIDA',
        case=False,
        na=False
    ).sum()

    return {
        'dias_bajos': dias_bajos,
        'dias_altos': dias_altos,
        'dias_cero': dias_cero,
        'faltas_registro': faltas_registro
    }


def generar_comentario(diff, dias_bajos):
    if diff > timedelta(0):
        return "Excelente desempeño, superó las horas requeridas."
    elif diff < timedelta(0):
        if dias_bajos > 3:
            return "Se detectan múltiples jornadas sin asistencia. Se recomienda revisión."
        return "No se alcanzaron las horas mínimas."
    else:
        return "Cumplimiento correcto."