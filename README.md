# CAMPO LOGÍSTICA TARIJA DSS

**Sistema de Soporte a Decisiones para la Gestión, Priorización y Optimización de Entregas en Tarija, Bolivia**

Proyecto académico desarrollado para la materia **Sistemas de Soporte a Decisiones (DSS)**.

---

## 1. Visión del producto

> Una interfaz limpia, intuitiva y libre de distracciones que transforma datos logísticos complejos en indicadores, alertas, comparaciones y recomendaciones explicables para tomar decisiones rápidas y fundamentadas.

## 2. Objetivo UX

Diseñar una experiencia consistente y de baja carga cognitiva que permita:

* al usuario operativo registrar y actualizar datos con rapidez y sin errores;
* al responsable logístico identificar en pocos segundos los pedidos críticos;
* comparar alternativas de asignación y recorrido;
* comprender el impacto esperado en kilómetros, combustible y riesgo de retraso;
* explorar escenarios mediante análisis **What-If** sin necesidad de conocer detalles técnicos del motor DSS.

---

## 3. User Personas

### Perfil 1 — Operativo: Despachador Logístico

**Objetivo:** ingresar y mantener información confiable con la menor cantidad de pasos posible.

**Necesidades:**

* formularios simples;
* campos obligatorios visibles;
* validación inmediata;
* prevención de duplicados;
* confirmación en acciones destructivas;
* tablas con búsqueda y filtros.

### Perfil 2 — Estratégico: Responsable Logístico

**Objetivo:** comprender la situación operativa y decidir qué alternativa conviene en menos de cinco segundos.

**Necesita ver:**

* pedidos críticos;
* riesgo de retraso;
* kilómetros estimados;
* consumo estimado de combustible;
* ranking de prioridad;
* comparación de alternativas;
* recomendación DSS y explicación;
* KPIs de desempeño.

![User Personas](ux_strategy/user_personas.png)

---

## 4. Objetivos de interacción

| Pantalla                | Objetivo                                                       |
| ----------------------- | -------------------------------------------------------------- |
| Login                   | Acceder según rol de forma rápida y segura.                    |
| Pedidos                 | Registrar, consultar y actualizar pedidos sin errores.         |
| Conductores / Vehículos | Conocer disponibilidad y capacidad de los recursos.            |
| Dashboard DSS           | Detectar en segundos los casos que requieren atención.         |
| Comparar alternativas   | Evaluar distancia, combustible, riesgo y puntuación.           |
| What-If                 | Modificar condiciones y observar cómo cambia la recomendación. |
| Seguimiento             | Consultar estado, progreso y ubicación de la entrega.          |
| Reportes                | Revisar KPIs y resultados de las decisiones.                   |

---

## 5. Principios UX aplicados

* **Mínima sorpresa:** navegación y controles consistentes.
* **Revelación progresiva:** primero KPIs y alertas; los detalles aparecen al profundizar.
* **Prevención de errores:** validaciones visuales y confirmaciones.
* **Control del usuario:** el DSS recomienda; la persona decide.
* **Color funcional:** colores neutros para la interfaz y rojo/verde reservados para alertas o estados.
* **Accesibilidad:** texto legible y la información crítica no depende únicamente del color.
* **Drill-down:** desde un KPI o alerta se puede acceder al pedido o alternativa específica.

---

## 6. Arquitectura de navegación

![Arquitectura de Navegación](diagrams/navegacion_campo_logistica.png)

**Flujo principal:**

`Login → Menú principal → CRUD / Dashboard DSS → Comparar alternativas / What-If / Seguimiento / Reportes`

---

## 7. Prototipos UX/UI

### Login

![Login](prototypes/login.png)

### CRUD de Pedidos

![CRUD Pedidos](prototypes/crud_pedidos.png)

### Dashboard DSS

![Dashboard DSS](prototypes/dashboard_dss.png)

---

## 8. Diferencia entre CRUD y DSS

El CRUD mantiene los datos operativos de pedidos, clientes, conductores y vehículos.

El componente DSS utiliza esos datos para **analizar criterios, comparar alternativas, calcular prioridad y riesgo, estimar kilómetros y combustible y generar recomendaciones explicables** para el Responsable Logístico.

El sistema apoya la toma de decisiones, pero **la decisión final permanece bajo responsabilidad del usuario**.

---

## 9. KPIs principales

1. Porcentaje de errores de priorización y asignación.
2. Kilómetros totales y promedio por entrega.
3. Litros y costo estimado de combustible.
4. Porcentaje de entregas tardías.
5. Porcentaje de entregas a tiempo.
6. Cantidad de pedidos de prioridad alta.
7. Cantidad de entregas en riesgo.
8. Tasa de utilización de vehículos.

---

# 10. Arquitectura y Modelos

