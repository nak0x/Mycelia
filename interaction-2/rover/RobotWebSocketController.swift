//
//  RobotWebSocketController.swift
//  IOTTools
//
//  Created by Jocelyn Marcilloux-Buisson on 15/12/2025.
//

import Foundation

class RobotWebSocketController {
    
    private let robot: Robot
    private let wsManager: WebSocketManager
    
    init(robot: Robot, wsManager: WebSocketManager) {
        self.robot = robot
        self.wsManager = wsManager
        
        wsManager.onFrameReceived = { [weak self] frame in
            self?.handleFrame(frame)
        }
    }
    
    private func handleFrame(_ frame: Frame) {
        guard robot.isConnected else {
            print("⚠️ Robot non connecté, commande ignorée")
            return
        }
        for payload in frame.payload {
            handlePayload(payload)
        }
    }
    
    private func handlePayload(_ payload: Payload) {
        print("🎮 Commande reçue: \(payload.slug) = \(payload.value.anyValue)")
        
        switch payload.slug {
            
        // ===== MOUVEMENTS =====
        case "forward":
            if let params = payload.value.intArrayValue, !params.isEmpty {
                let speed = params[0]
                let duration = params.count > 1 ? params[1] : 1
                robot.forward(speed: speed, durationS: duration)
            }
            else if let speed = payload.intValue {
                robot.forward(speed: speed, durationS: 1)
            }
            
        case "backward":
            if let params = payload.value.intArrayValue, !params.isEmpty {
                let speed = params[0]
                let duration = params.count > 1 ? params[1] : 1
                robot.backward(speed: speed, durationS: duration)
            }
            else if let speed = payload.intValue {
                robot.backward(speed: speed, durationS: 1)
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
            
        case "led-red":   robot.setMainLED(color: .red)
        case "led-green": robot.setMainLED(color: .green)
        case "led-blue":  robot.setMainLED(color: .blue)
        case "led-white": robot.setMainLED(color: .white)
        case "led-off":   robot.setMainLED(color: .off)
            
        default:
            print("⚠️ Commande inconnue ou mal formatée: \(payload.slug)")
        }
    }
    
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
