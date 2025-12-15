//
//  WebsocketView.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//

import SwiftUI

struct WebsocketView: View {
    
    // MARK: - State
    
    @State private var serverURL: String = "ws://localhost:8000/ios"
    @State private var deviceId: String = "IOS-APP-001"
    @State private var targetDeviceId: String = "RV-B456"
    
    @State private var wsManager: WebSocketManager?
    @State private var robot: Robot?
    @State private var controller: RobotWebSocketController?
    
    // SUPPRIMÉ : @State private var isRobotControlEnabled: Bool = false
    @State private var showLogs: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        VStack(spacing: 20) {
            
            // ===== HEADER =====
            Text("🌐 Contrôle WebSocket")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            // ===== CONFIGURATION =====
            VStack(spacing: 12) {
                TextField("URL du serveur", text: $serverURL)
                    .textFieldStyle(.roundedBorder)
                
                TextField("Device ID (cette app)", text: $deviceId)
                    .textFieldStyle(.roundedBorder)
                
                TextField("Target Device ID (robot)", text: $targetDeviceId)
                    .textFieldStyle(.roundedBorder)
            }
            .padding()
            .background(Color.gray.opacity(0.1))
            .cornerRadius(12)
            
            // ===== CONNEXION WEBSOCKET =====
            HStack(spacing: 15) {
                Button(action: connectWebSocket) {
                    HStack {
                        Image(systemName: wsManager?.isConnected == true ? "wifi" : "wifi.slash")
                        Text(wsManager?.isConnected == true ? "Connecté" : "Connecter")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(wsManager?.isConnected == true ? Color.green : Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
                }
                
                if wsManager?.isConnected == true {
                    Button(action: disconnectWebSocket) {
                        HStack {
                            Image(systemName: "xmark.circle")
                            Text("Déconnecter")
                        }
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                    }
                }
            }
            .padding(.horizontal)
            
            // ===== CONNEXION ROBOT =====
            if wsManager?.isConnected == true {
                VStack(spacing: 12) {
                    HStack {
                        Image(systemName: robot?.isConnected == true ? "antenna.radiowaves.left.and.right" : "antenna.radiowaves.left.and.right.slash")
                            .foregroundColor(robot?.isConnected == true ? .green : .gray)
                        Text(robot?.isConnected == true ? "Robot connecté" : "Robot déconnecté")
                            .font(.headline)
                    }
                    
                    if robot == nil {
                        Button(action: connectRobot) {
                            Text("Lier le Robot")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.orange)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                    } else if robot?.isConnected == false {
                        Button(action: { robot?.connect() }) {
                            Text("Reconnecter le Robot")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.orange)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                    }
                    
                    // SUPPRIMÉ : Le Toggle "Contrôle via WebSocket"
                    // Si on est ici (WS connecté + Robot connecté), le contrôle est actif par défaut.
                    if robot?.isConnected == true {
                        Text("✅ Pilotage distant actif")
                            .font(.caption)
                            .foregroundColor(.green)
                            .padding(.top, 4)
                    }
                }
                .padding()
                .background(Color.blue.opacity(0.1))
                .cornerRadius(12)
            }
            
            // ===== COMMANDES DE TEST (Envoyées via WS) =====
            if wsManager?.isConnected == true {
                VStack(spacing: 12) {
                    Text("🎮 Envoi de commandes (Via WS)")
                        .font(.headline)
                    
                    HStack(spacing: 10) {
                        Button("⬆️ Avant") {
                            sendTestCommand(.int(100), slug: "forward")
                        }
                        .buttonStyle(.borderedProminent)
                        
                        Button("⬇️ Arrière") {
                            sendTestCommand(.int(80), slug: "backward")
                        }
                        .buttonStyle(.borderedProminent)
                        
                        Button("🛑 Stop") {
                            sendTestCommand(.bool(true), slug: "stop")
                        }
                        .buttonStyle(.bordered)
                    }
                    
                    // Ajout des LEDs pour tester
                    HStack(spacing: 10) {
                         Button("🔴 R") { sendTestCommand(.bool(true), slug: "led-red") }
                         Button("🟢 G") { sendTestCommand(.bool(true), slug: "led-green") }
                         Button("🔵 B") { sendTestCommand(.bool(true), slug: "led-blue") }
                         Button("⚫️ Off") { sendTestCommand(.bool(true), slug: "led-off") }
                    }
                    .buttonStyle(.bordered)
                }
                .padding()
                .background(Color.purple.opacity(0.1))
                .cornerRadius(12)
            }
            
            // ===== ÉTAT & LOGS =====
            if wsManager != nil {
                VStack(spacing: 8) {
                    Button(action: { showLogs.toggle() }) {
                        HStack {
                            Image(systemName: showLogs ? "chevron.down" : "chevron.right")
                            Text("Logs (\(wsManager?.logs.count ?? 0))")
                                .font(.headline)
                            Spacer()
                        }
                    }
                    
                    if showLogs {
                        ScrollView {
                            VStack(alignment: .leading, spacing: 4) {
                                ForEach(wsManager?.logs ?? [], id: \.self) { log in
                                    Text(log)
                                        .font(.system(size: 10, design: .monospaced)) // Réduit un peu la taille
                                        .frame(maxWidth: .infinity, alignment: .leading)
                                }
                            }
                        }
                        .frame(height: 150)
                        .padding(8)
                        .background(Color.black.opacity(0.05))
                        .cornerRadius(8)
                        
                        Button("🗑️ Effacer les logs") {
                            wsManager?.clearLogs()
                        }
                        .font(.caption)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
            }
            
            Spacer()
        }
        .padding()
    }
    
    // MARK: - Actions
    
    private func connectWebSocket() {
        // Force la fermeture de l'ancien si existe
        wsManager?.disconnect()
        
        let newManager = WebSocketManager(serverURL: serverURL, deviceId: deviceId)
        
        // Callback de changement d'état (pour rafraichir la vue)
        newManager.onConnectionChanged = { _ in
            // SwiftUI rafraichira automatiquement grâce à @Observable ou les @State,
            // mais ici on s'assure que la vue sait que ça a changé.
        }
        
        self.wsManager = newManager
        newManager.connect()
    }
    
    private func disconnectWebSocket() {
        wsManager?.disconnect()
        // On ne nil pas wsManager tout de suite si on veut garder les logs,
        // mais pour une déconnexion propre :
        wsManager = nil
        controller = nil
        robot?.disconnect()
        robot = nil
    }
    
    private func connectRobot() {
        // Crée le robot (Rover par défaut)
        let newRobot = Rover(bluetoothName: targetDeviceId)
        
        // Configure les callbacks
        newRobot.onConnect = {
            print("✅ Robot relié à la passerelle WebSocket")
        }
        
        newRobot.onDisconnect = {
            print("❌ Robot déconnecté de la passerelle")
        }
        
        // Sauvegarde et connecte
        self.robot = newRobot
        newRobot.connect()
        
        // Crée le contrôleur (Le pont entre WS et Robot)
        if let wsManager = wsManager {
            controller = RobotWebSocketController(robot: newRobot, wsManager: wsManager)
            // PLUS DE configuration .isEnabled ici
        }
    }
    
    private func sendTestCommand(_ value: PayloadValue, slug: String) {
        // Envoie la commande au serveur, qui la renverra (probablement à nous-même si target = self
        // ou au robot si l'ID correspond).
        wsManager?.sendCommand(slug: slug, value: value, receiverId: targetDeviceId)
    }
}

#Preview {
    WebsocketView()
}
