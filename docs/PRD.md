# Product Requirements Document (PRD)

## CAMPO LOGÍSTICA TARIJA DSS

**Proyecto:** Sistema de Soporte a Decisiones para la Gestión, Priorización y Optimización de Entregas en Tarija, Bolivia.

**Versión:** 1.0
**Estado:** MVP académico
**Gestión:** 2026
**Base de datos:** PostgreSQL
**Arquitectura:** OLTP + ETL + Data Warehouse/OLAP + Motor DSS

---

# 1. Objetivo y Fronteras (Boundary Rules)

## 1.1 Propósito

CAMPO LOGÍSTICA TARIJA DSS es un Sistema de Soporte a Decisiones orientado a la gestión de entregas urbanas en Tarija. El sistema integra un núcleo transaccional OLTP para registrar pedidos, clientes, conductores, vehículos y asignaciones; un proceso ETL para preparar información histórica; un Data Warehouse para análisis de indicadores; y un Motor DSS que permite evaluar prioridad, riesgo, distancia, combustible y alternativas de asignación. El sistema genera información y recomendaciones explicables para el Responsable Logístico, quien conserva la decisión final.

## 1.2 Lo que DEBE hacer

* Registrar y mantener información operacional de pedidos, clientes, ubicaciones, conductores, vehículos y asignaciones mediante operaciones CRUD sobre PostgreSQL OLTP.
* Transformar información operacional mediante procesos ETL y cargar datos analíticos válidos en un Data Warehouse con Esquema en Estrella.
* Proporcionar soporte a decisiones mediante indicadores, priorización, evaluación de riesgo, comparación de alternativas y recomendaciones explicables.

## 1.3 Lo que NO debe hacer/tocar

Estas reglas constituyen fronteras obligatorias para desarrolladores humanos y agentes de IA:

* **NO** eliminar, renombrar o modificar tablas, columnas, PK, FK o restricciones existentes sin una modificación explícita y aprobada del modelo de datos.
* **NO** mezclar las responsabilidades del esquema transaccional `oltp` con las del esquema analítico `dw`.
* **NO** escribir directamente en `dw.fact_entrega` desde operaciones CRUD; los datos analíticos deben ingresar mediante el proceso ETL definido.
* **NO** cargar en `FACT_ENTREGA` asignaciones canceladas, entregas no finalizadas o registros que no superen las reglas de calidad ETL.
* **NO** almacenar texto descriptivo operacional innecesario dentro de `FACT_ENTREGA`; la tabla debe concentrar claves y métricas cuantitativas.
* **NO** modificar silenciosamente los pesos, criterios o restricciones del Motor DSS.
* **NO** recomendar alternativas que incumplan disponibilidad del conductor, disponibilidad del vehículo, capacidad requerida o condiciones válidas del pedido.
* **NO** presentar datos estimados como resultados reales.
* **NO** afirmar que los objetivos de reducción de kilómetros, combustible, errores o retrasos fueron alcanzados mientras no exista evidencia de medición.
* **NO** permitir que una recomendación del DSS ejecute automáticamente la decisión final sin confirmación del Responsable Logístico.
* **NO** eliminar trazabilidad entre los datos OLTP, las transformaciones ETL y la información analítica.
* **NO** introducir servicios de pago, APIs comerciales, GPS real, Machine Learning o funcionalidades de Release 2 dentro del alcance del MVP sin aprobación explícita.

---

# 2. Perfiles de Usuario

## 2.1 Administrador

Opera principalmente el núcleo transaccional. Gestiona información de pedidos, clientes, conductores, vehículos y datos necesarios para la operación del sistema.

## 2.2 Responsable Logístico

Es el principal usuario del DSS. Consulta prioridades, riesgos, alternativas, recomendaciones, indicadores y dashboards para apoyar la planificación y asignación de entregas. La decisión final permanece bajo su responsabilidad.

## 2.3 Analista Logístico

