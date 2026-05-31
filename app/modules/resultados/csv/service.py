import csv
import json
import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.resultados.resultado_model import EstadoResultado, ResultadoModel
from app.modules.resultados.resultado_repository import ResultadoRepository
from .constants import ANALYSIS_DIR, ERRORS_DIR
from .schemas import AnalisisImportacionResponseDTO, ConfirmarImportacionDTO
from .parser import parse_csv_file
from .exceptions import CSVFormatError

os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(ERRORS_DIR, exist_ok=True)

class CSVImportService:
    def __init__(self, db: Session):
        self.repository = ResultadoRepository(db)

    async def analizar_csv(self, id_fase_prueba: int, file: UploadFile) -> AnalisisImportacionResponseDTO:
        id_categoria, dict_inscripciones, dict_resultados = self.repository.get_contexto_importacion(id_fase_prueba)
        if id_categoria is None:
            raise NotFoundError("Fase de prueba no encontrada o no es válida.")

        content = await file.read()
        try:
            text_content = content.decode("utf-8")
        except UnicodeDecodeError:
            text_content = content.decode("latin-1")

        try:
            validos_nuevos, existentes, errores, filas_con_error_originales, headers_raw = parse_csv_file(
                text_content, dict_inscripciones, dict_resultados
            )
        except CSVFormatError as e:
            raise BusinessRuleError(str(e))

        archivo_errores_nombre = None
        if errores:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo_errores_nombre = f"resultado_import_errors_{timestamp}.csv"
            ruta_errores = os.path.join(ERRORS_DIR, archivo_errores_nombre)
            with open(ruta_errores, mode="w", newline="", encoding="utf-8") as err_file:
                err_writer = csv.writer(err_file)
                err_writer.writerow(headers_raw + ["ERROR_DETALLE"])
                for row_orig, error_obj in zip(filas_con_error_originales, errores):
                    err_writer.writerow(row_orig + [error_obj["error"]])

        token = f"resultado_import_{uuid.uuid4().hex}.json"
        ruta_analisis = os.path.join(ANALYSIS_DIR, token)
        analisis_data = {
            "id_fase_prueba": id_fase_prueba,
            "id_categoria": id_categoria,
            "validos_nuevos": validos_nuevos,
            "existentes": existentes
        }
        with open(ruta_analisis, "w", encoding="utf-8") as f:
            json.dump(analisis_data, f)

        return AnalisisImportacionResponseDTO(
            token=token,
            validos_nuevos=validos_nuevos,
            existentes=existentes,
            errores=errores,
            archivo_errores=archivo_errores_nombre
        )

    def procesar_importacion(self, id_fase_prueba: int, payload: ConfirmarImportacionDTO) -> dict:
        ruta_analisis = os.path.join(ANALYSIS_DIR, payload.token)
        if not os.path.exists(ruta_analisis):
            raise NotFoundError("Token de análisis caducado o inválido.")

        with open(ruta_analisis, "r", encoding="utf-8") as f:
            analisis_data = json.load(f)

        if analisis_data["id_fase_prueba"] != id_fase_prueba:
            raise BusinessRuleError("El token no corresponde a la fase especificada.")

        id_categoria = analisis_data["id_categoria"]
        nuevos = []
        actualizados_count = 0

        for row in analisis_data["validos_nuevos"]:
            nuevos.append(ResultadoModel(
                id_categoria=id_categoria,
                id_fase_prueba=id_fase_prueba,
                id_inscripcion=row["id_inscripcion"],
                nota=row["nota"],
                observaciones=row["observaciones"],
                estado=EstadoResultado.BORRADOR
            ))

        if nuevos:
            self.repository.bulk_save(nuevos)

        if payload.sobreescribir_existentes and analisis_data["existentes"]:
            resultados_db = {
                r.id_inscripcion: r for r in self.repository.get_all_by_fase(id_fase_prueba)
            }
            
            for row in analisis_data["existentes"]:
                res_model = resultados_db.get(row["id_inscripcion"])
                if res_model:
                    res_model.nota = row["resultado_csv"]
                    res_model.observaciones = row["observaciones"]
                    res_model.estado = EstadoResultado.BORRADOR
                    actualizados_count += 1
            
            if actualizados_count > 0:
                self.repository.bulk_update()

        os.remove(ruta_analisis)

        return {
            "nuevos_creados": len(nuevos),
            "existentes_actualizados": actualizados_count
        }