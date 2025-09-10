# NLP

Script de extracción de mensajes de Telegram (canales / grupos) usando Telethon.

## Configuración

1. Crea un archivo `.env` con:
	 - `api_id`
	 - `api_hash`
2. Se genera/usa automáticamente la sesión `session_name.session`.
3. Ejecuta:

```bash
./venv/bin/python telegram/extract_data_tg.py
```

Parámetros:

| Parámetro | Descripción |
|-----------|-------------|
| `group_username` | Username o ID del canal/grupo (`sin @`) |
| `n` | Días hacia atrás a extraer (si `extract_all=False`) |
| `batch_size` | Tamaño de lote para procesar mensajes |
| `limit` | Límite máximo de mensajes que Telethon intentará iterar |
| `extract_all` | Si es `True`, ignora el rango de fechas |

## Salida

Archivos JSON organizados por año y mes :

`Data/<group_username>/<YYYY>/mensajes_<group_username>_<YYYY-MM>.json`

Ejemplo: `Data/teleSUR_tv/2025/mensajes_teleSUR_tv_2025-09.json`

Fotos descargadas (organizadas por año/mes/día):

`Data/photos/<group_username>/<YYYY>/<MM>/<DD>/foto_YYYYMMDDTHHMMSS_msg<ID>_from<SENDER>.jpg`

Ejemplo:
`Data/photos/teleSUR_tv/2025/09/10/foto_20250910T065508_msg104224_from-1001283631731.jpg`

## Estructura del JSON generado

Cada archivo mensual es una lista de objetos. Estructura de cada mensaje:

```jsonc
{
	"text": "<contenido del mensaje>",              // Texto plano 
	"sender_id": "<id numérico del remitente>",    // ID del autor (string)
	"date": "2025-09-10T02:55:07+00:00",           // Fecha/hora en ISO 8601 (UTC)
	"bot": null,                                    // ID del bot si es reenviado vía bot, si no null
	"views": 598,                                   // Número de vistas del sms (en canales)
	"message_id": 104218,                           // ID único del mensaje dentro del canal/grupo
	"is_reply": false,                              // true si es respuesta a otro mensaje
	"reply_to": null,                               // ID del mensaje al que responde (o null)
	"reactions": {                                  // Diccionario: reacción -> conteo
		"👍": 25,
		"❤": 4
	},
	"total_reactions": 29,                          // Suma de todos los conteos de 'reactions'
	"photo_path": "Data/photos/teleSUR_tv/2025/09/10/foto_20250910T065508_msg104224_from-1001283631731.jpg" // null si no hay foto
}
```

## Ejemplo de archivo mensual

```jsonc
[
	{
		"text": "teleSUR...",
		"sender_id": "-1001283631731",
		"date": "2025-09-10T06:55:08+00:00",
		"bot": null,
		"views": 73,
		"message_id": 104224,
		"is_reply": false,
		"reply_to": null,
		"reactions": { "👍": 1, "🤔": 1 },
		"total_reactions": 2,
		"photo_path": "Data/photos/teleSUR_tv/2025/09/10/foto_20250910T065508_msg104224_from-1001283631731.jpg"
	}
]
```