Consulta indicadores históricos, compara resultados y puede ejecutar escenarios What-If autorizados modificando parámetros analíticos configurables.

## 2.4 Conductor

Consulta las entregas que le fueron asignadas y registra cambios de estado y evidencia de entrega dentro de sus permisos.

## 2.5 Cliente

Consulta el estado y seguimiento disponible de su pedido, sin acceso a información interna del DSS, otros clientes o decisiones logísticas.

---

# 3. Módulo 1: Requerimientos Transaccionales (CRUD / OLTP)

## 3.1 Épica E-01 — Gestión de Pedidos

Permitir el registro y mantenimiento de la información operacional necesaria para ejecutar y analizar las entregas.

### HU-01 — Registrar pedidos

**Como** Administrador,
**quiero** registrar un pedido con cliente, ubicación, fecha límite, peso y nivel de urgencia,
**para** disponer de la información necesaria para su planificación y posterior evaluación.

**Criterios de aceptación:**

* El código del pedido debe ser único.
* El pedido debe estar asociado a un cliente existente.
* El pedido debe tener una ubicación válida.
* `peso_kg` debe ser mayor que cero.
* `urgencia` debe encontrarse entre 1 y 5.
* La fecha límite debe ser válida.
* Si una validación falla, el pedido no debe persistirse y el sistema debe informar el campo inválido.

---

## 3.2 Épica E-02 — Gestión de Recursos Logísticos

Gestionar los recursos que pueden participar en una asignación.

### HU-02 — Gestionar conductores

**Como** Administrador,
**quiero** registrar y actualizar conductores y su disponibilidad,
**para** conocer qué recursos humanos pueden participar en las entregas.

**Criterios de aceptación:**

* Cada conductor debe poseer un identificador único.
* La licencia no puede duplicarse.
* Debe registrarse su estado de disponibilidad.
* Los datos inválidos deben rechazarse antes de persistir el registro.

### HU-03 — Gestionar vehículos

**Como** Administrador,
**quiero** registrar vehículos, capacidad, rendimiento y disponibilidad,
**para** determinar qué vehículos pueden utilizarse en las asignaciones.

**Criterios de aceptación:**

* La placa debe ser única.
* `capacidad_kg` debe ser mayor que cero.
* `rendimiento_km_l` debe ser mayor que cero.
* El sistema debe registrar la disponibilidad del vehículo.

---

## 3.3 Épica E-03 — Gestión de Asignaciones

### HU-04 — Registrar una asignación logística

**Como** Responsable Logístico,
**quiero** asignar un pedido a un conductor y vehículo disponibles,
**para** registrar formalmente los recursos responsables de ejecutar la entrega.

**Criterios de aceptación:**

* El pedido debe existir y encontrarse en un estado válido para asignación.
* El conductor debe existir y estar disponible.
* El vehículo debe existir y estar disponible.
* La capacidad del vehículo debe ser suficiente para el peso del pedido.
* Una asignación inválida no debe persistirse.
* El sistema debe registrar la fecha de asignación.

---

## 3.4 Épica E-04 — Ejecución de Entregas

### HU-05 — Actualizar estado de entrega

**Como** Conductor,
**quiero** actualizar el estado de una entrega asignada,
**para** registrar su progreso operacional.

**Criterios de aceptación:**

* El conductor solo puede modificar entregas que le correspondan.
* Los cambios deben respetar la secuencia de estados definida.
* La entrega finalizada debe registrar su fecha de entrega.
* Una transición de estado no válida debe rechazarse.

---

# 4. Módulo 2: Requerimientos Analíticos (DSS / OLAP)

## 4.1 Integración ETL

Los datos operacionales almacenados en PostgreSQL OLTP serán extraídos, validados y transformados antes de cargarse en el esquema analítico `dw`.

El proceso ETL deberá:

