# Pokédex Builder

Generador reproducible de una Pokédex Nacional con variantes almacenables en Pokémon HOME. Produce archivos Excel, CSV y JSON, además de un reporte separado de cobertura de los catálogos de disponibilidad por juego y shiny.

## Estado del proyecto

El generador ya incluye:

- Especies y variedades obtenidas desde PokéAPI.
- Caché JSON local para evitar descargas repetidas.
- Exclusión configurable de formas no admitidas.
- Correcciones de nombres y generación mediante YAML.
- Diferencias de género visibles en Pokémon HOME.
- Orden de género `Female` antes de `Male`.
- Indicadores de disponibilidad para los juegos configurados.
- Indicador de shiny obtenible sin evento.
- Exportación a CSV, JSON y XLSX.
- Reporte de cobertura para distinguir datos verificados de valores pendientes.

> Los catálogos `game_availability.yaml` y `shiny_availability.yaml` utilizan un criterio conservador. Mientras estén marcados como incompletos, una fila no catalogada permanece en `FALSE`, pero debe considerarse pendiente de verificación, no necesariamente una indisponibilidad confirmada.

## Requisitos

- Windows, macOS o Linux.
- Git.
- `uv`.
- Python 3.12.

Verifica las herramientas:

```powershell
uv --version
uv run python --version
```

## Instalación

Clona el repositorio y entra en la carpeta:

```powershell
git clone https://github.com/TU_USUARIO/pokedex-builder.git
cd pokedex-builder
```

Instala Python 3.12 si todavía no está disponible:

```powershell
uv python install 3.12
uv python pin 3.12
```

Sincroniza el entorno exactamente desde `pyproject.toml` y `uv.lock`:

```powershell
uv sync --locked
```

## Configuración

La aplicación funciona con valores predeterminados. Opcionalmente, copia `.env.example` como `.env` y ajusta sus valores:

```powershell
Copy-Item .env.example .env
```

Todas las variables usan el prefijo `POKEDEX_`.

## Generar todos los archivos

```powershell
uv run python build_pokedex.py
```

Se generan:

```text
output/
├── Pokedex.csv
├── Pokedex.json
├── Pokedex.xlsx
└── Catalog_Coverage.json
```

## Generar formatos específicos

Usa `--only` una o varias veces:

```powershell
uv run python build_pokedex.py --only excel
uv run python build_pokedex.py --only csv --only json
uv run python build_pokedex.py --only coverage
```

Valores admitidos:

- `csv`
- `json`
- `excel`
- `coverage`

## Actualizar la caché

Para ignorar la caché existente y consultar nuevamente las fuentes:

```powershell
uv run python build_pokedex.py --refresh-cache
```

La caché se almacena en `cache/` y no debe subirse a Git.

## Validar sin exportar

```powershell
uv run python build_pokedex.py --validate
```

Este comando ejecuta el flujo de descarga, transformación y validación, pero no escribe los archivos finales.

## Ayuda y versión

```powershell
uv run python build_pokedex.py --help
uv run python build_pokedex.py --version
```

## Pruebas y controles de calidad

Ejecuta Black:

```powershell
uv run black .
```

Comprueba el tipado estático:

```powershell
uv run mypy pokedex tests build_pokedex.py
```

Ejecuta toda la suite:

```powershell
uv run pytest -v
```

Ejecuta la cobertura:

```powershell
uv run pytest --cov=pokedex --cov-report=term-missing
```

Ejecuta los hooks:

```powershell
uv run pre-commit run --all-files
uv run pre-commit run --all-files --hook-stage pre-push
```

Flujo recomendado antes de cada commit:

```powershell
uv run black .
uv run mypy pokedex tests build_pokedex.py
uv run pytest -v
uv run pre-commit run --all-files
uv run pre-commit run --all-files --hook-stage pre-push
```

## Archivos de reglas

Los catálogos editables se encuentran en `data/`:

```text
data/
├── form_rules.yaml
├── form_overrides.yaml
├── gender_differences.yaml
├── game_availability.yaml
└── shiny_availability.yaml
```

### `form_rules.yaml`

Controla exclusiones como Mega Evoluciones, Gigantamax, formas temporales y especies configuradas con una sola fila.

### `form_overrides.yaml`

Corrige nombres visibles y la generación de introducción de variantes concretas.

### `gender_differences.yaml`

Define diferencias visuales de género y normaliza variedades que PokéAPI entrega por separado.

### `game_availability.yaml`

Asigna disponibilidad por juego mediante reglas por especie, inclusiones por `ID HOME` y exclusiones específicas.

### `shiny_availability.yaml`

Define qué especies o variantes pueden obtenerse shiny sin depender de un evento de distribución.

## Columnas exportadas

La tabla principal contiene:

1. `Nat Dex`
2. `Pokemon`
3. `Forma`
4. `Gen`
5. `ID HOME`
6. `Nombre`
7. `Obtenido`
8. `Prioridad`
9. `XY`
10. `ORAS`
11. `SM`
12. `USUM`
13. `LGPE`
14. `SwSh`
15. `Arceus`
16. `BDSP`
17. `ScVi`
18. `ZA`
19. `Legendario/Mítico`
20. `Obtenible`
21. `Posibles`

La dimensión interna de género no se exporta como una columna separada. Se refleja en `Forma`, `Nombre` e `ID HOME`. En Excel, `Posibles` se calcula con una fórmula y permanece oculta; en CSV y JSON se exporta vacía para conservar el mismo esquema de columnas.

## Excel

`Pokedex.xlsx` contiene:

- `Pokédex`: tabla completa con filtros y encabezados fijos.
- `Resumen`: métricas generales, disponibilidad por juego y seguimiento dinámico de `Obtenido`/`Posibles`.
- `Validación`: resultados de verificaciones automáticas.
- `Metadatos`: versión, fecha UTC y número de registros.

## Reporte de cobertura

`Catalog_Coverage.json` diferencia:

- `verified_true`: filas marcadas explícitamente como verdaderas.
- `verified_false`: filas cubiertas por una exclusión explícita.
- `unknown`: filas todavía pendientes de clasificación.
- `percent`: porcentaje de cobertura del catálogo.

No uses únicamente el valor booleano final para medir la calidad del catálogo mientras `complete` sea `false`.

## Flujo de Git recomendado

```powershell
git checkout develop
git checkout -b feature/nombre-del-cambio
```

Después de validar:

```powershell
git add .
git commit -m "Describe the change"
git push -u origin feature/nombre-del-cambio
```

No subas `.venv/`, `cache/`, `logs/` ni los archivos generados en `output/`.
