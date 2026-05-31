from .constants import CI_ALIASES, RESULTADO_ALIASES, OBSERVACIONES_ALIASES

def normalize_column_name(col_name: str) -> str:
    if not col_name:
        return ""
    return col_name.strip().lower().replace(" ", "_")

def map_column(normalized_col: str) -> str:
    if normalized_col in CI_ALIASES:
        return "ci"
    if normalized_col in RESULTADO_ALIASES:
        return "nota"
    if normalized_col in OBSERVACIONES_ALIASES:
        return "observaciones"
    return normalized_col

def normalize_observation(obs: str) -> str:
    if not obs:
        return ""
    return obs.strip()