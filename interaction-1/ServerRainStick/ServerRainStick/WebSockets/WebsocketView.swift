//
//  WebsocketView.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//

import SwiftUI

struct WebsocketView: View {
    
    // MARK: - State
    @State private var wsManager: WebSocketManager? = nil
    @State private var tapCount: Int = 0
    @State private var isConnected: Bool = false
    
    private let serverURL: String = "ws://192.168.1.85:8000"
    private let senderId: String = "IPHONE-030101"
    private let receiverId: String = "SERVER-AE490F"
    
    // MARK: - Body
    
    var body: some View {
        VStack(spacing: 32) {
            // ===== HEADER =====
            VStack(spacing: 8) {
                Text("Server RainStick")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                Text("WebSocket trigger")
                    .foregroundColor(.secondary)
            }
            .padding(.top, 40)
            
            // ===== CONNECTION STATUS =====
            VStack(spacing: 8) {
                HStack(spacing: 8) {
                    Image(systemName: isConnected ? "wifi" : "wifi.slash")
                        .foregroundColor(isConnected ? .green : .red)
                    Text(isConnected ? "Connected" : "Disconnected")
                        .font(.headline)
                }
                
                Button(isConnected ? "Disconnect" : "Connect") {
                    if isConnected {
                        disconnectWebSocket()
                    } else {
                        connectWebSocket()
                    }
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 10)
                .background(isConnected ? Color.red : Color.blue)
                .foregroundColor(.white)
                .cornerRadius(12)
            }
            
            // ===== SHERO IMPACTS BUTTON =====
            VStack(spacing: 16) {
                Button(action: handleSheroTap) {
                    Text("shero impacts")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(isConnected ? Color.accentColor : Color.gray)
                        .foregroundColor(.white)
                        .cornerRadius(16)
                }
                .disabled(!isConnected)
                
                Text("Taps: \(tapCount) / 6")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal)
            
            Spacer()
        }
        .padding()
        .onAppear {
            // Optionnel : auto-connexion au lancement
            connectWebSocket()
        }
    }
    
    // MARK: - Actions
    
    private func connectWebSocket() {
        wsManager?.disconnect()
        
        let manager = WebSocketManager(serverURL: serverURL, deviceId: senderId)
        manager.onConnectionChanged = { connected in
            DispatchQueue.main.async {
                self.isConnected = connected
                if !connected {
                    self.tapCount = 0
                }
            }
        }
        
        wsManager = manager
        manager.connect()
    }
    
    private func disconnectWebSocket() {
        wsManager?.disconnect()
        wsManager = nil
        isConnected = false
        tapCount = 0
    }
    
    private func handleSheroTap() {
        tapCount += 1
        
        if tapCount >= 6 {
            sendSheroImpactFrame()
            tapCount = 0
        }
    }
    
    /// Construit et envoie le JSON demandé par le serveur
    private func sendSheroImpactFrame() {
        struct Status: Codable {
            let connection: Int
        }
        
        struct Metadata: Codable {
            let senderId: String
            let timestamp: Int
            let messageId: String
            let type: String
            let receiverId: String
            let status: Status
        }
        
        struct PayloadItem: Codable {
            let datatype: String
            let value: String
            let slug: String
        }
        
        struct SheroFrame: Codable {
            let metadata: Metadata
            let payload: [PayloadItem]
        }
        
        // Exemple conforme à la structure fournie
        let metadata = Metadata(
            senderId: senderId,
            timestamp: 1678886400,
            messageId: "MSG-20230315-0001",
            type: "up",
            receiverId: receiverId,
            status: Status(connection: 200)
        )
        
        let payload = [
            PayloadItem(datatype: "bool", value: "true", slug: "rain-stick")
        ]
        
        let frame = SheroFrame(metadata: metadata, payload: payload)
        
        do {
            let data = try JSONEncoder().encode(frame)
            guard let jsonString = String(data: data, encoding: .utf8) else { return }
            wsManager?.send(text: jsonString)
        } catch {
            print("Failed to encode SheroFrame: \(error)")
        }
    }
}

#Preview {
    WebsocketView()
}
