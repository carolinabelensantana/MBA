"""
Modulo de construccion del email HTML con el digest diario de empleos.
"""

import pandas as pd
from datetime import datetime


# Meses en español para formatear la fecha
MONTHS_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def _format_date_es(dt) -> str:
    """Formatea una fecha en español: '13 de abril de 2026'."""
    now = datetime.now()
    return f"{now.day} de {MONTHS_ES[now.month]} de {now.year}"


def _salary_badge(row) -> str:
    """Genera el badge de salario si hay datos disponibles."""
    try:
        min_amt = row.get("min_amount")
        max_amt = row.get("max_amount")
        currency = row.get("currency", "")
        interval = row.get("interval", "")

        if pd.notna(min_amt) and pd.notna(max_amt) and min_amt > 0:
            return (
                f'<span style="display:inline-block;background:#d4edda;color:#155724;'
                f'padding:3px 8px;border-radius:12px;font-size:11px;margin-bottom:8px;">'
                f'Salario: {currency} {int(min_amt):,} - {int(max_amt):,} / {interval}'
                f'</span><br>'
            )
    except Exception:
        pass
    return ""


def _site_badge(site: str) -> str:
    """Badge con el nombre del sitio donde se encontro la oferta."""
    colors = {
        "linkedin": "#0077b5",
        "indeed": "#003a9b",
        "glassdoor": "#0caa41",
        "google": "#db4437",
    }
    color = colors.get((site or "").lower(), "#666")
    label = (site or "").capitalize()
    return (
        f'<span style="display:inline-block;background:{color};color:#fff;'
        f'padding:2px 7px;border-radius:10px;font-size:10px;margin-right:6px;">'
        f'{label}</span>'
    )


def _location_text(row) -> str:
    """Texto de ubicacion con icono segun si es remoto o presencial."""
    is_remote = row.get("is_remote", False)
    location = row.get("location", "") or ""

    if is_remote or "remote" in location.lower() or "remoto" in location.lower():
        return "Remoto"
    return location if location else "Ubicacion no especificada"


def _job_card(row, is_priority: bool = False) -> str:
    """Genera el HTML de una tarjeta de oferta."""
    border_color = "#6c5ce7" if is_priority else "#e0e0e0"
    title = row.get("title", "Sin titulo")
    company = row.get("company", "Empresa no especificada")
    job_url = row.get("job_url", "#")
    site = row.get("site", "")
    location_text = _location_text(row)
    salary = _salary_badge(row)
    site_badge = _site_badge(site)

    # Fecha relativa
    date_str = ""
    try:
        date_posted = row.get("date_posted")
        if date_posted and pd.notna(date_posted):
            days_ago = (datetime.now().date() - pd.to_datetime(date_posted).date()).days
            date_str = "Hoy" if days_ago == 0 else f"Hace {days_ago} dia{'s' if days_ago > 1 else ''}"
    except Exception:
        pass

    return f"""
    <div style="background:#fff;border:1px solid {border_color};border-left:4px solid {border_color};
                border-radius:8px;padding:16px 18px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;">
            <div style="flex:1;min-width:200px;">
                <h3 style="margin:0 0 4px 0;font-size:15px;color:#1a1a2e;font-weight:600;">{title}</h3>
                <p style="margin:0 0 6px 0;font-size:13px;font-weight:600;color:#4a4a6a;">{company}</p>
                <p style="margin:0 0 8px 0;font-size:12px;color:#888;">
                    {"Remoto" if "remoto" in location_text.lower() or "remote" in location_text.lower()
                      else ""}{"" if not location_text or location_text == "Ubicacion no especificada"
                      else ("" if "remoto" in location_text.lower() or "remote" in location_text.lower()
                            else location_text)}
                    {(" &middot; " + date_str) if date_str else ""}
                </p>
                {salary}
                {site_badge}
            </div>
        </div>
        <a href="{job_url}"
           style="display:inline-block;background:#6c5ce7;color:#fff;padding:8px 18px;
                  border-radius:6px;text-decoration:none;font-size:13px;font-weight:500;
                  margin-top:8px;">
            Ver oferta &rarr;
        </a>
    </div>
    """


