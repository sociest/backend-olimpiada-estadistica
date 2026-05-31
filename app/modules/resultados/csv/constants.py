import os

TMP_DIR = os.path.join(os.getcwd(), "tmp")
ANALYSIS_DIR = os.path.join(TMP_DIR, "resultado_analizados")
ERRORS_DIR = os.path.join(TMP_DIR, "csv_resultado_errores")

CI_ALIASES = {
    "carnet_identidad", "carnet", "ci", "cedula", 
    "documento", "nro_documento", "numero_documento"
}

RESULTADO_ALIASES = {
    "resultado", "nota", "puntaje", "calificacion", "score"
}

OBSERVACIONES_ALIASES = {
    "observaciones", "observacion", "comentarios", "obs", "detalle"
}