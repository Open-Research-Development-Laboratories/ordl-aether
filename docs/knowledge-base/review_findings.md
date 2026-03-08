Back to index: [../INDEX.md](../INDEX.md) | [Knowledge Base Catalog](doc_catalog.md)

# Review Findings

- Generated: `2026-03-08T03:44:58.878038+00:00`

Ordered by severity.

## [P1] HTTPException statuses are overwritten as 500

- File: `aether-system/backend/api/routes.py:77`
- Detail: Route handlers raise HTTPException with 400/503, but broad exception handlers catch them and re-raise 500, masking intended client/server error semantics.

## [P1] NASA APOD endpoint URL is built from API key string

- File: `aether-system/backend/modules/data_ingestion.py:158`
- Detail: APOD fetch URL uses NASA_API_KEY as host prefix; expected base endpoint is https://api.nasa.gov/planetary/apod with API key in query params.

## [P1] Frontend health polling points to non-existent prefixed route

- File: `aether-system/frontend/src/App.jsx:28`
- Detail: Base URL is /api/v1, but health endpoint exists at /health (outside router prefix). Current request resolves to /api/v1/health and will fail.

## [P1] Loader icon is used but not imported

- File: `aether-system/frontend/src/pages/SystemStatus.jsx:35`
- Detail: Component renders <Loader /> during loading state, but Loader is absent from lucide-react imports, causing runtime ReferenceError.

## [P2] Registered source name does not match ingestion switch key

- File: `aether-system/backend/modules/data_ingestion.py:143`
- Detail: Default source is registered as OpenMeteo but process() checks for source_name == "weather", causing Unknown source if callers use advertised source names.

## [P2] Default CORS settings conflict with credentialed requests

- File: `aether-system/backend/main.py:107`
- Detail: Defaults use allow_origins=['*'] with allow_credentials=True. FastAPI/Starlette CORS docs state wildcard cannot be combined with credentialed requests.
