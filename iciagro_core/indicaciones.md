# Especificación Funcional del Sistema

## 1. Gestión de Proveedores

### Objetivo

Administrar la información básica de los proveedores registrados en el sistema.

### Campos

| Campo     | Tipo       |
| --------- | ---------- |
| Código    | Automático |
| Nombre    | Texto      |
| Contacto  | Editable   |
| Ubicación | Editable   |

### Reglas de Negocio

1. Los campos **Contacto** y **Ubicación** deben ser editables.
2. Las modificaciones deben estar restringidas a usuarios autorizados.
3. Como mejora futura, se podrá implementar la eliminación y creación de proveedores.

---

# 2. Evaluación de Proveedores

## Objetivo

Registrar y calcular automáticamente la evaluación de desempeño de cada proveedor.

### Campos Automáticos

* Fecha de evaluación.
* Nombre del proveedor.
* Producto abastecido.

### Campos Seleccionables

* Código de proveedor (obtenido de la hoja o módulo de proveedores).

### Campos Manuales

* Criterios de evaluación.
* Observaciones.

### Reglas de Negocio

1. Al seleccionar un proveedor, se debe completar automáticamente:

   * Nombre.
   * Producto abastecido.
2. El sistema debe calcular automáticamente una nota final de 0 a 100.

### Clasificación Automática

| Rango      | Resultado      |
| ---------- | -------------- |
| 90 - 100   | Excelente      |
| 75 - 89    | Aceptable      |
| 60 - 74    | Condicionado   |
| Menor a 60 | No recomendado |

---

# 3. Gestión de Clientes

## Objetivo

Registrar información operativa relacionada con clientes.

### Campos Seleccionables

* Cliente.
* No aplica.

### Campos Manuales

* Contacto.
* Frecuencia.
* Punto de entrega.
* Observaciones.

### Reglas de Negocio

1. Debe existir una lista desplegable con los clientes registrados.
2. Debe permitirse ingresar información manualmente cuando sea necesario.
3. Debe existir la opción **No aplica** para datos no disponibles.

---

# 4. Recepción de Materia Prima

## Objetivo

Registrar el ingreso de materia prima proveniente de proveedores.

### Datos Generados Automáticamente

* Fecha.
* Día juliano.
* Código de recepción.

### Formato del Código

```text
REC-AÑODÍAJULIANO-CONSECUTIVO
```

Ejemplo:

```text
REC-26123001
```

### Campos Seleccionables

* Proveedor.
* Estado.
* Responsable.

### Campos Manuales

* Cantidad recibida.
* Unidad de medida.

### Reglas de Negocio

#### Selección de proveedor

1. La lista debe obtenerse desde el catálogo de proveedores.
2. Al seleccionar un proveedor, la materia prima debe completarse automáticamente.

#### Caso especial

* El proveedor **PROV-001** puede suministrar más de una materia prima.
* Para este proveedor se deberá habilitar una lista de selección de producto.

#### Estados permitidos

* Aceptado.
* Rechazado.

#### Validaciones

1. Si el estado es **Aceptado**, se genera el código de recepción.
2. Si el estado es **Rechazado**, no se genera el código de recepción.
3. Los responsables deben seleccionarse desde una lista predefinida.

---

# 5. Producción Interna

## Objetivo

Controlar la creación de lotes internos de producción.

### Datos Generados Automáticamente

* Fecha.
* Día juliano.
* Lote interno.

### Productos Disponibles

* HOB
* HOG
* HOR

### Formato del Lote

```text
HP-AÑODÍAJULIANO-CODIGO-CONSECUTIVO
```

### Reglas de Negocio

1. Cada código de producto mantiene su propio consecutivo.
2. Si un producto ya posee registros previos, el consecutivo debe continuar desde el último valor generado.
3. El sistema debe construir automáticamente el lote interno.

### Campos Manuales

* Kilogramos de sustrato.
* Gramos de micelio.
* Temperatura de pasteurización.
* Tiempo de pasteurización.
* Tiempo de secado.
* Observaciones.

