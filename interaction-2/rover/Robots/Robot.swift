//
//  Robot.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//

import Foundation

/// Abstract base class for all your robots.
/// You never instantiate it directly.
/// You use Rover or Sphero, which inherit from it.
@Observable
class Robot {

    // MARK: - properties

    let bluetoothName: String
    private(set) var isConnected: Bool = false
    private(set) var batteryState: BatteryState = .unknown
    private(set) var lastSample: SensorSample = .empty
    private(set) var impactCount: Int = 0
    private var lastImpactTime: TimeInterval = 0
    
    // Impact Validation State
    private var candidateImpact: (time: TimeInterval, sample: SensorSample)?
    private var distanceTraveled: Double = 0
    
    var heading: Int = 0

    // MARK: - Simple callbacks

    var onConnect: (() -> Void)?
    var onDisconnect: (() -> Void)?
    var onSensorUpdate: ((SensorSample) -> Void)?
    var onBatteryUpdate: ((BatteryState) -> Void)?
    var onImpact: (() -> Void)?


    // MARK: - Init

    init(bluetoothName: String) {
        self.bluetoothName = bluetoothName
    }

    // MARK: - "Abstract" methods to override

    func connect() {
        fatalError("connect() must be overridden in the subclass")
    }

    func disconnect() {
        fatalError("disconnect() must be overridden in the subclass")
    }

    func forward(speed: Int, durationS: Int = 1) {
        fatalError("forward() must be overridden in the subclass")
    }

    func backward(speed: Int, durationS: Int = 1) {
        fatalError("backward() must be overridden in the subclass")
    }

    func turn(degrees: Int) {
        fatalError("turn() must be overridden in the subclass")
    }

    func stop() {
        fatalError("stop() must be overridden in the subclass")
    }

    func setMainLED(color: RobotColor) {
        fatalError("setMainLED() must be overridden in the subclass")
    }
}

// MARK: - Internal methods (for runners)

extension Robot {

    /// Called by the runner when Synchrosphere is ready.
    func _didConnect() {
        isConnected = true
        onConnect?()
    }

    /// Called by the runner when the controller is stopped.
    func _didDisconnect() {
        isConnected = false
        onDisconnect?()
    }

    /// Update sensors from Synchrosphere's `SyncsSample` type.
    func _updateFrom(syncsSample: SyncsSample) {
        let sample = SensorSample(
            x: syncsSample.x,
            y: syncsSample.y,
            vx: syncsSample.vx,
            vy: syncsSample.vy,
            ax: syncsSample.ax,
            ay: syncsSample.ay,
            yaw: syncsSample.yaw
        )
        
        // Update cumulative distance
        let dx = sample.x - lastSample.x
        let dy = sample.y - lastSample.y
        let dist = sqrt(dx*dx + dy*dy)
        distanceTraveled += Double(dist)
        
        let now = Date().timeIntervalSince1970
        
        // --- Validation Step ---
        if let candidate = candidateImpact {
            // Wait 1 second before validating
            if now - candidate.time >= 1.0 {
                // Check if robot is stable (stopped)
                // "Reste quasiment a la meme hauteur" -> interpreted as "Remains stable/stopped"
                // Check if current velocity is near zero
                let v = sqrt(sample.vx*sample.vx + sample.vy*sample.vy)
                if v < 0.1 {
                    impactCount += 1
                    lastImpactTime = now
                    print("✅ VALID IMPACT! Stable after 1s. Count: \(impactCount)")
                    onImpact?()
                } else {
                    print("❌ INVALID IMPACT: Robot still moving (v=\(v))")
                }
                candidateImpact = nil
            }
            // During the 1s wait, we just pass
            lastSample = sample
            onSensorUpdate?(sample)
            return
        }
        
        // --- Detection Step ---
        
        // 1. Acceleration Magnitude (Direct hit)
        let accelMag = sqrt(sample.ax*sample.ax + sample.ay*sample.ay)
        
        // 2. Delta Velocity (Hit missed by sampling rate)
        let dvx = sample.vx - (lastSample.vx)
        let dvy = sample.vy - (lastSample.vy)
        let deltaV = sqrt(dvx*dvx + dvy*dvy)
        
        // Thresholds
        let accelThreshold: Float = 2.5
        let velocityThreshold: Float = 0.2
        let minDistance: Double = 0.5 // 50 cm
        
        // Detect Trigger
        if (accelMag > accelThreshold || deltaV > velocityThreshold) {
            // Condition: Minimum Distance Traveled
            // User: "Il faut une distance minimum"
            if distanceTraveled > minDistance {
                 print("⚠️ POTENTIAL IMPACT (Mag: \(String(format: "%.2f", accelMag)), dV: \(String(format: "%.2f", deltaV))). Waiting 1s validation...")
                 candidateImpact = (time: now, sample: sample)
                 // Reset distance to require movement before next impact?
                 // distanceTraveled = 0
                 // Let's keep cumulative distance, but could verify distance *since last impact*.
                 // For now, simple check.
            } else {
                print("Ignored Impact: Distance too small (\(String(format: "%.2f", distanceTraveled))m)")
            }
        }
        
        lastSample = sample
        
        // Log for analysis
        print(String(format: "LOG_DATA: time=%.3f ax=%.3f ay=%.3f vx=%.3f vy=%.3f dv=%.3f mag=%.3f dist=%.2f",
                     now, sample.ax, sample.ay, sample.vx, sample.vy, deltaV, accelMag, distanceTraveled))
        
        onSensorUpdate?(sample)
    }

    /// Update the battery from `SyncsBatteryState` to your `BatteryState`.
    func _updateBattery(from syncsState: SyncsBatteryState?) {
        let newState: BatteryState
        
        if let s = syncsState {
            switch s {
            case .ok:
                newState = .ok
            case .low:
                newState = .low
            case .critical:
                newState = .critical
            @unknown default:
                newState = .unknown
            }
        } else {
            newState = .unknown
        }

        batteryState = newState
        onBatteryUpdate?(newState)
    }
}
