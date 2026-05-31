import csv
from io import StringIO
from typing import Tuple

from .exceptions import CSVFormatError, CSVValidationError
from .normalizer import normalize_column_name, map_column, normalize_observation
from .validators import validate_nota, validate_ci_present, validate_inscripcion

def parse_csv_file(text_content: str, dict_inscripciones: dict, dict_resultados: dict) -> Tuple[list, list, list, list, list]:
    csv_reader = csv.reader(StringIO(text_content))
    headers_raw = next(csv_reader, None)
    
    if not headers_raw:
        raise CSVFormatError("El archivo CSV está vacío.")

    col_idx_ci, col_idx_nota, col_idx_obs = -1, -1, -1
    
    for idx, h in enumerate(headers_raw):
        norm_h = map_column(normalize_column_name(h))
        if norm_h == "ci": col_idx_ci = idx
        elif norm_h == "nota": col_idx_nota = idx
        elif norm_h == "observaciones": col_idx_obs = idx

    if col_idx_ci == -1 or col_idx_nota == -1:
        raise CSVFormatError("El CSV debe contener columnas para Carnet de Identidad y Resultado/Nota.")

    validos_nuevos = []
    existentes = []
    errores = []
    filas_con_error_originales = []

    for row_num, row in enumerate(csv_reader, start=2):
        if not any(row):
            continue
        
        ci_raw = ""
        try:
            if len(row) <= max(col_idx_ci, col_idx_nota):
                raise CSVValidationError("La fila no tiene la cantidad de columnas requeridas.")

            ci_raw = row[col_idx_ci]
            nota_raw = row[col_idx_nota]
            obs_raw = row[col_idx_obs] if col_idx_obs != -1 and col_idx_obs < len(row) else ""

            ci = validate_ci_present(ci_raw)
            nota = validate_nota(nota_raw)
            obs = normalize_observation(obs_raw)
            
            id_insc = validate_inscripcion(ci, dict_inscripciones)
            
            if id_insc in dict_resultados:
                existentes.append({
                    "ci": ci,
                    "resultado_csv": nota,
                    "resultado_actual": dict_resultados[id_insc],
                    "id_inscripcion": id_insc,
                    "observaciones": obs
                })
            else:
                validos_nuevos.append({
                    "ci": ci,
                    "nota": nota,
                    "id_inscripcion": id_insc,
                    "observaciones": obs
                })

        except CSVValidationError as e:
            errores.append({"fila": row_num, "ci": ci_raw.strip(), "error": str(e)})
            filas_con_error_originales.append(row)
        except Exception as e:
            errores.append({"fila": row_num, "ci": ci_raw.strip(), "error": f"Error inesperado: {str(e)}"})
            filas_con_error_originales.append(row)

    return validos_nuevos, existentes, errores, filas_con_error_originales, headers_raw