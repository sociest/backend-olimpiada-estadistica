from datetime import date, datetime
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.modules.convocatorias.convocatoria_model import ConvocatoriaModel, EstadoConvocatoria, EstadoTemporal
from app.modules.convocatorias.convocatoria_repository import ConvocatoriaRepository
from app.modules.convocatorias.convocatoria_schema import ConvocatoriaCreateDTO, ConvocatoriaUpdateDTO, ConvocatoriaResponseDTO
# al inicio de convocatoria_service.py, agregá:
from app.modules.materiales.material_repository import MaterialRepository
from app.modules.materiales.material_model import EstadoMaterial, TipoMaterialEnum
from app.modules.sistema.sistema_model import AuditoriaModel, TipoAccion, TipoModulo
from app.modules.sistema.sistema_repository import SistemaRepository

class ConvocatoriaService:
    def __init__(self, db: Session):
        self.repository = ConvocatoriaRepository(db)
        self.material_repo = MaterialRepository(db)
        self.sistema_repository = SistemaRepository(db)
        
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
        data = {}
        for column in convocatoria.__table__.columns:
            data[column.name] = getattr(convocatoria, column.name)
        
        data["estado_temporal"] = self.calculate_estado_temporal(convocatoria)
        
        return ConvocatoriaResponseDTO.model_validate(data).model_dump()

    def get_by_id(self, convocatoria_id: int):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")
        return self._map_response(convocatoria)

    def get_all(self, page: int, limit: int, estado: EstadoConvocatoria = None, estado_temporal: EstadoTemporal = None, start_date: datetime = None, end_date: datetime = None):
        skip = (page - 1) * limit
        items, total = self.repository.get_all(skip, limit, estado, start_date, end_date)
        
        mapped_items = [self._map_response(item) for item in items]
        
        if estado_temporal:
            mapped_items = [i for i in mapped_items if i["estado_temporal"] == estado_temporal]
            total = len(mapped_items)
            mapped_items = mapped_items[skip:skip+limit]

        return mapped_items, total

    def create(self, data: ConvocatoriaCreateDTO, current_admin_id: int):
        if data.gestion < datetime.now().year:
            raise BusinessRuleError("La gestión debe ser igual o mayor al año en curso.")
        
        data.nombre_convocatoria = data.nombre_convocatoria.upper()
        self._validate_fechas_futuras(data.model_dump())
        self._validate_fechas_logica(data.inicio_olimpiadas, data.fin_olimpiadas,
                                    data.fecha_inicio_inscripcion, data.fecha_fin_inscripcion)

        if data.inicio_olimpiadas and data.fin_olimpiadas:
            if self.repository.check_overlap_fechas_global(
                data.inicio_olimpiadas, data.fin_olimpiadas
            ):
                raise BusinessRuleError(
                    "Las fechas de la olimpiada se solapan con otra convocatoria PUBLICADA."
                )

        conv_dict = data.model_dump()
        conv_dict["estado"] = EstadoConvocatoria.BORRADOR
        convocatoria = ConvocatoriaModel(**conv_dict)
        creada = self.repository.create(convocatoria)
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=TipoAccion.CREAR,
                modulo=TipoModulo.CONVOCATORIA,
                descripcion=f"Convocatoria creada {creada.nombre_convocatoria} gestion {creada.gestion}",
            )
        )
        return self._map_response(creada)

    def update(self, convocatoria_id: int, data: ConvocatoriaUpdateDTO, current_admin_id: int):
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
            allowed_fields = {"nombre_convocatoria", "gestion", "descripcion", "inicio_olimpiadas",
                            "fin_olimpiadas", "fecha_inicio_inscripcion", "fecha_fin_inscripcion", "monto_inscripcion"}
        elif convocatoria.estado == EstadoConvocatoria.OCULTA:
            allowed_fields = {"nombre_convocatoria", "descripcion"}
        elif convocatoria.estado == EstadoConvocatoria.PUBLICADA:
            allowed_fields = {"nombre_convocatoria", "descripcion"}
            if estado_temp == EstadoTemporal.PROXIMA:
                allowed_fields.update({"inicio_olimpiadas", "fin_olimpiadas",
                                    "fecha_inicio_inscripcion", "fecha_fin_inscripcion"})
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

        if new_inicio_olimp != convocatoria.inicio_olimpiadas or new_fin_olimp != convocatoria.fin_olimpiadas:
            if self.repository.check_overlap_fechas_global(
                new_inicio_olimp, new_fin_olimp, exclude_id=convocatoria.id_convocatoria
            ):
                raise BusinessRuleError("Las nuevas fechas se solapan con otra convocatoria PUBLICADA.")

        for key, value in updates.items():
            setattr(convocatoria, key, value)

        actualizada = self.repository.update(convocatoria)
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=TipoAccion.ACTUALIZAR,
                modulo=TipoModulo.CONVOCATORIA,
                descripcion=f"Convocatoria actualizada {actualizada.nombre_convocatoria} gestion {actualizada.gestion}",
            )
        )
        return self._map_response(actualizada)

    def cambiar_estado(self, convocatoria_id: int, nuevo_estado: EstadoConvocatoria, current_admin_id: int):
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
            
            if (convocatoria.inicio_olimpiadas is None or
                convocatoria.fin_olimpiadas is None or
                convocatoria.fecha_inicio_inscripcion is None or
                convocatoria.fecha_fin_inscripcion is None or
                convocatoria.monto_inscripcion is None):
                raise BusinessRuleError("Para publicar, todos los campos de fechas y monto deben estar completos.")
            
            if self.repository.check_overlap_fechas_global(
                convocatoria.inicio_olimpiadas,
                convocatoria.fin_olimpiadas,
                exclude_id=convocatoria.id_convocatoria
            ):
                raise BusinessRuleError("Las fechas se solapan con otra convocatoria PUBLICADA.")
            self._validar_materiales_principales(convocatoria.id_convocatoria)
        
        if nuevo_estado in [EstadoConvocatoria.CANCELADA, EstadoConvocatoria.OCULTA]:
            if estado_actual != EstadoConvocatoria.PUBLICADA:
                raise BusinessRuleError(f"Solo se puede pasar a {nuevo_estado.value} desde PUBLICADA.")

        convocatoria.estado = nuevo_estado
        actualizada = self.repository.update(convocatoria)
        accion = TipoAccion.ACTUALIZAR
        if nuevo_estado == EstadoConvocatoria.PUBLICADA:
            accion = TipoAccion.PUBLICAR
        elif nuevo_estado == EstadoConvocatoria.OCULTA:
            accion = TipoAccion.OCULTAR

        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=accion,
                modulo=TipoModulo.CONVOCATORIA,
                descripcion=f"Convocatoria {actualizada.nombre_convocatoria} cambio estado de {estado_actual} a {nuevo_estado}",
            )
        )
        return self._map_response(actualizada)
    
    def delete(self, convocatoria_id: int, current_admin_id: int):
        convocatoria = self.repository.get_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada")

        if convocatoria.estado == EstadoConvocatoria.PUBLICADA:
            raise BusinessRuleError("No se puede eliminar físicamente una convocatoria con estado PUBLICADA.")

        descripcion = f"Convocatoria eliminada {convocatoria.nombre_convocatoria} gestion {convocatoria.gestion}"
        self.repository.delete(convocatoria)
        self.sistema_repository.create_auditoria(
            AuditoriaModel(
                id_administrador=current_admin_id,
                accion=TipoAccion.ELIMINAR,
                modulo=TipoModulo.CONVOCATORIA,
                descripcion=descripcion,
            )
        )
        return {"id_convocatoria": convocatoria_id}
    
    def _validar_materiales_principales(self, convocatoria_id: int):
        tipos = [TipoMaterialEnum.AFICHE, TipoMaterialEnum.CONVOCATORIA, TipoMaterialEnum.REGLAMENTO]
        faltantes = []
        for tipo in tipos:
            material = self.material_repo.get_material_principal(convocatoria_id, tipo)
            if not material or material.estado != EstadoMaterial.PUBLICO:
                faltantes.append(tipo.value)
        if faltantes:
            raise BusinessRuleError(
                f"Faltan los siguientes materiales principales (o no están en estado PUBLICO): {', '.join(faltantes)}"
            )

    def get_convocatoria_principal(self):
        convocatoria = self.repository.get_convocatoria_principal()
        if not convocatoria:
            raise NotFoundError("No hay ninguna convocatoria principal en este momento")
        return self._map_response(convocatoria)
     
    def get_convocatoria_activa(self):
        convocatoria = self.repository.get_convocatoria_activa()
        if not convocatoria:
            raise NotFoundError("No hay ninguna convocatoria activa en este momento")
        return self._map_response(convocatoria)
    
    def get_convocatoria_principal_id(self) -> int:
        convocatoria = self.repository.get_convocatoria_principal()
        if not convocatoria:
            raise NotFoundError("No hay ninguna convocatoria principal en este momento")
        return convocatoria.id_convocatoria

    def get_inicio_publico(self) -> dict:
        convocatoria = self.repository.get_convocatoria_principal()
        if not convocatoria:
            raise NotFoundError("No hay ninguna convocatoria principal en este momento")
        
        return self._construir_detalle_publico(
            convocatoria, 
            tipos_materiales=[TipoMaterialEnum.AFICHE, TipoMaterialEnum.CONVOCATORIA]
        )

    def get_detalle_publico(self, convocatoria_id: int) -> dict:
        convocatoria = self.repository.get_public_by_id(convocatoria_id)
        if not convocatoria:
            raise NotFoundError("Convocatoria no encontrada o no está publicada")
            
        return self._construir_detalle_publico(
            convocatoria, 
            tipos_materiales=[TipoMaterialEnum.AFICHE, TipoMaterialEnum.CONVOCATORIA, TipoMaterialEnum.REGLAMENTO]
        )

    def get_lista_publica(self) -> list:
        convocatorias = self.repository.get_public_convocatorias_list()
        return [
            {
                "id_convocatoria": c.id_convocatoria,
                "nombre_convocatoria": c.nombre_convocatoria,
                "gestion": c.gestion,
                "descripcion": c.descripcion,
                "inicio_olimpiadas": c.inicio_olimpiadas,
                "fin_olimpiadas": c.fin_olimpiadas
            }
            for c in convocatorias
        ]

    def _construir_detalle_publico(self, convocatoria: ConvocatoriaModel, tipos_materiales: list) -> dict:
        base_data = self._map_response(convocatoria)
        
        base_data["categorias"] = [
            {
                "id_categoria": cat.id_categoria,
                "nombre_categoria": cat.nombre_categoria,
                "curso": str(cat.curso),
                "nivel": cat.nivel
            }
            for cat in convocatoria.categorias
        ]
        
        materiales = {}
        for tipo in tipos_materiales:
            mat = self.material_repo.get_material_principal(convocatoria.id_convocatoria, tipo)
            if mat and mat.estado == EstadoMaterial.PUBLICO:
                materiales[tipo.name.lower()] = {
                    "nombre": mat.nombre_material,
                    "enlace_acceso": mat.enlace_acceso
                }
            else:
                materiales[tipo.name.lower()] = None
                
        base_data["material_principal"] = materiales
        return base_data

    def get_public_minified_list(self) -> list:
        items = self.repository.get_public_minified_list()
        items_mapped = []
        for item in items:
            estado_temporal = self.calculate_estado_temporal(item)
            if(estado_temporal == EstadoTemporal.FINALIZADA):
                items_mapped.append(
                    {
                        "id_convocatoria": item.id_convocatoria,
                        "nombre_convocatoria": item.nombre_convocatoria,
                        "gestion": item.gestion
                    }
                )
        return items_mapped