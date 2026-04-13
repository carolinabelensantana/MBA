"""
Entry point del Job Notifier.
Orquesta el scraping, construye el email y lo envia por Gmail.

Variables de entorno requeridas (configuradas como GitHub Secrets):
    GMAIL_USER          - Direccion Gmail desde donde se envia
    GMAIL_APP_PASSWORD  - Contrasena de aplicacion de Gmail (no la contrasena normal)
    NOTIFY_EMAIL        - Correo donde recibir las notificaciones (puede ser el mismo)
"""

import os
import sys
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Permitir imports desde el mismo directorio
sys.path.insert(0, os.path.dirname(__file__))

from scraper import scrape_all_jobs
from email_builder import build_html_email, build_no_results_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _get_env(name: str) -> str:
    """Obtiene una variable de entorno o falla con mensaje claro."""
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(
            f"Variable de entorno '{name}' no configurada. "
            f"Configurala como GitHub Secret en tu repositorio."
        )
    return value


def send_email(subject: str, html_body: str) -> None:
    """Envia el email HTML via Gmail SMTP."""
    gmail_user = _get_env("GMAIL_USER")
    gmail_password = _get_env("GMAIL_APP_PASSWORD")
    notify_email = os.environ.get("NOTIFY_EMAIL") or gmail_user

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"People Jobs Notifier <{gmail_user}>"
    msg["To"] = notify_email

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    logger.info(f"Enviando email a {notify_email}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, notify_email, msg.as_string())

    logger.info("Email enviado correctamente.")


def main() -> None:
    today = datetime.now().strftime("%d/%m/%Y")
    logger.info(f"=== People Jobs Notifier - {today} ===")

    # 1. Scrapear empleos
    jobs_df = scrape_all_jobs()

    # 2. Construir y enviar email
    if jobs_df.empty:
        logger.info("No se encontraron ofertas. Enviando email de sin resultados.")
        send_email(
            subject=f"People Jobs {today} - Sin nuevas ofertas",
            html_body=build_no_results_email(),
        )
    else:
        total = len(jobs_df)
        top_count = int(jobs_df["is_top_tier"].sum())
        logger.info(f"Enviando digest con {total} ofertas ({top_count} prioritarias).")

        send_email(
            subject=f"People Jobs {today} - {total} ofertas ({top_count} en empresas top)",
            html_body=build_html_email(jobs_df),
        )

    logger.info("=== Finalizado ===")


if __name__ == "__main__":
    main()
