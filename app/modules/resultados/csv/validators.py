from .exceptions import CSVValidationError

def validate_nota(nota_raw: str) -> int:
    try:
        nota = int(float(nota_raw.strip()))
    except ValueError:
        raise CSVValidationError(f"La nota '{nota_raw}' no es un número válido.")
    
    if nota < 0 or nota > 100:
        raise CSVValidationError("El resultado debe estar en un rango de 0 a 100.")
    return nota

def validate_ci_present(ci_raw: str) -> str:
    ci = ci_raw.strip()
    if not ci:
        raise CSVValidationError("El Carnet de Identidad no puede estar vacío.")
    return ci

def validate_inscripcion(ci: str, dict_inscripciones: dict):
    inscripcion = dict_inscripciones.get(ci)
    if not inscripcion:
        raise CSVValidationError(f"No existe inscripción para la categoría de esta fase con el CI '{ci}'.")
    return inscripcion.id_inscripcion