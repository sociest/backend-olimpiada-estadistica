from datetime import date, datetime
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel, EstadoConvocatoria, EstadoTemporal
from app.modules.convocatorias.convocatoria_repository import ConvocatoriaRepository
from app.modules.convocatorias.convocatoria_schema import ConvocatoriaCreateDTO, ConvocatoriaUpdateDTO


class ConvocatoriaService:
    def __init__(self, db: Session):
        self.repository = ConvocatoriaRepository(db)

    def calculate_estado_temporal(self, convocatoria: ConvocatoriaModel) -> EstadoTemporal:
        if convocatoria.estado == EstadoConvocatoria.OCULTA:
            return EstadoTemporal.OCULTA
        if convocatoria.estado == EstadoConvocatoria.BORRADOR:
            return EstadoTemporal.BORRADOR
        if convocatoria.estado == EstadoConvocatoria.CANCELADA:
            return EstadoTemporal.CANCELADA

        if not all([convocatoria.inicio_olimpiadas, convocatoria.fin_olimpiadas, convocatoria.fecha_inicio_inscripcion, convocatoria.fecha_fin_inscripcion]):
            return EstadoTemporal.BORRADOR

        ahora = datetime.now()
        ahora_date = ahora.date()

        if ahora_date < convocatoria.inicio_olimpiadas:
            return EstadoTemporal.PROXIMA
        if ahora < convocatoria.fecha_inicio_inscripcion:
            return EstadoTemporal.INSCRIPCIONES_PROXIMAS
        if convocatoria.fecha_inicio_inscripcion <= ahora <= convocatoria.fecha_fin_inscripcion:
            return EstadoTemporal.INSCRIPCION_EN_CURSO
        if convocatoria.fecha_fin_inscripcion < ahora and ahora_date <= convocatoria.fin_olimpiadas:
            return EstadoTemporal.EN_CURSO
        
        return EstadoTemporal.FINALIZADA

    def _validate_fechas_logica(self, inicio_olimp, fin_olimp, inicio_insc, fin_insc):
        if inicio_olimp and fin_olimp and inicio_olimp > fin_olimp:
            raise BusinessRuleError("Inicio de olimpiadas debe ser anterior a la fecha de fin.")
        if inicio_insc and fin_insc and inicio_insc >= fin_insc:
            raise BusinessRuleError("Inicio de inscripción debe ser anterior a la fecha de fin de inscripción.")
        if inicio_olimp and inicio_insc and inicio_insc.date() < inicio_olimp:
            raise BusinessRuleError("El inicio de inscripción debe estar dentro del rango de la olimpiada.")
        if fin_olimp and fin_insc and fin_insc.date() > fin_olimp:
            raise BusinessRuleError("El fin de inscripción debe estar dentro del rango de la olimpiada.")

    def _validate_fechas_futuras(self, updates: dict):
        hoy = date.today()
        ahora = datetime.now()
        if "inicio_olimpiadas" in updates and updates["inicio_olimpiadas"] and updates["inicio_olimpiadas"] < hoy:
            raise BusinessRuleError("La fecha de inicio de olimpiadas no puede estar en el pasado.")
        if "fin_olimpiadas" in updates and updates["fin_olimpiadas"] and updates["fin_olimpiadas"] < hoy:
            raise BusinessRuleError("La fecha de fin de olimpiadas no puede estar en el pasado.")
        if "fecha_inicio_inscripcion" in updates and updates["fecha_inicio_inscripcion"] and updates["fecha_inicio_inscripcion"] < ahora:
            raise BusinessRuleError("El inicio de inscripción no puede estar en el pasado.")
        if "fecha_fin_inscripcion" in updates and updates["fecha_fin_inscripcion"] and updates["fecha_fin_inscripcion"] < ahora:
            raise BusinessRuleError("El fin de inscripción no puede estar en el pasado.")

    def _map_response(self, convocatoria: ConvocatoriaModel):
        data = convocatoria.__dict__.copy()
        data["estado_temporal"] = self.calculate_estado_temporal(convocatoria)
        return data

    def get_by_id(self, convocatoria_id: int):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")
        return self._map_response(convocatoria)

    def get_all(self, page: int, limit: int, estado: str = None, estado_temporal: str = None, start_date: datetime = None, end_date: datetime = None):
        skip = (page - 1) * limit
        items, total = self.repository.get_all(skip, limit, estado, start_date, end_date)
        
        mapped_items = [self._map_response(item) for item in items]
        
        if estado_temporal:
            mapped_items = [i for i in mapped_items if i["estado_temporal"] == estado_temporal]
            total = len(mapped_items)
            mapped_items = mapped_items[skip:skip+limit]

        return mapped_items, total

    def create(self, data: ConvocatoriaCreateDTO):
        if data.gestion < datetime.now().year:
            raise BusinessRuleError("La gestión debe ser igual o mayor al año en curso.")
        
        data.nombre_convocatoria = data.nombre_convocatoria.upper()
        self._validate_fechas_futuras(data.model_dump())
        self._validate_fechas_logica(data.inicio_olimpiadas, data.fin_olimpiadas, data.fecha_inicio_inscripcion, data.fecha_fin_inscripcion)

        conv_dict = data.model_dump()
        conv_dict["estado"] = EstadoConvocatoria.BORRADOR
        convocatoria = ConvocatoriaModel(**conv_dict)
        creada = self.repository.create(convocatoria)
        return self._map_response(creada)

    def update(self, convocatoria_id: int, data: ConvocatoriaUpdateDTO):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")

        if data.nombre_convocatoria:
            data.nombre_convocatoria = data.nombre_convocatoria.upper()
        
        updates = data.model_dump(exclude_unset=True)
        if not updates:
            return self._map_response(convocatoria)

        estado_temp = self.calculate_estado_temporal(convocatoria)
        allowed_fields = set()

        if convocatoria.estado == EstadoConvocatoria.CANCELADA:
            raise BusinessRuleError("No se puede editar una convocatoria CANCELADA.")
        elif convocatoria.estado == EstadoConvocatoria.BORRADOR:
            allowed_fields = {"nombre_convocatoria", "gestion", "descripcion", "inicio_olimpiadas", "fin_olimpiadas", "fecha_inicio_inscripcion", "fecha_fin_inscripcion", "monto_inscripcion"}
        elif convocatoria.estado == EstadoConvocatoria.OCULTA:
            allowed_fields = {"nombre_convocatoria", "descripcion"}
        elif convocatoria.estado == EstadoConvocatoria.PUBLICADA:
            allowed_fields = {"nombre_convocatoria", "descripcion"}
            if estado_temp == EstadoTemporal.PROXIMA:
                allowed_fields.update({"inicio_olimpiadas", "fin_olimpiadas", "fecha_inicio_inscripcion", "fecha_fin_inscripcion"})
            elif estado_temp == EstadoTemporal.INSCRIPCIONES_PROXIMAS:
                allowed_fields.update({"fecha_inicio_inscripcion", "fecha_fin_inscripcion", "fin_olimpiadas"})
            elif estado_temp in [EstadoTemporal.INSCRIPCION_EN_CURSO, EstadoTemporal.EN_CURSO]:
                allowed_fields.update({"fecha_fin_inscripcion", "fin_olimpiadas"})
            elif estado_temp == EstadoTemporal.FINALIZADA:
                raise BusinessRuleError("No se pueden editar fechas de una convocatoria FINALIZADA.")

        for key in updates.keys():
            if key not in allowed_fields:
                raise BusinessRuleError(f"El campo '{key}' no es editable en el estado actual ({estado_temp.value}).")

        self._validate_fechas_futuras(updates)

        new_inicio_olimp = updates.get("inicio_olimpiadas", convocatoria.inicio_olimpiadas)
        new_fin_olimp = updates.get("fin_olimpiadas", convocatoria.fin_olimpiadas)
        new_inicio_insc = updates.get("fecha_inicio_inscripcion", convocatoria.fecha_inicio_inscripcion)
        new_fin_insc = updates.get("fecha_fin_inscripcion", convocatoria.fecha_fin_inscripcion)

        self._validate_fechas_logica(new_inicio_olimp, new_fin_olimp, new_inicio_insc, new_fin_insc)

        if convocatoria.estado == EstadoConvocatoria.PUBLICADA and (new_inicio_olimp != convocatoria.inicio_olimpiadas or new_fin_olimp != convocatoria.fin_olimpiadas):
            if self.repository.check_overlap_fechas(new_inicio_olimp, new_fin_olimp, exclude_id=convocatoria.id_convocatoria):
                raise BusinessRuleError("Las nuevas fechas se superponen con otra convocatoria PUBLICADA.")

        for key, value in updates.items():
            setattr(convocatoria, key, value)

        actualizada = self.repository.update(convocatoria)
        return self._map_response(actualizada)

    def cambiar_estado(self, convocatoria_id: int, nuevo_estado: EstadoConvocatoria):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")

        estado_actual = convocatoria.estado

        if nuevo_estado == EstadoConvocatoria.BORRADOR:
            raise BusinessRuleError("No se puede regresar una convocatoria al estado BORRADOR.")

        if estado_actual == EstadoConvocatoria.CANCELADA:
            raise BusinessRuleError("Una convocatoria CANCELADA no puede cambiar de estado.")

        if nuevo_estado == EstadoConvocatoria.PUBLICADA:
            if estado_actual not in [EstadoConvocatoria.BORRADOR, EstadoConvocatoria.OCULTA]:
                raise BusinessRuleError(f"No se puede publicar desde {estado_actual.value}.")
            
            if not all([convocatoria.inicio_olimpiadas, convocatoria.fin_olimpiadas, convocatoria.fecha_inicio_inscripcion, convocatoria.fecha_fin_inscripcion, convocatoria.monto_inscripcion]):
                raise BusinessRuleError("Para publicar, todos los campos de fechas y monto deben estar completos.")
            
            if self.repository.check_overlap_fechas(convocatoria.inicio_olimpiadas, convocatoria.fin_olimpiadas, exclude_id=convocatoria.id_convocatoria):
                raise BusinessRuleError("No se puede publicar porque las fechas se superponen con otra convocatoria PUBLICADA activa.")

        if nuevo_estado in [EstadoConvocatoria.CANCELADA, EstadoConvocatoria.OCULTA]:
            if estado_actual != EstadoConvocatoria.PUBLICADA:
                raise BusinessRuleError(f"Solo se puede pasar a {nuevo_estado.value} desde PUBLICADA.")

        convocatoria.estado = nuevo_estado
        actualizada = self.repository.update(convocatoria)
        return self._map_response(actualizada)
    
    def delete(self, convocatoria_id: int):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")

        if convocatoria.estado == EstadoConvocatoria.PUBLICADA:
            raise BusinessRuleError("No se puede eliminar físicamente una convocatoria con estado PUBLICADA.")

        self.repository.delete(convocatoria)
        return {"id_convocatoria": convocatoria_id}