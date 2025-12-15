//
//  SpheroRunner.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 02/12/2025.
//

import Foundation
import Pappe

/// Runner dedicated to Sphero-like devices (Mini / Bolt).
/// - Uses Synchrosphere + Pappe the same way as RoverRunner.
/// - Executes pending commands synchronously in the Pappe loop.
/// - Reads command duration (ms) for forward/back/turn (default handled by RobotCommand).
final class SpheroRunner {

    // MARK: - Properties

    unowned let robot: Robot

    private let engine = SyncsEngine()
    private var controller: SyncsController?
    private var config: SyncsControllerConfig?

    /// Next command to execute (nil = idle)
    var pendingCommand: RobotCommand?

    // MARK: - Init

    init(robot: Robot) {
        self.robot = robot
    }

    // MARK: - Connect

    func connect() {

        //------------------------------------------------------
        // 1) Configure controller (logs + callbacks)
        //------------------------------------------------------
        var cfg = SyncsControllerConfig(deviceSelector: .anyBolt)
        cfg.logLevel = .info

        cfg.stateDidChangeCallback = { [weak self] state in
            guard let self = self else { return }

            // Consider "connected" once the robot is awake.
            if state.contains(.isAwake), !self.robot.isConnected {
                DispatchQueue.main.async { self.robot._didConnect() }
            }

            // Consider "disconnected" if the BLE link drops.
            if !state.contains(.isConnected), self.robot.isConnected {
                DispatchQueue.main.async { self.robot._didDisconnect() }
            }

            // Best-effort battery feedback from controller state flags.
            if state.contains(.isBatteryCritical) {
                DispatchQueue.main.async { self.robot._updateBattery(from: .critical) }
            } else if state.contains(.isBatteryLow) {
                DispatchQueue.main.async { self.robot._updateBattery(from: .low) }
            } else {
                DispatchQueue.main.async { self.robot._updateBattery(from: .ok) }
            }
        }

        self.config = cfg

        //------------------------------------------------------
        // 2) Build Pappe controller
        //------------------------------------------------------
        controller = engine.makeController(for: cfg) { names, ctx in

            activity(names.Main, [
                "cmdSpeed",
                "cmdHeading",
                "cmdDir",
                "cmdSeconds",
                "doRollForSeconds",
                "doStop"
            ]) { val in

                //------------------------------------------------------
                // Initialize Pappe vars once
                //------------------------------------------------------
                exec {
                    val.cmdSpeed = SyncsSpeed(0)
                    val.cmdHeading = SyncsHeading(0)
                    val.cmdDir = SyncsDir.forward
                    val.cmdSeconds = 1

                    val.doRollForSeconds = false
                    val.doStop = false
                }

                //------------------------------------------------------
                // Main loop
                //------------------------------------------------------
                `repeat` {

                    //------------------------------------------------------
                    // 1) SWIFT → PAPPE binding (allowed here)
                    //------------------------------------------------------
                    exec {
                        // Reset flags
                        val.doRollForSeconds = false
                        val.doStop = false

                        guard let cmd = self.pendingCommand else { return }

                        // Helpers (Swift only)
                        func clampSpeed(_ s: Int) -> SyncsSpeed {
                            let v = max(0, min(255, s))
                            return SyncsSpeed(UInt8(v))
                        }

                        func clampHeading(_ h: Int) -> SyncsHeading {
                            // normalize to 0...359
                            let norm = ((h % 360) + 360) % 360
                            return SyncsHeading(UInt16(norm))
                        }

                        func msToSeconds(_ ms: Int) -> Int {
                            // Synchrosphere offers RollForSeconds(seconds: Int)
                            // Keep it simple: minimum 1 second.
                            let clamped = max(1, ms)
                            let secs = Int(ceil(Double(clamped) / 1000.0))
                            return max(1, secs)
                        }

                        // Defaults
                        var speed: SyncsSpeed = 0
                        var heading: SyncsHeading = clampHeading(self.robot.heading)
                        var dir: SyncsDir = .forward
                        var seconds: Int = 1
                        var shouldRoll = false
                        var shouldStop = false

                        switch cmd {

                        case .forward(let s, let durationMs):
                            speed = clampSpeed(s)
                            heading = clampHeading(self.robot.heading)
                            dir = SyncsDir.forward
                            seconds = msToSeconds(durationMs)
                            shouldRoll = true

                        case .backward(let s, let durationMs):
                            speed = clampSpeed(s)
                            heading = clampHeading(self.robot.heading)
                            dir = SyncsDir.backward
                            seconds = msToSeconds(durationMs)
                            shouldRoll = true

                        case .turn(let headingDeg, let durationMs):
                            // Simple turning command: speed 0 towards heading.
                            // (The actual behavior depends on device firmware.)
                            speed = clampSpeed(0)
                            heading = clampHeading(headingDeg)
                            dir = SyncsDir.forward
                            seconds = msToSeconds(durationMs)
                            shouldRoll = true

                        case .stop:
                            heading = clampHeading(self.robot.heading)
                            shouldStop = true

                        case .setLED:
                            // Ignored for now (Bolt has matrix LEDs)
                            break
                        }

                        // Write Pappe vars
                        val.cmdSpeed = speed
                        val.cmdHeading = heading
                        val.cmdDir = dir
                        val.cmdSeconds = seconds
                        val.doRollForSeconds = shouldRoll
                        val.doStop = shouldStop

                        // Consume command
                        self.pendingCommand = nil
                    }

                    //------------------------------------------------------
                    // 2) PAPPE execution (no Swift here)
                    //------------------------------------------------------

                    `if` { val.doRollForSeconds as Bool } then: {
                        run(Syncs.RollForSeconds, [
                            val.cmdSpeed,
                            val.cmdHeading,
                            val.cmdDir,
                            val.cmdSeconds
                        ])
                    }

                    `if` { val.doStop as Bool } then: {
                        run(Syncs.StopRoll, [
                            val.cmdHeading
                        ])
                    }

                    //------------------------------------------------------
                    // 3) Loop pacing
                    //------------------------------------------------------
                    run(Syncs.WaitMilliseconds, [10])

                } until: { false }
            }
        }

        //------------------------------------------------------
        // 3) Start
        //------------------------------------------------------
        controller?.start()
    }

    // MARK: - Disconnect

    func disconnect() {
        controller?.stop()
        controller = nil
    }

    // MARK: - Commands

    func send(_ command: RobotCommand) {
        pendingCommand = command
    }
}