1. Construir `DIM_TIEMPO` a partir de las fechas de entrega.
2. Comparar `fecha_entrega` con `fecha_limite` para determinar retrasos.
3. Validar que distancia, combustible y costo no contengan valores negativos.
4. Integrar ubicación operacional en atributos analíticos de zona, ciudad y departamento.
5. Excluir asignaciones canceladas, entregas no finalizadas y registros que no superen las reglas de calidad.

La granularidad de `FACT_ENTREGA` será:

> **Cada fila de FACT_ENTREGA representa una entrega individual ejecutada correspondiente a un pedido y su asignación logística.**

---

## 4.2 Épica E-05 — Análisis de Prioridad y Riesgo

### HU-DSS-01 — Consultar prioridad de pedidos

**Como** Responsable Logístico,
**quiero** obtener un índice de prioridad entre 0 y 100 para los pedidos pendientes,
**para** identificar cuáles requieren atención primero.

**Criterios de aceptación:**

* El índice debe encontrarse entre 0 y 100.
* El cálculo debe considerar únicamente los criterios configurados para el Motor DSS.
* Con los mismos datos y los mismos pesos, el resultado debe ser determinista.
* El sistema debe mostrar los criterios que influyeron en la puntuación.

### HU-DSS-02 — Identificar riesgo de retraso

**Como** Responsable Logístico,
**quiero** identificar pedidos con riesgo de retraso,
**para** anticipar problemas antes del incumplimiento de la fecha comprometida.

**Criterios de aceptación:**

* El sistema debe calcular un nivel cuantitativo de riesgo.
* El resultado debe estar asociado al pedido evaluado.
* Deben mostrarse las variables principales utilizadas para determinar el riesgo.
* La evaluación no debe modificar automáticamente la asignación existente.

---

## 4.3 Épica E-06 — Comparación y Recomendación

### HU-DSS-03 — Comparar alternativas de asignación

**Como** Responsable Logístico,
**quiero** comparar al menos dos alternativas válidas de asignación,
**para** seleccionar la opción logística más conveniente.

**Criterios de aceptación:**

* Cada alternativa debe mostrar puntuación, distancia estimada, combustible estimado y riesgo de retraso.
* Deben excluirse alternativas que incumplan disponibilidad o capacidad.
* Las alternativas deben utilizar los mismos criterios y pesos dentro de una misma evaluación.
* El sistema debe conservar la trazabilidad de la evaluación.

### HU-DSS-04 — Obtener recomendación explicable

**Como** Responsable Logístico,
**quiero** recibir una recomendación explicable entre las alternativas válidas,
**para** comprender por qué una opción obtiene una valoración superior antes de tomar la decisión.

**Criterios de aceptación:**

* El sistema debe identificar la alternativa recomendada.
* Debe mostrar su puntuación.
* Debe indicar los criterios con mayor influencia.
* Debe mostrar diferencias relevantes frente a las demás alternativas.
* La recomendación no debe ejecutar automáticamente la asignación.

---

## 4.4 Épica E-07 — Indicadores y Dashboard

### HU-DSS-05 — Consultar KPI de entregas tardías

**Como** Responsable Logístico,
**quiero** consultar el porcentaje de entregas tardías por período, zona, conductor y vehículo,
**para** identificar patrones de incumplimiento.

**Indicador:**

`SUM(entrega_tardia) / SUM(cantidad_entregas) * 100`

### HU-DSS-06 — Consultar KPI de distancia

**Como** Responsable Logístico,
**quiero** consultar kilómetros totales y promedio por período, zona, conductor y vehículo,
**para** analizar la eficiencia de los recorridos.

**Indicadores:**

* `SUM(distancia_km)`
* `AVG(distancia_km)`

### HU-DSS-07 — Consultar KPI de combustible

**Como** Responsable Logístico,
**quiero** consultar litros consumidos y costo estimado de combustible por período, zona y vehículo,
**para** analizar el uso de recursos logísticos.

**Indicadores:**

* `SUM(combustible_litros)`
* `SUM(costo_combustible)`
* litros promedio por entrega

