"""
Modulo de scraping: busca ofertas en LinkedIn, Indeed y Glassdoor
usando la biblioteca python-jobspy.
"""

import logging
import re
import pandas as pd
from jobspy import scrape_jobs

from config import ROLE_KEYWORDS, EXCLUDE_KEYWORDS, BLOCKED_COMPANIES, TOP_TIER_COMPANIES, SEARCHES, JOB_SITES, RESULTS_PER_SEARCH, HOURS_OLD, ARGENTINA_LOCATIONS

logger = logging.getLogger(__name__)

# Regex que detecta cualquier variante Unicode de guion/raya
_UNICODE_DASHES = re.compile(
    r'[\u00ad\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe63\uff0d]'
)


def _normalize(text: str) -> str:
    """Convierte a minusculas y reemplaza todos los guiones Unicode por ASCII '-'."""
    return _UNICODE_DASHES.sub("-", text).lower().strip()


def is_relevant_role(title: str) -> bool:
    """Verifica si el titulo del puesto coincide con algun keyword de rol
    y no contiene palabras que indiquen un nivel junior/entry."""
    if not title:
        return False
    normalized = _normalize(title)
    has_keyword = any(_normalize(kw) in normalized for kw in ROLE_KEYWORDS)
    is_junior = any(_normalize(ex) in normalized for ex in EXCLUDE_KEYWORDS)
    return has_keyword and not is_junior


def is_blocked_company(company: str) -> bool:
    """Verifica si la empresa esta en la lista de fuentes bloqueadas."""
    if not company:
        return False
    normalized = _normalize(company)
    return any(_normalize(bc) in normalized for bc in BLOCKED_COMPANIES)


def is_valid_location(row) -> bool:
    """Solo acepta trabajos donde la ubicacion menciona Argentina explicitamente."""
    location = _normalize(str(row.get("location", "") or ""))
    company = _normalize(str(row.get("company", "") or ""))

    # Si la ubicacion menciona Argentina: aceptar
    if any(term in location for term in ARGENTINA_LOCATIONS):
        return True

    # Si la ubicacion esta vacia pero la empresa tiene "usa" en el nombre: rechazar
    if any(x in company for x in [" usa", " u.s.", "united states"]):
        logger.info(f"  [EXCLUIDO POR UBICACION] {row.get('title', '')} - empresa: {row.get('company', '')}")
        return False

    # Ubicacion vacia: dejar pasar (puede ser un rol de Argentina sin dato)
    if not location or location in ("nan", "none"):
        return True

    # Ubicacion presente pero no Argentina: rechazar
    logger.info(f"  [EXCLUIDO POR UBICACION] {row.get('title', '')} - {row.get('location', '')}")
    return False


def is_top_tier_company(company: str) -> bool:
    """Verifica si la empresa esta en la lista de empresas prioritarias."""
    if not company:
        return False
    normalized = _normalize(company)
    return any(_normalize(tc) in normalized for tc in TOP_TIER_COMPANIES)


def scrape_all_jobs() -> pd.DataFrame:
    """
    Ejecuta todas las busquedas configuradas y devuelve un DataFrame
    con los resultados deduplicados, filtrados y ordenados.
    """
    all_results = []

    for search in SEARCHES:
        term = search["term"]
        location = search.get("location", "")
        is_remote = search.get("is_remote", False)

        label = f"'{term}'" + (f" en {location}" if location else " (remoto)")
        logger.info(f"Buscando: {label}")

        try:
            jobs = scrape_jobs(
                site_name=JOB_SITES,
                search_term=term,
                location=location if location else None,
                results_wanted=RESULTS_PER_SEARCH,
                hours_old=HOURS_OLD,
                country_indeed="Argentina",
                is_remote=is_remote,
                linkedin_fetch_description=False,  # mas rapido sin descripcion completa
            )

            if jobs is not None and not jobs.empty:
                logger.info(f"  -> {len(jobs)} resultados encontrados")
                all_results.append(jobs)
            else:
                logger.info(f"  -> Sin resultados")

        except Exception as e:
            logger.warning(f"  -> Error en busqueda '{term}': {e}")
            continue

    if not all_results:
        logger.warning("No se encontraron resultados en ninguna busqueda.")
        return pd.DataFrame()

    # Combinar todos los resultados
    combined = pd.concat(all_results, ignore_index=True)
    logger.info(f"Total antes de filtros: {len(combined)} ofertas")

    # Normalizar columnas clave para evitar problemas con NaN
    combined["title"] = combined["title"].fillna("").astype(str).str.strip()
    combined["company"] = combined["company"].fillna("").astype(str).str.strip()

    # Eliminar duplicados por titulo + empresa
    combined = combined.drop_duplicates(subset=["title", "company"], keep="first")
    logger.info(f"Total tras deduplicar: {len(combined)} ofertas")

    # Filtrar solo roles relevantes (por si alguna busqueda trae resultados off-topic)
    mask_relevant = combined["title"].apply(is_relevant_role)
    logger.info(f"Excluidos por titulo irrelevante o junior: {(~mask_relevant).sum()}")
    for title in combined[~mask_relevant]["title"].tolist():
        logger.info(f"  [EXCLUIDO POR TITULO] {title}")
    combined = combined[mask_relevant]

    # Excluir empresas/plataformas bloqueadas
    mask_not_blocked = ~combined["company"].apply(is_blocked_company)
    logger.info(f"Excluidos por empresa bloqueada: {(~mask_not_blocked).sum()}")
    for company in combined[~mask_not_blocked]["company"].tolist():
        logger.info(f"  [EXCLUIDO POR EMPRESA] {company}")
    combined = combined[mask_not_blocked]

    # Filtrar por ubicacion geografica (solo Argentina o remoto global)
    mask_location = combined.apply(is_valid_location, axis=1)
    logger.info(f"Excluidos por ubicacion invalida: {(~mask_location).sum()}")
    combined = combined[mask_location]

    logger.info(f"Total tras filtros: {len(combined)} ofertas")

    if combined.empty:
        return combined

    # Marcar empresas prioritarias
    combined["is_top_tier"] = combined["company"].apply(is_top_tier_company)

    # Ordenar: prioritarias primero, luego por fecha descendente
    combined = combined.sort_values(
        by=["is_top_tier", "date_posted"],
        ascending=[False, False]
    ).reset_index(drop=True)

    logger.info(
        f"Resultado final: {len(combined)} ofertas "
        f"({combined['is_top_tier'].sum()} en empresas prioritarias)"
    )

    return combined