### Responsable

Selección mediante lista predefinida.

---

# 6. Producto Terminado

## Objetivo

Registrar el proceso de empaque y cierre de producción.

### Campos Seleccionables

* Fecha de cosecha.
* Fecha de empaque.
* Lote interno.
* Responsable.
* Estado.

### Campos Manuales

* Presentación.
* Cantidad empacada.
* Unidad.
* Temperatura de refrigeración.

### Reglas de Negocio

1. Las fechas de cosecha y empaque pueden ser diferentes.
2. El usuario debe seleccionar un lote proveniente de Producción Interna.
3. Una vez utilizado, el lote no podrá reutilizarse.
4. Al seleccionar un lote:

   * Deben cargarse automáticamente sus datos asociados.
5. Estados permitidos:

   * Aceptado.
   * Rechazado.

---

# 7. Expedición y Ventas

## Objetivo

Registrar las ventas y despachos de producto terminado.

### Clientes Disponibles

* CL-001
* CL-002
* CL-003

### Productos Disponibles

* HOB
* HOG
* HOR

### Campos Manuales

* Cantidad.
* Unidad.
* Destino.

### Reglas de Negocio

1. Al seleccionar un cliente, debe mostrarse automáticamente su tipo.
2. El lote vendido debe provenir de Producto Terminado.
3. Solo podrán seleccionarse lotes con estado **Aceptado**.
4. Los lotes rechazados no deben mostrarse.
5. El responsable debe seleccionarse desde una lista predefinida.
6. La condición de entrega podrá ser:

   * Aceptado.
   * Rechazado.

---

# 8. Retiro de Producto

## Objetivo

Gestionar eventos de retiro o inmovilización de producto.

### Datos Automáticos

* Fecha.
* Código de retiro.

### Formato del Código

```text
RET-AÑODÍAJULIANO
```

Ejemplo:

```text
RET-26123
```

### Campos Manuales

* Origen del aviso.
* Motivo.
* Acción inmediata.
* Comunicación realizada.

### Campos Seleccionables

* Lote afectado.
* Cliente relacionado.
* Responsable.
* Producto inmovilizado.

### Reglas de Negocio

1. Solo deben mostrarse lotes aceptados provenientes de Expedición y Ventas.
2. Una vez utilizado un lote en un retiro, este debe quedar bloqueado.
3. Producto inmovilizado:

   * Sí.
   * No.
4. La cantidad afectada debe completarse automáticamente al seleccionar el lote.

---

# 9. Generación de Etiquetas

## Objetivo

Automatizar la generación de etiquetas de trazabilidad.

---

## 9.1 Etiqueta de Producción

### Entrada

Selección de lote interno (HP).

### Información Transferida

* Fecha de producción.
* Lote interno.
* Código de producto.
* Cantidad de sustrato utilizada.
* Cantidad de micelio utilizada.

### Información Fija

* Datos de la empresa.

---

## 9.2 Etiqueta de Producto Final

### Información Fija

* Nombre del producto.
* Condiciones de conservación.
* Productor.

### Información Transferida

* Fecha de cosecha.
* Fecha de empaque.
* Presentación.

### Reglas de Negocio

Toda la información deberá obtenerse automáticamente del lote asociado para garantizar la trazabilidad completa del producto.
# Matriz de Origen de Datos Automáticos

Esta sección define el origen de todos los campos que deben completarse automáticamente dentro del sistema.

---

## Evaluación de Proveedores

### Módulo origen: Proveedores

Al seleccionar un código de proveedor, el sistema debe completar automáticamente:

| Campo Destino        | Campo Origen         |
| -------------------- | -------------------- |
| Nombre del proveedor | Nombre del proveedor |
| Producto abastecido  | Producto abastecido  |

---

## Recepción de Materia Prima

### Módulo origen: Proveedores

Al seleccionar un proveedor, el sistema debe completar automáticamente:

