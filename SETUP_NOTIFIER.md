# Guia de Setup - People Jobs Notifier

Este sistema busca automaticamente roles HRBP, People Manager y Head of People
en LinkedIn, Indeed y Glassdoor, y te manda un email diario con las mejores oportunidades.

---

## Lo que necesitas antes de empezar

- Una cuenta de **Gmail** (la que usas normalmente esta bien)
- Tu cuenta de **GitHub** (ya la tenes)
- 10 minutos para hacer el setup una sola vez

---

## Paso 1: Crear una Contrasena de Aplicacion en Gmail

> Gmail no te deja usar tu contrasena normal para enviar emails automaticos.
> Necesitas crear una "contrasena de aplicacion" especial.

1. Abre **myaccount.google.com**
2. En el menu de la izquierda, hace click en **Seguridad**
3. Baja hasta encontrar **Verificacion en dos pasos** y asegurate de tenerla activada
   *(si no la tenes, primero activala)*
4. Una vez activada, vuelve a Seguridad y busca **Contrasenas de aplicaciones**
5. Hace click ahi y te va a pedir que confirmes tu identidad
6. En el campo que dice "Nombre de la app" escribi: `Job Notifier`
7. Hace click en **Crear**
8. Te va a aparecer una contrasena de 16 caracteres como esta: `abcd efgh ijkl mnop`
9. **Copiala y guardalas en un lugar seguro** (la vas a necesitar en el Paso 2)

---

## Paso 2: Agregar los Secrets en GitHub

Los "secrets" son como contrasenas guardadas de forma segura en GitHub.
El script las usa para enviar el email, sin que esten visibles en el codigo.

1. Ve a tu repositorio en GitHub: **github.com/carolinabelensantana/mba**
2. Hace click en **Settings** (la rueda dentada en el menu de arriba)
3. En el menu de la izquierda, busca **Secrets and variables** → **Actions**
4. Hace click en **New repository secret** y agrega estos 3 secrets:

---

### Secret 1: `GMAIL_USER`
- **Name:** `GMAIL_USER`
- **Value:** tu direccion de Gmail completa, ejemplo: `carolinasantana@gmail.com`

---

### Secret 2: `GMAIL_APP_PASSWORD`
- **Name:** `GMAIL_APP_PASSWORD`
- **Value:** la contrasena de aplicacion que copiaste en el Paso 1
  *(sin espacios, todo junto: `abcdefghijklmnop`)*

---

### Secret 3: `NOTIFY_EMAIL`
- **Name:** `NOTIFY_EMAIL`
- **Value:** el email donde queres recibir las notificaciones
  *(puede ser el mismo Gmail u otro correo)*

---

## Paso 3: Verificar que funciona

1. Ve a tu repositorio → **Actions** (en el menu de arriba)
2. En la lista de la izquierda, hace click en **Daily People Jobs Notification**
3. Hace click en **Run workflow** → **Run workflow** (boton verde)
4. Espera unos minutos (puede tardar hasta 5 min)
5. Si aparece un tilde verde: **todo funciona**
6. Revisa tu email: deberia haberte llegado el primer digest

---

## Como funciona de ahi en adelante

- **De lunes a viernes a las 8:00 AM** (hora Argentina) te llega el email automaticamente
- Busca en LinkedIn, Indeed y Glassdoor simultaneamente
- Prioriza empresas como Mercado Libre, Globant, Google, Meta, startups con funding, etc.
- Te muestra primero las ofertas de empresas prioritarias, despues el resto

---

## Personalizar la busqueda

Si queres ajustar las palabras clave, empresas o busquedas, todo esta en:

```
job_notifier/config.py
```

Ese archivo tiene comentarios que explican cada seccion. Podes editarlo directamente
desde GitHub (haciendo click en el lapiz) sin necesidad de instalar nada.

---

## Preguntas frecuentes

**Q: No me llego el email, que hago?**
A: Ve a GitHub → Actions y revisa si el workflow dio error (icono rojo).
   El error mas comun es que la contrasena de aplicacion este mal copiada.

**Q: Me llegan muchos empleos irrelevantes**
A: Edita `job_notifier/config.py` y agrega o quita palabras de `ROLE_KEYWORDS`.

**Q: Quiero recibirlo tambien los fines de semana**
A: En `.github/workflows/job_notifier.yml`, cambia `1-5` por `*` en la linea del cron.

**Q: Quiero agregar mas empresas prioritarias**
A: Edita la lista `TOP_TIER_COMPANIES` en `job_notifier/config.py`.

---

## Soporte

Si algo no funciona, revisa la seccion **Actions** en tu repositorio de GitHub
para ver los logs de error. Suelen ser muy descriptivos.
