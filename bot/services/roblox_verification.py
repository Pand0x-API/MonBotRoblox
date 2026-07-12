import secrets
import time


class RobloxVerificationService:
    """Gestion des demandes de liaison Discord <-> Roblox."""

    def __init__(self):
        self.pending = {}

    def create_code(self, discord_id: int):
        code = secrets.token_hex(3).upper()
        self.pending[code] = {
            "discord_id": discord_id,
            "created": time.time()
        }
        return code

    def verify_code(self, code: str):
        data = self.pending.get(code.upper())

        if not data:
            return None

        if time.time() - data["created"] > 300:
            del self.pending[code.upper()]
            return None

        return data

    def remove(self, code: str):
        self.pending.pop(code.upper(), None)
