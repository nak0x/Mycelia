//
//  WebsocketRoverView.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//
//  Redesigned for Premium Dark UI

import SwiftUI

struct WebsocketRoverView: View {
    
    // MARK: - State
    
    @State private var serverURL: String = "ws://localhost:8000/ios"
    @State private var deviceId: String = "IOS-APP-001"
    @State private var targetDeviceId: String = "RV-B456"
    
    @State private var wsManager: WebSocketManager?
    @State private var robot: Robot?
    @State private var controller: RobotWebSocketController?
    
    @State private var showLogs: Bool = false
    
    // MARK: - Colors
    
    private let bgMain = Color(hex: "151622")
    private let bgCard = Color(hex: "202434")
    private let bgInput = Color(hex: "252942")
    private let accentBlue = Color(hex: "0088FF")
    private let accentRed = Color(hex: "FF4444")
    private let textPrimary = Color.white
    private let textSecondary = Color.white.opacity(0.6)
    
    // MARK: - Body
    
    var body: some View {
        ZStack {
            bgMain.ignoresSafeArea()
            
            VStack(spacing: 24) {
                
                // ===== HEADER =====
                VStack(spacing: 8) {
                    HStack {
                        Image(systemName: "globe")
                            .foregroundColor(accentBlue)
                            .font(.system(size: 24))
                        Text("Contrôle WebSocket du Rover")
                            .font(.system(size: 22, weight: .bold))
                            .foregroundColor(textPrimary)
                    }
                }
                .padding(.top, 20)
                
                // ===== CONFIGURATION =====
                VStack(spacing: 12) {
                    CustomTextField(text: $serverURL, placeholder: "Server URL", bg: bgInput, color: textPrimary)
                    CustomTextField(text: $deviceId, placeholder: "Device ID", bg: bgInput, color: textPrimary)
                    CustomTextField(text: $targetDeviceId, placeholder: "Target Device ID", bg: bgInput, color: textPrimary)
                }
                .padding()
                .background(bgCard)
                .cornerRadius(16)
                
                // ===== CONNEXION WEBSOCKET =====
                Button(action: {
                    if wsManager?.isConnected == true {
                        disconnectWebSocket()
                    } else {
                        connectWebSocket()
                    }
                }) {
                    HStack {
                        Image(systemName: wsManager?.isConnected == true ? "wifi" : "wifi.slash")
                        Text(wsManager?.isConnected == true ? "Connecté" : "Connecter")
                    }
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(wsManager?.isConnected == true ? Color.green : accentBlue)
                    .foregroundColor(.white)
                    .cornerRadius(12)
                }
                
                // ===== ROBOT CONTROL & STATS =====
                VStack(spacing: 16) {
                    
                    // Robot Connection Status
                    HStack {
                        Image(systemName: robot?.isConnected == true ? "antenna.radiowaves.left.and.right" : "antenna.radiowaves.left.and.right.slash")
                            .foregroundColor(robot?.isConnected == true ? .green : .gray)
                        Text(robot?.isConnected == true ? "Robot connecté" : "Robot déconnecté")
                            .font(.headline)
                            .foregroundColor(textPrimary)
                        
                        if (wsManager?.isConnected == true) && (robot?.isConnected == true) {
                            Spacer()
                            Image(systemName: "link")
                                .foregroundColor(.green)
                        }
                    }
                    
                    // Actions
                    if robot == nil || robot?.isConnected == false {
                        Button(action: {
                            if robot == nil { connectRobot() }
                            else { robot?.connect() }
                        }) {
                            Text(robot == nil ? "Connecter le Robot" : "Reconnecter le Robot")
                                .fontWeight(.semibold)
                                .frame(maxWidth: .infinity)
                                .padding()
                                .background(accentBlue)
                                .foregroundColor(.white)
                                .cornerRadius(12)
                        }
                    } else {
                        HStack(spacing: 12) {
                            Button(action: { robot?.disconnect(); controller = nil }) {
                                Text("Déconnecter le Robot")
                                    .fontWeight(.semibold)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(accentRed)
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                            }
                            
                            Button(action: disconnectRobot) {
                                Text("Supprimer")
                                    .fontWeight(.semibold)
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(Color.white.opacity(0.1))
                                    .foregroundColor(.white)
                                    .cornerRadius(12)
                            }
                        }
                    }
                    

                }
                .padding()
                .background(bgCard)
                .cornerRadius(16)
                
                // ===== ÉTAT & LOGS =====
                if wsManager != nil {
                    VStack(spacing: 8) {
                        Button(action: { showLogs.toggle() }) {
                            HStack {
                                Image(systemName: showLogs ? "chevron.down" : "chevron.right")
                                Text("Logs (\(wsManager?.logs.count ?? 0))")
                                    .font(.headline)
                                    .foregroundColor(textPrimary)
                                Spacer()
                            }
                        }
                        
                        if showLogs {
                            ScrollView {
                                VStack(alignment: .leading, spacing: 4) {
                                    ForEach(wsManager?.logs ?? [], id: \.self) { log in
                                        Text(log)
                                            .font(.system(size: 10, design: .monospaced))
                                            .foregroundColor(textSecondary)
                                            .frame(maxWidth: .infinity, alignment: .leading)
                                    }
                                }
                            }
                            .frame(height: 150)
                            .padding(8)
                            .background(Color.black.opacity(0.2))
                            .cornerRadius(8)
                            
                            Button(action: { wsManager?.clearLogs() }) {
                                Text("🗑️ Effacer les logs")
                                    .font(.caption)
                                    .foregroundColor(textSecondary)
                            }
                        }
                    }
                    .padding()
                    .background(bgCard)
                    .cornerRadius(12)
                }
                
                Spacer()
            }
            .padding()
        }
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
        // On garde le robot indépendant du WS
        controller = nil
        wsManager = nil
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
    WebsocketRoverView()
}
