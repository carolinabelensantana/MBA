"""
Modulo de scraping: busca ofertas en LinkedIn, Indeed y Glassdoor
usando la biblioteca python-jobspy.
"""

import logging
import pandas as pd
from jobspy import scrape_jobs

from config import ROLE_KEYWORDS, EXCLUDE_KEYWORDS, TOP_TIER_COMPANIES, SEARCHES, JOB_SITES, RESULTS_PER_SEARCH, HOURS_OLD

logger = logging.getLogger(__name__)


def is_relevant_role(title: str) -> bool:
    """Verifica si el titulo del puesto coincide con algun keyword de rol
    y no contiene palabras que indiquen un nivel junior/entry."""
    if not title:
        return False
    title_lower = title.lower()
    has_keyword = any(kw.lower() in title_lower for kw in ROLE_KEYWORDS)
    is_junior = any(ex.lower() in title_lower for ex in EXCLUDE_KEYWORDS)
    return has_keyword and not is_junior


def is_top_tier_company(company: str) -> bool:
    """Verifica si la empresa esta en la lista de empresas prioritarias."""
    if not company:
        return False
    company_lower = company.lower()
    return any(tc.lower() in company_lower for tc in TOP_TIER_COMPANIES)


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

    # Eliminar duplicados por titulo + empresa
    combined = combined.drop_duplicates(subset=["title", "company"], keep="first")
    logger.info(f"Total tras deduplicar: {len(combined)} ofertas")

    # Filtrar solo roles relevantes (por si alguna busqueda trae resultados off-topic)
    combined = combined[combined["title"].apply(is_relevant_role)]
    logger.info(f"Total tras filtrar por rol: {len(combined)} ofertas")

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
