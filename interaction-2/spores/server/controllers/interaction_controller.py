import asyncio
import json
from aiohttp import web
from ..utils.messages import build_fan_message, build_robot_command
from ..config import DEFAULT_IOS_TARGET

class InteractionController:
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager

    async def trigger_interaction_1(self):
        """
        Séquence d'interaction-1:
        1. Allumer les Fans (ESP32)
        2. Attendre 3 secondes
        3. Faire avancer le rover pendant 10 secondes (iOS)
        """
        print("\n" + "="*60)
        print("🎬 DÉCLENCHEMENT INTERACTION-1")
        print("="*60)

        # Étape 1: Allumer les Fans
        print("💡 Étape 1/5: Allumage des Fans...")
        fan_msg = build_fan_message(True)
        await self.ws_manager.send_to_esp32(fan_msg)

        # Étape 2: Attendre 3 secondes
        print("⏳ Étape 2/5: Attente de 3 secondes...")
        await asyncio.sleep(3)

        # Étape 3: Faire avancer le rover pendant 10 secondes
        print("🤖 Étape 3/5: Avancement du rover pendant 10 secondes...")
        forward_msg = build_robot_command("forward", [100, 10], DEFAULT_IOS_TARGET)
        await self.ws_manager.send_to_ios(forward_msg)

        # Étape 4: Attendre 5 secondes
        print("⏳ Étape 4/5: Attente de 5 secondes...")
        await asyncio.sleep(5)

        # Étape 5: Éteindre les Fans
        print("💡 Étape 5/5: Éteindre les Fans...")
        fan_msg = build_fan_message(False)
        await self.ws_manager.send_to_esp32(fan_msg)

        print("="*60)
        print("✅ INTERACTION-1 TERMINÉE")
        print("="*60 + "\n")

    async def http_trigger_handler(self, request):
        """Handler pour les requêtes HTTP POST"""
        if request.method != 'POST':
            return web.Response(status=405, text="Method Not Allowed")

        try:
            data = await request.json()
            print(f"\n📨 Requête POST reçue: {json.dumps(data, indent=2)}")

            # Vérifie si c'est la trame attendue
            payload = data.get("payload", [])
            for item in payload:
                if item.get("slug") == "interaction-1" and item.get("value") == "done":
                    print("🎯 Déclenchement de l'interaction-1 détecté!")
                    # Lance l'interaction en arrière-plan
                    asyncio.create_task(self.trigger_interaction_1())
                    return web.json_response({"status": "success", "message": "Interaction-1 déclenchée"})

            return web.json_response({"status": "ignored", "message": "Payload non reconnu"})

        except json.JSONDecodeError:
            return web.Response(status=400, text="Invalid JSON")
        except Exception as e:
            print(f"❌ Erreur HTTP: {e}")
            return web.Response(status=500, text=str(e))