def _section(title: str, icon: str, jobs: pd.DataFrame, is_priority: bool) -> str:
    """Genera una seccion completa del email (header + tarjetas)."""
    if jobs.empty:
        cards_html = '<p style="color:#aaa;font-size:13px;padding:8px 0;">Sin resultados en esta categoria hoy.</p>'
    else:
        cards_html = "".join(
            _job_card(row, is_priority=is_priority)
            for _, row in jobs.iterrows()
        )

    return f"""
    <div style="background:#fff;padding:24px 28px;margin-top:4px;">
        <h2 style="color:#1a1a2e;font-size:16px;margin:0 0 18px 0;
                   padding-bottom:10px;border-bottom:2px solid #f0f0f0;">
            {icon} {title} <span style="color:#aaa;font-weight:400;font-size:13px;">({len(jobs)})</span>
        </h2>
        {cards_html}
    </div>
    """


def build_html_email(jobs_df: pd.DataFrame) -> str:
    """
    Construye el email HTML completo con el digest diario.
    Recibe un DataFrame de pandas con las ofertas encontradas.
    """
    today = _format_date_es(datetime.now())
    total = len(jobs_df)

    top_jobs = jobs_df[jobs_df["is_top_tier"] == True].reset_index(drop=True)
    other_jobs = jobs_df[jobs_df["is_top_tier"] == False].reset_index(drop=True)
    top_count = len(top_jobs)

    priority_section = _section(
        "Empresas Prioritarias",
        "&#11088;",
        top_jobs,
        is_priority=True,
    )
    other_section = _section(
        "Otras Oportunidades",
        "&#128203;",
        other_jobs,
        is_priority=False,
    )

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People Jobs Daily</title>
</head>
<body style="font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;margin:0;padding:24px 12px;">
    <div style="max-width:620px;margin:0 auto;">

        <!-- Header -->
        <div style="background:linear-gradient(135deg,#1a1a2e 0%,#6c5ce7 100%);
                    padding:32px 28px;border-radius:12px 12px 0 0;text-align:center;">
            <h1 style="color:#fff;margin:0 0 6px 0;font-size:22px;letter-spacing:-0.5px;">
                Roles People &amp; HRBP
            </h1>
            <p style="color:#d0c9ff;margin:0 0 14px 0;font-size:13px;">{today}</p>
            <div style="display:inline-flex;gap:16px;flex-wrap:wrap;justify-content:center;">
                <span style="background:rgba(255,255,255,0.15);color:#fff;padding:6px 14px;
                             border-radius:20px;font-size:13px;">
                    {total} ofertas nuevas
                </span>
                <span style="background:rgba(255,255,255,0.15);color:#fff;padding:6px 14px;
                             border-radius:20px;font-size:13px;">
                    &#11088; {top_count} en empresas top
                </span>
            </div>
        </div>

        {priority_section}
        {other_section}

        <!-- Footer -->
        <div style="background:#fff;padding:20px 28px;border-radius:0 0 12px 12px;
                    border-top:1px solid #f0f0f0;text-align:center;">
            <p style="color:#bbb;font-size:11px;margin:0 0 4px 0;">
                Busqueda automatica diaria &middot; HRBP / People Manager / Head of People
            </p>
            <p style="color:#bbb;font-size:11px;margin:0;">
                Argentina &amp; Remoto &middot; LinkedIn, Indeed, Glassdoor
            </p>
        </div>

    </div>
</body>
</html>"""


def build_no_results_email() -> str:
    """Email de confirmacion cuando no hay resultados nuevos."""
    today = _format_date_es(datetime.now())
    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>People Jobs Daily</title></head>
<body style="font-family:'Helvetica Neue',Arial,sans-serif;background:#f0f2f8;
             margin:0;padding:24px 12px;">
    <div style="max-width:620px;margin:0 auto;background:#fff;border-radius:12px;
                padding:40px 28px;text-align:center;">
        <h1 style="color:#1a1a2e;font-size:20px;">People Jobs Daily</h1>
        <p style="color:#888;font-size:14px;">{today}</p>
        <p style="color:#555;font-size:15px;margin-top:24px;">
            No se encontraron nuevas ofertas en las ultimas 48 horas.<br>
            <span style="color:#aaa;font-size:13px;">El sistema esta funcionando correctamente.</span>
        </p>
    </div>
</body>
</html>"""