---

# 5. Requerimientos No Funcionales

## RNF-01 — Rendimiento de consultas operacionales

Las operaciones CRUD comunes deberán responder en **menos de 2 segundos en el percentil 95 (p95)** utilizando un conjunto de prueba de hasta **1.000 pedidos**, excluyendo latencia de servicios externos.

## RNF-02 — Rendimiento del Dashboard DSS

Las consultas de los tres KPI principales deberán completar su procesamiento en **menos de 2 segundos en p95** sobre un conjunto de prueba de hasta **10.000 filas en FACT_ENTREGA**, dentro del entorno académico de referencia.

## RNF-03 — Determinismo del Motor DSS

Con idénticos datos de entrada, criterios, pesos y restricciones, el Motor DSS deberá producir la **misma puntuación y ordenamiento en el 100 % de ejecuciones repetidas**.

## RNF-04 — Integridad de datos

El **100 % de los registros persistidos** deberá satisfacer las restricciones PK, FK, UNIQUE, NOT NULL y CHECK definidas en el esquema correspondiente. Ningún registro que viole una restricción podrá confirmarse en la transacción.

## RNF-05 — Calidad ETL

El **100 % de los registros cargados en FACT_ENTREGA** deberá corresponder a entregas finalizadas que hayan superado las reglas ETL definidas. Los registros rechazados deberán identificarse durante el proceso de carga y no incorporarse silenciosamente a la tabla de hechos.

## RNF-06 — Trazabilidad DSS

El **100 % de las recomendaciones generadas** deberá conservar el identificador de la evaluación y los valores utilizados para comparar sus alternativas, permitiendo reconstruir la razón de la recomendación.

## RNF-07 — Usabilidad

Un Responsable Logístico deberá poder acceder desde el Dashboard DSS al detalle de una recomendación en un máximo de **3 interacciones de navegación**.

---

# 6. Puertas de Calidad (Quality Gates)

## 6.1 Definition of Ready (DoR)

Una Historia de Usuario estará lista para desarrollo únicamente cuando:

* [ ] Tiene un rol claramente identificado.
* [ ] Expresa una necesidad y un beneficio verificable.
* [ ] Posee criterios de aceptación observables.
* [ ] Sus dependencias están identificadas.
* [ ] Las entidades y datos necesarios están definidos.
* [ ] Se conoce si pertenece a OLTP, ETL, OLAP o Motor DSS.
* [ ] No contradice ninguna Boundary Rule.
* [ ] Puede implementarse sin modificar alcance no aprobado.
* [ ] Puede probarse de forma independiente o mediante dependencias explícitas.
* [ ] No contiene términos ambiguos como “rápido”, “mejor”, “inteligente” o “eficiente” sin una métrica asociada.

## 6.2 Definition of Done (DoD)

Una funcionalidad será considerada terminada únicamente cuando:

* [ ] Cumple todos sus criterios de aceptación.
* [ ] Las validaciones de entrada y restricciones de datos funcionan.
* [ ] Las pruebas asociadas finalizan satisfactoriamente.
* [ ] No introduce errores conocidos en funcionalidades existentes.
* [ ] Respeta las Boundary Rules del PRD.
* [ ] Las modificaciones de base de datos son coherentes con el modelo aprobado.
* [ ] Las funcionalidades DSS mantienen trazabilidad de los cálculos realizados.
* [ ] Los requisitos no funcionales aplicables fueron verificados.
* [ ] La documentación técnica afectada fue actualizada.
* [ ] Los cambios fueron versionados mediante Git con un commit descriptivo.

---

# 7. Mapeo de Arquitectura

