//
//  RobotWebSocketController.swift
//  IOTTools
//
//  Created by Jocelyn Marcilloux-Buisson on 15/12/2025.
//



import Foundation

/// Contrôleur qui écoute les frames WebSocket et pilote le Robot
class RobotWebSocketController {
    
    // MARK: - Properties
    
    private let robot: Robot
    private let wsManager: WebSocketManager
    
    
    // MARK: - Init
    
    init(robot: Robot, wsManager: WebSocketManager) {
        self.robot = robot
        self.wsManager = wsManager
        
        // S'abonne aux frames reçues
        wsManager.onFrameReceived = { [weak self] frame in
            self?.handleFrame(frame)
        }
    }
    
    // MARK: - Frame Handling
    
    /// Traite une frame reçue et exécute la commande sur le robot
    private func handleFrame(_ frame: Frame) {
        guard robot.isConnected else {
            print("⚠️ Robot non connecté, commande ignorée")
            return
        }
        
        // Traite chaque payload de la frame
        for payload in frame.payload {
            handlePayload(payload)
        }
    }
    
    /// Traite un payload individuel
    private func handlePayload(_ payload: Payload) {
        print("🎮 Commande reçue: \(payload.slug) = \(payload.value.anyValue)")
        
        // Routing des commandes par slug
        switch payload.slug {
            
        // ===== MOUVEMENTS =====
        case "forward":
            if let speed = payload.intValue {
                robot.forward(speed: speed)
            }
            
        case "backward":
            if let speed = payload.intValue {
                robot.backward(speed: speed)
            }
            
        case "turn":
            if let degrees = payload.intValue {
                robot.turn(degrees: degrees)
            }
            
        case "stop":
            robot.stop()
            
        case "heading":
            if let heading = payload.intValue {
                robot.heading = heading
            }
            
        // ===== LED =====
        case "led":
            if let colorData = payload.stringValue {
                let components = colorData.split(separator: ",").compactMap { UInt8($0) }
                if components.count == 3 {
                    let color = RobotColor(r: components[0], g: components[1], b: components[2])
                    robot.setMainLED(color: color)
                }
            }
            
        case "led-red":
            robot.setMainLED(color: .red)
        case "led-green":
            robot.setMainLED(color: .green)
        case "led-blue":
            robot.setMainLED(color: .blue)
        case "led-white":
            robot.setMainLED(color: .white)
        case "led-off":
            robot.setMainLED(color: .off)
            
        // ===== ACTIONS COMPOSÉES =====
        case "move":
            if let command = payload.stringValue {
                let parts = command.split(separator: ",")
                if parts.count == 2, let value = Int(parts[1]) {
                    switch parts[0] {
                    case "forward": robot.forward(speed: value)
                    case "backward": robot.backward(speed: value)
                    case "turn": robot.turn(degrees: value)
                    default: break
                    }
                }
            }
            
        default:
            print("⚠️ Commande inconnue: \(payload.slug)")
        }
    }
    
    // MARK: - Send Robot State
    // (Le reste de la classe reste identique pour l'envoi d'état)
    func sendRobotState() {
        guard robot.isConnected else { return }
        
        let payloads: [Payload] = [
            .bool(robot.isConnected, slug: "robot-connected"),
            .int(robot.heading, slug: "robot-heading"),
            .string(robot.batteryState.description, slug: "robot-battery"),
            .float(Double(robot.lastSample.x), slug: "robot-x"),
            .float(Double(robot.lastSample.y), slug: "robot-y"),
            .float(Double(robot.lastSample.yaw), slug: "robot-yaw")
        ]
        
        let frame = Frame(
            senderId: wsManager.deviceId,
            receiverId: "SERVER",
            type: "robot-state",
            payloads: payloads
        )
        
        wsManager.sendFrame(frame)
    }
}

// MARK: - BatteryState Extension
extension BatteryState: CustomStringConvertible {
    public var description: String {
        switch self {
        case .ok: return "ok"
        case .low: return "low"
        case .critical: return "critical"
        case .unknown: return "unknown"
        }
    }
}

// MARK: - Payload Value Helpers
extension Payload {
    /// Récupère la valeur en Int
    var intValue: Int? {
        return value.intValue
    }
    
    /// Récupère la valeur en String
    var stringValue: String? {
        return value.stringValue
    }
}