La arquitectura técnica de **CAMPO LOGÍSTICA TARIJA DSS** se documenta bajo el enfoque **Docs as Code**, utilizando PlantUML para mantener modelos textuales, versionables y trazables dentro del mismo repositorio.

Los modelos técnicos se concentran en las tres Historias de Usuario críticas que representan el núcleo del MVP DSS:

| Historia  | Funcionalidad                    | Propósito                                                                                            |
| --------- | -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **HU-04** | Calcular prioridad               | Determinar qué pedidos requieren atención primero.                                                   |
| **HU-08** | Comparar alternativas            | Evaluar diferentes posibilidades de asignación mediante distancia, combustible, riesgo y puntuación. |
| **HU-09** | Generar recomendación explicable | Recomendar la alternativa más conveniente y explicar los factores que justifican el resultado.       |

El flujo principal del núcleo DSS es:

`Datos → Priorización → Comparación de alternativas → Recomendación explicable → Decisión humana`

---

## 10.1 Diagrama de Casos de Uso

Representa la interacción del **Responsable Logístico** con las funcionalidades centrales del Motor DSS. El modelo muestra cómo el usuario puede calcular prioridades, comparar alternativas y obtener una recomendación antes de confirmar su decisión.

![Diagrama de Casos de Uso](docs/uml/casos_uso_motor_dss.png)

**Código fuente:** [`casos_uso_motor_dss.puml`](docs/uml/casos_uso_motor_dss.puml)

---

## 10.2 Diagrama de Clases

Representa las entidades operacionales y analíticas necesarias para soportar las historias críticas del MVP. Los pedidos, conductores y vehículos alimentan una evaluación DSS que compara alternativas utilizando criterios de decisión y produce una recomendación explicable.

![Diagrama de Clases](docs/uml/clases_motor_dss.png)

**Código fuente:** [`clases_motor_dss.puml`](docs/uml/clases_motor_dss.puml)

---

## 10.3 Diagrama de Secuencia

Representa el flujo cronológico de la generación de una recomendación DSS desde el Dashboard hasta la Base de Datos y el Motor de Decisión. Incluye validaciones, comparación iterativa de alternativas, manejo de errores y confirmación opcional de la decisión.

![Diagrama de Secuencia](docs/uml/secuencia_recomendacion_dss.png)

**Código fuente:** [`secuencia_recomendacion_dss.puml`](docs/uml/secuencia_recomendacion_dss.puml)

---

## 10.4 Trazabilidad HU → Modelo técnico

| Historia | Caso de Uso                      | Clase principal | Operación principal    |
| -------- | -------------------------------- | --------------- | ---------------------- |
| HU-04    | Calcular prioridad               | `EvaluacionDSS` | `calcularPrioridad()`  |
| HU-08    | Comparar alternativas            | `Alternativa`   | `calcularPuntuacion()` |
| HU-09    | Generar recomendación explicable | `Recomendacion` | `generarExplicacion()` |

Esta trazabilidad permite mantener coherencia entre los requisitos funcionales del Product Backlog, los modelos arquitectónicos y la futura implementación del sistema.

---

## 10.5 Docs as Code

Los modelos PlantUML se almacenan en:

`/docs/uml`

Cada modelo conserva tanto su **código fuente `.puml`** como su representación visual exportada, permitiendo que los diagramas puedan modificarse, versionarse y revisarse mediante Git.

Estructura:

```text
docs/
└── uml/
    ├── casos_uso_motor_dss.puml
    ├── casos_uso_motor_dss.png
    ├── clases_motor_dss.puml
    ├── clases_motor_dss.png
    ├── secuencia_recomendacion_dss.puml
    └── secuencia_recomendacion_dss.png
```

---

## 11. Estructura del repositorio

```text
CAMPOLOGISTICA-DSS/
│
├── README.md
│
├── ux_strategy/
│   └── user_personas.png
│
├── diagrams/
│   └── navegacion_campo_logistica.png
│
├── prototypes/
│   ├── login.png
│   ├── crud_pedidos.png
│   └── dashboard_dss.png
│
└── docs/
    └── uml/
        ├── casos_uso_motor_dss.puml
        ├── casos_uso_motor_dss.png
        ├── clases_motor_dss.puml
        ├── clases_motor_dss.png
        ├── secuencia_recomendacion_dss.puml
        └── secuencia_recomendacion_dss.png
```

---

## 12. Enlaces del proyecto

## Entorno de desarrollo (Incremento 0)

1. Copiar `.env.example` como `.env` y reemplazar sus valores solo para el entorno local.
2. Iniciar PostgreSQL 16 con `docker compose up -d`.
3. Instalar `backend/requirements.txt` y ejecutar `uvicorn app.main:app --reload` desde `backend`.
4. Ejecutar `npm ci` y `npm run dev` desde `frontend`.

