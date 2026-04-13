# ============================================================
# CONFIGURACION DEL JOB NOTIFIER
# Podes editar estas listas para ajustar los resultados
# ============================================================

# Palabras clave para filtrar roles relevantes
ROLE_KEYWORDS = [
    "HRBP",
    "HR Business Partner",
    "Human Resources Business Partner",
    "People Partner",
    "People Manager",
    "Head of People",
    "Head of HR",
    "HR Manager",
    "People & Culture Manager",
    "People and Culture Manager",
    "People Operations Manager",
    "Gerente de Personas",
    "Gerente RRHH",
    "Gerente de Recursos Humanos",
    "Director de Personas",
    "People Director",
    "VP People",
    "VP of People",
    "VP HR",
    "Chief People Officer",
    "CPO",
]

# Empresas de primer nivel (se muestran primero en el email)
TOP_TIER_COMPANIES = [
    # --- LatAm Tech Unicorns ---
    "Mercado Libre",
    "MercadoLibre",
    "Globant",
    "Despegar",
    "Naranja X",
    "Naranja",
    "Uala",
    "Ualá",
    "Tiendanube",
    "Nuvemshop",
    "Satellogic",
    "Lemon Cash",
    "Bitso",
    "OLX",
    "PedidosYa",
    "Pedidos Ya",
    "Rappi",
    "Kavak",
    "Pomelo",
    "Bind",
    "Bindeo",
    "Nubi",
    "Brubank",
    "Mango",
    "Increase",
    "Trocafone",
    "dLocal",
    "Inswitch",
    "Kushki",
    # --- Big Tech / Multinationals ---
    "Google",
    "Alphabet",
    "Meta",
    "Facebook",
    "Instagram",
    "Amazon",
    "AWS",
    "Microsoft",
    "Apple",
    "Netflix",
    "Spotify",
    "Salesforce",
    "HubSpot",
    "Stripe",
    "Uber",
    "Airbnb",
    "Twitter",
    "LinkedIn",
    "Twilio",
    "Zoom",
    "GitLab",
    "GitHub",
    "Atlassian",
    "Workday",
    "ServiceNow",
    "Okta",
    "Auth0",
    "Notion",
    "Slack",
    # --- Multinacionales tradicionales (consumo masivo, pharma, finanzas, retail, telecom) ---
    "Unilever",
    "Procter & Gamble",
    "P&G",
    "Nestlé",
    "Nestle",
    "Coca-Cola",
    "PepsiCo",
    "Mondelez",
    "AB InBev",
    "Heineken",
    "Diageo",
    "Johnson & Johnson",
    "Pfizer",
    "Novartis",
    "Roche",
    "AstraZeneca",
    "Bayer",
    "MSD",
    "Merck",
    "Abbott",
    "Medtronic",
    "Santander",
    "BBVA",
    "HSBC",
    "Citi",
    "JPMorgan",
    "Goldman Sachs",
    "Galicia",
    "Banco Macro",
    "Naranja",
    "Prudential",
    "Zurich",
    "Mapfre",
    "Disney",
    "Warner",
    "Universal",
    "Nike",
    "Adidas",
    "Toyota",
    "Ford",
    "Volkswagen",
    "General Motors",
    "Shell",
    "Total",
    "YPF",
    # --- LatAm Scale-ups / Funded Startups ---
    "Nubank",
    "Nu",
    "Creditas",
    "iFood",
    "Clip",
    "Konfio",
    "Kueski",
    "Neon",
    "Jeeves",
    "Tribal",
    "Conekta",
    "Pagos360",
    "SAP",
    "Oracle",
    "IBM",
    "Cognizant",
    "Infosys",
]

# Configuracion de busquedas (que buscar y donde)
# Podes agregar o quitar busquedas segun tus necesidades
SEARCHES = [
    # --- Argentina ---
    {"term": "HRBP", "location": "Argentina", "is_remote": False},
    {"term": "HR Business Partner", "location": "Argentina", "is_remote": False},
    {"term": "People Manager", "location": "Argentina", "is_remote": False},
    {"term": "Head of People", "location": "Argentina", "is_remote": False},
    {"term": "Gerente Recursos Humanos", "location": "Argentina", "is_remote": False},
    {"term": "Gerente de Personas", "location": "Argentina", "is_remote": False},
    # --- Remoto global ---
    {"term": "HRBP remote", "location": "", "is_remote": True},
    {"term": "HR Business Partner remote LatAm", "location": "", "is_remote": True},
    {"term": "People Partner remote", "location": "", "is_remote": True},
    {"term": "Head of People remote", "location": "", "is_remote": True},
]

# Sitios donde buscar (opciones: "linkedin", "indeed", "glassdoor", "google")
# LinkedIn puede ser lento o bloquearse a veces; indeed es el mas estable
JOB_SITES = ["linkedin", "indeed", "glassdoor"]

# Cuantos resultados buscar por combinacion de busqueda + sitio
RESULTS_PER_SEARCH = 15

# Solo mostrar trabajos publicados en las ultimas N horas
HOURS_OLD = 48  # 48h para no perderse nada si hay algun fallo puntual

# Horario del digest (configurable en el workflow de GitHub Actions)
# Por defecto: 8:00 AM hora Argentina (UTC-3) = 11:00 UTC
SEND_HOUR_UTC = 11
