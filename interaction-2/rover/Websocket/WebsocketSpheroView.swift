//
//  WebsocketView.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//
//  Redesigned for Premium Dark UI

import SwiftUI

struct WebsocketSpheroView: View {
    
    // MARK: - State
    
    @State private var serverURL: String = "ws://localhost:8000/ios"
    @State private var deviceId: String = "IOS-APP-001"
    @State private var targetDeviceId: String = "SB-0994"
    
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
                        Text("Contrôle WebSocket du Sphero")
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
                    
                    // Sensor Stats
                    if robot?.isConnected == true {
                        VStack(alignment: .leading, spacing: 16) {
                            
                            HStack {
                                StatView(icon: "chart.bar.fill", value: "\(robot?.impactCount ?? 0)", label: "Impacts", color: .red)
                                Spacer()
                                let vx = robot?.lastSample.vx ?? 0
                                let vy = robot?.lastSample.vy ?? 0
                                let v = sqrt(vx*vx + vy*vy) * 100
                                StatView(icon: "speedometer", value: String(format: "%.1f", v), label: "cm/s", color: .orange)
                            }
                            
                            Divider().background(Color.white.opacity(0.1))
                            
                            HStack(alignment: .top) {
                                let ax = robot?.lastSample.ax ?? 0
                                let ay = robot?.lastSample.ay ?? 0
                                VStack(alignment: .leading) {
                                    Text("ACCEL (g)")
                                        .font(.caption)
                                        .fontWeight(.bold)
                                        .foregroundColor(textSecondary)
                                    Text("X: \(String(format: "%+.2f", ax))")
                                    Text("Y: \(String(format: "%+.2f", ay))")
                                }
                                .font(.system(.footnote, design: .monospaced))
                                .foregroundColor(textPrimary)
                                
                                Spacer()
                                
                                let px = robot?.lastSample.x ?? 0
                                let py = robot?.lastSample.y ?? 0
                                VStack(alignment: .trailing) {
                                    Text("POS (m)")
                                        .font(.caption)
                                        .fontWeight(.bold)
                                        .foregroundColor(textSecondary)
                                    Text("X: \(String(format: "%+.2f", px))")
                                    Text("Y: \(String(format: "%+.2f", py))")
                                }
                                .font(.system(.footnote, design: .monospaced))
                                .foregroundColor(textPrimary)
                            }
                        }
                        .padding()
                        .background(Color.white)
                        .cornerRadius(12)
                    }
                }
                .padding()
                .background(bgCard)
                .cornerRadius(16)
                
                Spacer()
            }
            .padding()
        }
    }
    
    // MARK: - Actions
    
    private func connectWebSocket() {
        wsManager?.disconnect()
        let newManager = WebSocketManager(serverURL: serverURL, deviceId: deviceId)
        setupWSCallbacks(newManager)
        self.wsManager = newManager
        newManager.connect()
        refreshBridge()
    }
    
    private func disconnectWebSocket() {
        wsManager?.disconnect()
        controller = nil
        wsManager = nil
    }
    
    private func connectRobot() {
        let newRobot = Sphero(bluetoothName: targetDeviceId)
        newRobot.onConnect = { print("✅ Robot relié à la passerelle WebSocket") }
        newRobot.onDisconnect = { print("❌ Robot déconnecté de la passerelle") }
        self.robot = newRobot
        newRobot.connect()
        if let wsManager = wsManager, wsManager.isConnected {
            controller = RobotWebSocketController(robot: newRobot, wsManager: wsManager)
        }
    }

    private func disconnectRobot() {
        controller = nil
        robot?.disconnect()
        robot = nil
    }

    private func refreshBridge() {
        if let r = robot, r.isConnected, let ws = wsManager, ws.isConnected {
            controller = RobotWebSocketController(robot: r, wsManager: ws)
        } else {
            controller = nil
        }
    }

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

// MARK: - Components

struct CustomTextField: View {
    @Binding var text: String
    var placeholder: String
    var bg: Color
    var color: Color
    
    var body: some View {
        TextField("", text: $text)
            .placeholder(when: text.isEmpty) {
                Text(placeholder).foregroundColor(color.opacity(0.4))
            }
            .padding()
            .background(Color.white.opacity(0.05))
            .cornerRadius(10)
            .foregroundColor(color)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
    }
}

extension View {
    func placeholder<Content: View>(
        when shouldShow: Bool,
        alignment: Alignment = .leading,
        @ViewBuilder placeholder: () -> Content) -> some View {

        ZStack(alignment: alignment) {
            placeholder().opacity(shouldShow ? 1 : 0)
            self
        }
    }
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

struct StatView: View {
    let icon: String
    let value: String
    let label: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
                .padding(10)
                .background(color.opacity(0.1))
                .clipShape(Circle())
            
            VStack(alignment: .leading) {
                Text(value)
                    .font(.title3)
                    .fontWeight(.bold)
                    .foregroundColor(.black)
                Text(label)
                    .font(.caption)
                    .foregroundColor(.gray)
            }
        }
    }
}

#Preview {
    WebsocketSpheroView()
}