El backend expone `GET http://localhost:8000/health` y el frontend usa `http://localhost:5173`. Los esquemas `oltp` y `dw` serán creados mediante migraciones posteriores; este incremento no crea tablas ni datos de dominio.

---

**Repositorio:** CAMPOLOGISTICA-DSS

**Documentación técnica:** `/docs`

**Modelos PlantUML:** `/docs/uml`

---

## Tecnologías y herramientas autorizadas

* **Frontend Target (Futuro):** React, Vite, TypeScript, Tailwind CSS, shadcn/ui, Lucide React, Apache ECharts, React-Leaflet.
* **Backend Target (Futuro):** Python, FastAPI, SQLAlchemy, Pydantic, Alembic, pytest.
* **Base de datos Target:** PostgreSQL 16 (Esquemas `oltp` y `dw`).
* **Documentación & Modelado:** PlantUML (Docs as Code), Git, GitHub.

---

## Arquitectura Dual: OLTP + Data Warehouse

CAMPO LOGÍSTICA TARIJA DSS utiliza una arquitectura dual que separa el procesamiento operacional del procesamiento analítico mediante dos esquemas relacionales independientes en PostgreSQL: `oltp` y `dw`.

El esquema **`oltp`** está orientado a las operaciones CRUD diarias y mantiene los datos normalizados para reducir redundancia y proteger la integridad relacional (PK autogeneradas con `BIGSERIAL`, FK con `BIGINT`, atributos de pedidos `urgencia` SMALLINT 1..5 y vehículos `rendimiento_km_l`).

El esquema **`dw`** utiliza un Esquema en Estrella (Star Schema) compuesto por `FACT_ENTREGA` y las dimensiones `DIM_TIEMPO`, `DIM_CLIENTE`, `DIM_CONDUCTOR`, `DIM_VEHICULO` y `DIM_UBICACION` con surrogate keys (`sk_*`), optimizado para consultas analíticas e indicadores históricos.

### Modelo OLTP — PostgreSQL (esquema `oltp`)

El modelo transaccional transforma las entidades definidas en UML en tablas relacionales mediante reglas ORM. Se utilizan claves primarias (`BIGSERIAL`), claves foráneas (`BIGINT`) y restricciones `UNIQUE`, `NOT NULL` y `CHECK` para mantener la integridad de los datos.

![Modelo OLTP](docs/database/modelo_oltp.png)

**Fuente PlantUML:** [`modelo_oltp.puml`](docs/database/modelo_oltp.puml)

### Data Warehouse — Esquema en Estrella (esquema `dw`)

El modelo analítico utiliza `FACT_ENTREGA` como tabla de hechos central y las dimensiones Tiempo, Cliente, Conductor, Vehículo y Ubicación.

La granularidad establecida es:

> **Cada fila de FACT_ENTREGA representa una entrega individual ejecutada correspondiente a un pedido y su asignación logística.**

Métricas de `FACT_ENTREGA`: `cantidad_entregas` (=1), `distancia_km`, `combustible_litros`, `costo_combustible`, `minutos_retraso`, `entrega_tardia`, `entrega_a_tiempo`.

![Data Warehouse](docs/database/modelo_dw_estrella.png)

**Fuente PlantUML:** [`modelo_dw_estrella.puml`](docs/database/modelo_dw_estrella.puml)

### Configuración del Motor DSS

El Motor DSS evalúa prioridades y recomendaciones utilizando una ponderación base congelada (Total 100%, escala 0-100):
* **Urgencia:** 30%
* **Riesgo de retraso:** 25%
* **Eficiencia de distancia:** 20%
* **Eficiencia de combustible:** 15%
* **Disponibilidad/capacidad de recursos:** 10%

**Restricciones duras:** Se evalúan antes del ranking. Si un conductor no está disponible, un vehículo no está disponible, la capacidad es insuficiente o el pedido no es asignable, la alternativa se **excluye** del ranking.

### Flujos de Información

La arquitectura comprende dos flujos diferenciados:

1. **Flujo Operacional DSS:**
   `PostgreSQL OLTP (esquema oltp) → Motor DSS → Prioridad / Riesgo / Recomendación → Dashboard DSS → Responsable Logístico → DECISIÓN HUMANA`

2. **Flujo Analítico:**
   `PostgreSQL OLTP (esquema oltp) → ETL → Data Warehouse (esquema dw) → KPIs / Histórico → Dashboard DSS → Responsable Logístico`

El OLTP registra la operación diaria y alimenta directamente al Motor DSS para soporte operacional, mientras que el Data Warehouse conserva información e indicadores analíticos históricos procesados por el ETL. En todos los casos, **la decisión final permanece bajo la responsabilidad del Responsable Logístico**.