```text
                    CAMPO LOGÍSTICA TARIJA DSS

                    +-----------------------+
                    |     USUARIOS CRUD     |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | PostgreSQL OLTP       |
                    |-----------------------|
                    | clientes              |
                    | pedidos               |
                    | ubicaciones           |
                    | conductores           |
                    | vehiculos             |
                    | asignaciones          |
                    | evaluaciones DSS      |
                    | alternativas          |
                    +-----------+-----------+
                                |
                    +-----------+-----------+
                    |                       |
                    v                       v
             +-------------+             +-----+
             | MOTOR DSS   |             | ETL |
             |-------------|             +--+--+
             | prioridad   |                |
             | riesgo      |                v
             | alternativas|       +--------------------+
             | recomendac. |       | DATA WAREHOUSE     |
             +------+------+       | PostgreSQL DW      |
                    |              |--------------------|
                    |              | FACT_ENTREGA       |
                    |              | DIM_TIEMPO         |
                    |              | DIM_CLIENTE        |
                    |              | DIM_CONDUCTOR      |
                    |              | DIM_VEHICULO       |
                    |              | DIM_UBICACION      |
                    |              +---------+----------+
                    |                        |
                    +------------+-----------+
                                 |
                                 v
                    +-----------------------+
                    |    DASHBOARD DSS      |
                    |-----------------------|
                    | KPIs                  |
                    | comparaciones         |
                    | recomendaciones       |
                    | histórico             |
                    +-----------+-----------+
                                |
                                v
                    +-----------------------+
                    | RESPONSABLE LOGÍSTICO |
                    |   DECISIÓN FINAL      |
                    +-----------------------+
```

## 7.1 Flujo analítico simplificado

```text
[PostgreSQL OLTP] --> [ETL] --> [Data Warehouse / OLAP]
                              --> [KPIs / Dashboard]
                              --> [Responsable Logístico]
```

El OLTP constituye la fuente operacional; ETL limpia, valida e integra los datos; el Data Warehouse conserva información preparada para análisis histórico y agregaciones; y el Motor DSS complementa esta arquitectura mediante evaluación de prioridad, riesgo y alternativas. La información resultante apoya al Responsable Logístico sin reemplazar su decisión.

---

# 8. Trazabilidad de Arquitectura

| Componente            | Responsabilidad principal                            |
| --------------------- | ---------------------------------------------------- |
| PostgreSQL OLTP       | Persistencia de operaciones CRUD                     |
| Motor DSS             | Prioridad, riesgo, comparación y recomendación       |
| ETL                   | Extracción, validación, transformación e integración |
| PostgreSQL DW         | Persistencia analítica e histórica                   |
| FACT_ENTREGA          | Métricas cuantitativas de entregas ejecutadas        |
| Dimensiones           | Contexto temporal, geográfico y operacional          |
| Dashboard DSS         | Visualización de KPI, análisis y recomendaciones     |
| Responsable Logístico | Decisión final                                       |

---

# 9. Alcance del MVP

El MVP contempla:

* gestión operacional básica;
* persistencia PostgreSQL;
* pedidos, clientes, ubicaciones, conductores y vehículos;
* asignaciones;
* estados de entrega;
* Motor DSS multicriterio;
* prioridad y riesgo;
* comparación de alternativas;
* recomendaciones explicables;
* proceso ETL;
* Data Warehouse con Esquema en Estrella;
* tres KPI logísticos;
* Dashboard DSS;
* análisis What-If básico.

Quedan fuera del MVP, salvo aprobación explícita:

* GPS real;
* aplicaciones móviles nativas;
* APIs comerciales de mapas;
* Machine Learning predictivo;
* predicción de tráfico;
* WhatsApp/SMS;
* asignación totalmente automática;
* optimización avanzada en producción;
* infraestructura comercial o servicios con costo.

---

# 10. Criterio de Éxito del Producto

El producto será considerado funcional a nivel MVP cuando permita registrar la información operacional definida, transformar entregas válidas hacia el Data Warehouse, calcular los tres KPI establecidos y proporcionar al Responsable Logístico información de prioridad, riesgo, comparación y recomendación con trazabilidad suficiente para fundamentar una decisión humana.
