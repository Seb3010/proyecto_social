# T21 — JS mínimo — Vanilla JS solo si hace falta

## Intención

Determinar si el proyecto necesita una razón concreta y real para usar JavaScript del lado del cliente. Si existe, definir la implementación mínima. Si no existe, dejar la tarea cerrada sin agregar JS.

## Alcance

### Incluye
- Revisar todos los templates en busca de una necesidad real de JS (confirmación de acciones destructivas, mejoras de UX que no se resuelven en servidor)
- Crear un único `static/js/app.js` **solo si** se confirma una necesidad genuina
- Incluir el script en `templates/base.html` con `<script>` si fuera necesario

### No incluye
- Agregar JS por decoración o estética
- Duplicar validaciones del servidor en el cliente
- Introducir librerías o frameworks externos
- Agregar rutas, modelos o lógica de servidor
- Implementar funcionalidad de borrado (eso sería otra tarea)

## Hallazgos

### Resultado del análisis de templates

| Template | Posible necesidad de JS | Veredicto |
|---|---|---|
| `base.html` | Los flash messages podrían cerrarse solos después de unos segundos | **Marginal** — comodidad, el sistema funciona sin eso |
| `dashboard.html` | No existe acción destructiva | **Ninguna** — no hace falta confirmación |
| `listado.html` | La búsqueda ya es un form GET del servidor | **Ninguna** — funciona bien sin JS |
| `detalle.html` | Vista de solo lectura | **Ninguna** |
| `login.html` | Formulario simple con auth del servidor | **Ninguna** |
| `nueva_beca.html` | La validación ya está en `_validar_beca()` del servidor | **Ninguna** — duplicarla violaría la regla del proyecto |

### Observaciones clave

1. **No hay acciones destructivas.** Existe `delete()` en `models/scholarship.py`, pero no hay ruta ni botón en el dashboard. No hay nada que confirmar.
2. **La búsqueda es server-side.** Agregar debounce o AJAX no arregla ningún problema real; solo suma complejidad.
3. **La validación del servidor ya está completa.** Los formularios validan título, institución, fecha y link del lado del servidor. Repetir eso en JS no aporta valor.
4. **Los flash messages son el único candidato.** Pero cerrarlos automáticamente sería solo una mejora cosmética y de bajo impacto.

## Recomendación

**Marcar T21 como completa sin agregar JavaScript.**

No hay necesidad concreta, no decorativa y no redundante de JS en el estado actual del proyecto.

Agregar auto-cierre de flash messages introduciría un archivo `static/js/app.js` y un `<script>` en `base.html` para una mejora puramente estética. Eso va contra la regla del proyecto: usar JS solo si aporta comportamiento real.

## Si en el futuro aparece una acción de borrado

Si más adelante se conecta `models.scholarship.delete()` a una ruta real y se agrega un botón de eliminar en el dashboard, el patrón mínimo sería:

- `static/js/app.js` con un `confirm('¿Eliminar esta beca?')`
- `<script src="{{ url_for('static', filename='js/app.js') }}"></script>` en `base.html` antes de `</body>`

Sin frameworks, sin dependencias externas, sin abstracciones innecesarias.

## Archivos afectados

Ninguno. No se crean ni modifican archivos.

## Riesgos

Ninguno.

## Verificación

- [ ] Confirmar que todos los templates renderizan correctamente en rutas públicas y admin
- [ ] Confirmar que no existen archivos JS en `static/js/`
- [ ] Confirmar que `base.html` no carga JS externo

## Próximo paso

Cerrar T21. Si en el futuro se agrega una acción destructiva, volver a evaluar con el patrón mínimo definido arriba.
