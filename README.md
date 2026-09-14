
# CAMPO LOGÍSTICA TARIJA DSS

**Sistema de Soporte a Decisiones para la Gestión, Priorización y Optimización de Entregas en Tarija, Bolivia**

## 1. Visión del producto

> Una interfaz limpia, intuitiva y libre de distracciones que transforma datos logísticos complejos en indicadores, alertas, comparaciones y recomendaciones explicables para tomar decisiones rápidas y fundamentadas.

## 2. Objetivo UX

Diseñar una experiencia consistente y de baja carga cognitiva que permita:

- al usuario operativo registrar y actualizar datos con rapidez y sin errores;
- al responsable logístico identificar en pocos segundos los pedidos críticos;
- comparar alternativas de asignación y recorrido;
- comprender el impacto esperado en kilómetros, combustible y riesgo de retraso;
- explorar escenarios mediante análisis **What-If** sin necesidad de conocer detalles técnicos del motor DSS.

## 3. User Personas

### Perfil 1 — Operativo: Despachador Logístico

**Objetivo:** ingresar y mantener información confiable con la menor cantidad de pasos posible.

**Necesidades:**
- formularios simples;
- campos obligatorios visibles;
- validación inmediata;
- prevención de duplicados;
- confirmación en acciones destructivas;
- tablas con búsqueda y filtros.

### Perfil 2 — Estratégico: Responsable Logístico

**Objetivo:** comprender la situación operativa y decidir qué alternativa conviene en menos de cinco segundos.

**Necesita ver:**
- pedidos críticos;
- riesgo de retraso;
- kilómetros estimados;
- consumo estimado de combustible;
- ranking de prioridad;
- comparación de alternativas;
- recomendación DSS y explicación;
- KPIs de desempeño.

![User Personas](ux_strategy/user_personas.png)

## 4. Objetivos de interacción

| Pantalla | Objetivo |
|---|---|
| Login | Acceder según rol de forma rápida y segura. |
| Pedidos | Registrar, consultar y actualizar pedidos sin errores. |
| Conductores/Vehículos | Conocer disponibilidad y capacidad de los recursos. |
| Dashboard DSS | Detectar en segundos los casos que requieren atención. |
| Comparar alternativas | Evaluar distancia, combustible, riesgo y puntuación. |
| What-If | Modificar condiciones y observar cómo cambia la recomendación. |
| Seguimiento | Consultar estado, progreso y ubicación de la entrega. |
| Reportes | Revisar KPIs y resultados de las decisiones. |

## 5. Principios UX aplicados

- **Mínima sorpresa:** navegación y controles consistentes.
- **Revelación progresiva:** primero KPIs y alertas; los detalles aparecen al profundizar.
- **Prevención de errores:** validaciones visuales y confirmaciones.
- **Control del usuario:** el DSS recomienda; la persona decide.
- **Color funcional:** colores neutros para la interfaz y rojo/verde reservados para alertas o estados.
- **Accesibilidad:** texto legible y la información crítica no depende únicamente del color.
- **Drill-down:** desde un KPI o alerta se puede acceder al pedido o alternativa específica.

## 6. Arquitectura de navegación

![Arquitectura de Navegación](diagrams/navegacion_campo_logistica.png)

Flujo principal:

`Login → Menú principal → CRUD / Dashboard DSS → Comparar alternativas / What-If / Seguimiento / Reportes`

## 7. Prototipos

### Login
![Login](prototypes/login.png)

### CRUD de Pedidos
![CRUD Pedidos](prototypes/crud_pedidos.png)

### Dashboard DSS
![Dashboard DSS](prototypes/dashboard_dss.png)

## 8. Diferencia entre CRUD y DSS

El CRUD mantiene datos operativos de pedidos, clientes, conductores y vehículos. El componente DSS utiliza esos datos para **analizar criterios, comparar alternativas, calcular prioridad y riesgo, estimar kilómetros y combustible y generar recomendaciones explicables** para el responsable logístico.

## 9. KPIs principales

1. Porcentaje de errores de priorización/asignación.
2. Kilómetros totales y promedio por entrega.
3. Litros y costo estimado de combustible.
4. Porcentaje de entregas tardías.
5. Porcentaje de entregas a tiempo.
6. Cantidad de pedidos de prioridad alta.
7. Cantidad de entregas en riesgo.
8. Tasa de utilización de vehículos.

## 10. Estructura del repositorio

```text
campo-logistica-tarija-dss/
├── README.md
├── ux_strategy/
│   ├── README.md
│   └── user_personas.png
├── diagrams/
│   ├── README.md
│   └── navegacion_campo_logistica.png
└── prototypes/
    ├── README.md
    ├── login.png
    ├── crud_pedidos.png
    └── dashboard_dss.png
```


Proyecto académico — Sistemas de Soporte a Decisiones (DSS), 2026.
=======
# CAMPOLOGISTICA-DSS

