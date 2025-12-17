from ..utils.messages import build_interaction_done_message

class InteractionController:
    def __init__(self, ws_manager):
        self.ws_manager = ws_manager
        self.balance_status = False
        self.sphero_status = False

    async def handle_message(self, websocket, data):
        """Processes incoming messages for interaction logic"""
        metadata = data.get("metadata", {})
        payload = data.get("payload", [])

        print(f"   Sender: {metadata.get('senderId', '')}")
        print(f"   Type: {metadata.get('type')}")
        print(f"   Payload: {payload}")

        # Logic: Detect Balance & Sphero statuses
        for item in payload:
            if item.get("slug") == "balance" and item.get("value") is True:
                print("🔄 BALANCE detected as TRUE")
                self.balance_status = True
            elif item.get("slug") == "sphero" and item.get("value") is True:
                print("🟣 SPHERO detected as TRUE")
                self.sphero_status = True

        # Check completion
        if self.balance_status and self.sphero_status:
            print("\n" + "="*60)
            print("✅ BALANCE + SPHERO = INTERACTION-2 DONE")
            print("="*60)
            
            done_message = build_interaction_done_message()
            # Broadcast result
            await self.ws_manager.broadcast(done_message, sender=websocket)
            
            # Reset
            self.balance_status = False
            self.sphero_status = False
            print("="*60 + "\n")

        # Log robot state
        if metadata.get('type') == 'robot-state':
            print("   📊 État du robot:")
            for item in payload:
                print(f"      - {item['slug']}: {item['value']}")

    def reset(self):
        self.balance_status = False
        self.sphero_status = False
