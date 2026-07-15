# SQLite migration V2

Migration progressive prévue :

users

- discord_id
- roblox_id
- username
- verified
- created_at
- updated_at

Le système actuel database.json reste compatible pendant la transition.

Objectif : migrer sans casser /verify, Flask ou Render.
