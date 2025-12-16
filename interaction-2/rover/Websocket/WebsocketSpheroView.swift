//
//  WebsocketView.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//

import SwiftUI

struct WebsocketSpheroView: View {
    
    // MARK: - State
    
    @State private var serverURL: String = "ws://localhost:8000/ios"
    @State private var deviceId: String = "IOS-APP-001"
    @State private var targetDeviceId: String = "SB-0994"
    
    @State private var wsManager: WebSocketManager?
    @State private var robot: Robot?
    @State private var controller: RobotWebSocketController?
    
    // SUPPRIMÉ : @State private var isRobotControlEnabled: Bool = false
    @State private var showLogs: Bool = false
    
    // MARK: - Body
    
    var body: some View {
        VStack(spacing: 20) {
            
            // ===== HEADER =====
            Text("🌐 Contrôle WebSocket du Sphero")
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
            
            // ===== CONNEXION ROBOT (indépendant du WebSocket) =====
            VStack(spacing: 12) {
                HStack {
                    Image(systemName: robot?.isConnected == true ? "antenna.radiowaves.left.and.right" : "antenna.radiowaves.left.and.right.slash")
                        .foregroundColor(robot?.isConnected == true ? .green : .gray)
                    Text(robot?.isConnected == true ? "Robot connecté" : "Robot déconnecté")
                        .font(.headline)
                }

                if robot == nil {
                    Button(action: connectRobot) {
                        Text("Connecter le Robot")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.orange)
                            .foregroundColor(.white)
                            .cornerRadius(10)
                    }
                } else if robot?.isConnected == false {
                    HStack(spacing: 12) {
                        Button(action: { robot?.connect() }) {
                            Text("Reconnecter le Robot")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.orange)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        Button(action: disconnectRobot) {
                            Text("Supprimer")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.gray)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                    }
                } else {
                    HStack(spacing: 12) {
                        Button(action: { robot?.disconnect(); controller = nil }) {
                            Text("Déconnecter le Robot")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.red)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                        Button(action: disconnectRobot) {
                            Text("Supprimer")
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(Color.gray)
                                .foregroundColor(.white)
                                .cornerRadius(10)
                        }
                    }
                }

                // Indicateur de pont actif seulement si WS connecté + robot connecté
                if (wsManager?.isConnected == true) && (robot?.isConnected == true) {
                    Text("✅ Pilotage distant actif (pont WebSocket ↔︎ Robot)")
                        .font(.caption)
                        .foregroundColor(.green)
                        .padding(.top, 4)
                }
            }
            .padding()
            .background(Color.blue.opacity(0.1))
            .cornerRadius(12)
            
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

        // Callbacks de connexion pour (re)créer le pont si nécessaire
        setupWSCallbacks(newManager)

        self.wsManager = newManager
        newManager.connect()
        // Si le robot est déjà prêt, tente de créer le pont
        refreshBridge()
    }
    
    private func disconnectWebSocket() {
        wsManager?.disconnect()
        controller = nil
        wsManager = nil
    }
    
    private func connectRobot() {
        // Crée le robot (Sphero par défaut)
        let newRobot = Sphero(bluetoothName: targetDeviceId)
        
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
        
        // Crée le contrôleur (pont) si WS déjà connecté
        if let wsManager = wsManager, wsManager.isConnected {
            controller = RobotWebSocketController(robot: newRobot, wsManager: wsManager)
        }
    }

    private func disconnectRobot() {
        controller = nil
        robot?.disconnect()
        robot = nil
    }

    // Recrée/retire le pont en fonction des connexions
    private func refreshBridge() {
        if let r = robot, r.isConnected, let ws = wsManager, ws.isConnected {
            controller = RobotWebSocketController(robot: r, wsManager: ws)
        } else {
            controller = nil
        }
    }

    // Hook dans connectWebSocket pour gérer le pont dynamiquement
    private func setupWSCallbacks(_ manager: WebSocketManager) {
        manager.onConnectionChanged = { isConnected in
            if !isConnected {
                controller = nil
            } else {
                refreshBridge()
            }
        }
    }
}

#Preview {
    WebsocketSpheroView()
}