| Campo Destino          | Campo Origen                         |
| ---------------------- | ------------------------------------ |
| Nombre del proveedor   | Nombre del proveedor                 |
| Materia prima asociada | Producto abastecido por el proveedor |

### Excepción

Para el proveedor **PROV-001**, el sistema debe permitir seleccionar manualmente la materia prima debido a que abastece más de un producto.

---

## Producción Interna

### Datos generados por el sistema

| Campo                    | Origen  |
| ------------------------ | ------- |
| Fecha                    | Sistema |
| Día juliano              | Sistema |
| Consecutivo por producto | Sistema |
| Lote interno             | Sistema |

### Construcción del lote interno

```text
HP-AÑODÍAJULIANO-CODIGOPRODUCTO-CONSECUTIVO
```

---

## Producto Terminado

### Módulo origen: Producción Interna

Al seleccionar un lote interno, el sistema debe recuperar automáticamente toda la información asociada al lote.

| Campo Destino             | Campo Origen       |
| ------------------------- | ------------------ |
| Lote interno              | Producción Interna |
| Código de producto        | Producción Interna |
| Fecha de producción       | Producción Interna |
| Cantidad de sustrato      | Producción Interna |
| Cantidad de micelio       | Producción Interna |
| Responsable de producción | Producción Interna |

### Campos que permanecen manuales

* Presentación.
* Cantidad empacada.
* Unidad.
* Temperatura de refrigeración.

---

## Expedición y Ventas

### Módulo origen: Clientes

Al seleccionar un cliente:

| Campo Destino   | Campo Origen |
| --------------- | ------------ |
| Tipo de cliente | Clientes     |

### Módulo origen: Producto Terminado

Los lotes disponibles deben provenir únicamente de registros aceptados en Producto Terminado.

| Campo Destino   | Campo Origen       |
| --------------- | ------------------ |
| Lote vendido    | Producto Terminado |
| Estado del lote | Producto Terminado |

### Restricción

Los lotes con estado **Rechazado** no deben mostrarse para selección.

---

## Retiro de Producto

### Módulo origen: Expedición y Ventas

Los lotes afectados deben provenir únicamente de ventas previamente registradas.

| Campo Destino       | Campo Origen        |
| ------------------- | ------------------- |
| Lote afectado       | Expedición y Ventas |
| Cliente relacionado | Expedición y Ventas |
| Cantidad afectada   | Expedición y Ventas |

### Restricción

Una vez que un lote sea utilizado en un retiro de producto, no podrá volver a seleccionarse para otro retiro.

---

## Etiqueta de Producción

### Módulo origen: Producción Interna

Al seleccionar un lote interno (HP), la etiqueta debe obtener automáticamente:

| Campo Etiqueta         | Campo Origen       |
| ---------------------- | ------------------ |
| Fecha de producción    | Producción Interna |
| Lote interno           | Producción Interna |
| Código de producto     | Producción Interna |
| Kilogramos de sustrato | Producción Interna |
| Gramos de micelio      | Producción Interna |

### Información fija

* Datos de la empresa.

---

## Etiqueta de Producto Final

### Módulo origen: Producto Terminado

Al seleccionar un lote terminado, la etiqueta debe obtener automáticamente:

| Campo Etiqueta   | Campo Origen       |
| ---------------- | ------------------ |
| Fecha de cosecha | Producto Terminado |
| Fecha de empaque | Producto Terminado |
| Presentación     | Producto Terminado |

### Información fija

* Nombre del producto.
* Condiciones de conservación.
* Productor.

---

# Flujo General de Dependencias

```text
PROVEEDORES
│
├── Evaluación de Proveedores
└── Recepción de Materia Prima
        │
        ▼
Producción Interna
        │
        ▼
Producto Terminado
        │
        ▼
Expedición y Ventas
        │
        ▼
Retiro de Producto

Producción Interna
        └── Etiqueta de Producción

Producto Terminado
        └── Etiqueta de Producto Final