# AGENTS.md

## Estado del repo verificado
- El directorio del repo estaba vacio al momento de crear este archivo. No hay `README`, manifiestos, lockfiles, workflows, ni scripts verificables todavia.
- No inventes comandos de setup, run, test o lint. Primero busca fuentes ejecutables reales cuando existan.

## Intencion y preferencias del usuario (no verificadas en codigo)
- App web monolitica para mostrar informacion de becas.
- Arquitectura MVC.
- Frontend esperado: `HTML`, `CSS` y `vanilla JS` lo mas basico posible.
- No usar frameworks de frontend ni librerias externas salvo que una necesidad futura verificada lo justifique.
- Backend esperado: `Python`, `Flask` y `SQLite`.
- El acceso a base de datos debe usar `sqlite3` de la libreria estandar directamente.
- No usar ORM ni abstracciones que oculten SQL salvo que una necesidad futura verificada lo fuerce.
- Debe existir login para usuario admin.
- La interfaz cambia para admin; el admin agrega y edita la informacion de becas publicada.

## Como arrancar futuras sesiones
- Lee primero `README*`, manifiestos raiz, lockfiles, config de Flask/Python, workflows CI y cualquier archivo de instrucciones antes de asumir estructura o comandos.
- Si el codigo ya existe, identifica entrypoints reales antes de cambiar arquitectura. En este proyecto deberian aparecer claramente las capas `models`, `views` y `controllers` o su equivalente Flask.
- Trata la experiencia admin como un flujo distinto de la vista publica. No mezcles permisos de edicion con la UI publica.
- Si aparecen decisiones en codigo que contradicen el brief, confia en el codigo y actualiza este archivo.

## Señales que vale la pena documentar cuando el repo crezca
- Comando exacto para levantar Flask en desarrollo.
- Ubicacion real de la base SQLite y como se inicializa.
- Como se resuelve autenticacion admin y persistencia de sesion.
- Estructura MVC real y entrypoints HTTP.
- Cualquier script de carga/edicion de becas o migraciones.

## Convenciones del equipo (verificadas en código)
- **task_list.csv NO es fuente de verdad**: Antes de confiar en el estado de una tarea ([x]), verificar siempre contra el código real y la base de datos. El CSV se actualiza DESPUÉS de que el código está verificado.
- Formato: `[x]` = completada, `[ ]` = pendiente.
- Para verificar una tarea de base de datos: ejecutar consulta SQL directa o leer los archivos de esquema/código correspondientes.
