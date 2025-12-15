//
//  RobotRunner.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//

import Foundation
import Pappe

/// The low-level runner responsible for sending Pappe commands
/// and dispatching Synchrosphere events to `Robot`.
///
/// - No ObservableObject.
/// - No Swift control statements inside Pappe blocks.
/// - All logic safely bridged inside exec {}.
///
class RoverRunner {

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
        // 1) Configure SyncsControllerConfig (callbacks)
        //------------------------------------------------------
        var cfg = SyncsControllerConfig(deviceSelector: .anyRVR)

        cfg.stateDidChangeCallback = { [weak self] state in
            guard let self = self else { return }

            // When robot is awake, everything is ready
            if state.contains(.isAwake) && !self.robot.isConnected {
                DispatchQueue.main.async {
                    self.robot._didConnect()
                }
            }

            // When connection drops
            if !state.contains(.isConnected) && self.robot.isConnected {
                DispatchQueue.main.async {
                    self.robot._didDisconnect()
                }
            }

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
        // 2) Build the Pappe controller
        //------------------------------------------------------
        controller = engine.makeController(for: cfg) { names, ctx in
            
            activity(names.Main, [
                "cmdSpeed",
                "cmdHeading",
                "cmdDir",
                "cmdLED",
                "doRoll",
                "doStop",
                "doLED",
                "cmdDuration"
            ]) { val in

                //------------------------------------------------------
                // Initialize Pappe variables once
                //------------------------------------------------------
                exec {
                    val.cmdSpeed = SyncsSpeed(0)
                    val.cmdHeading = SyncsHeading(0)
                    val.cmdDir = SyncsDir.forward
                    val.cmdLED = SyncsColor.black

                    val.doRoll = false
                    val.doStop = false
                    val.doLED = false
                    val.cmdDuration = 1
                }

                //------------------------------------------------------
                // Main synchronous infinite loop
                //------------------------------------------------------
                `repeat` {

                    //------------------------------------------------------
                    // 1) SWIFT → PAPPE BINDING (ALLOWED HERE)
                    //------------------------------------------------------
                    exec {

                        // Reset Pappe flags
                        val.doRoll = false
                        val.doStop = false
                        val.doLED = false

                        guard let cmd = self.pendingCommand else { return }

                        switch cmd {

                        case .forward(let speed, let durationS):
                            val.cmdSpeed = SyncsSpeed(UInt16(speed))
                            val.cmdHeading = SyncsHeading(UInt16(self.robot.heading))
                            val.cmdDir = SyncsDir.forward
                            val.doRoll = true
                            val.cmdDuration = durationS

                        case .backward(let speed, let durationS):
                            val.cmdSpeed = SyncsSpeed(UInt16(speed))
                            val.cmdHeading = SyncsHeading(UInt16(self.robot.heading))
                            val.cmdDir = SyncsDir.backward
                            val.doRoll = true
                            val.cmdDuration = durationS

                        case .turn(let heading, let durationS):
                            val.cmdSpeed = SyncsSpeed(0)
                            val.cmdHeading = SyncsHeading(UInt16(heading))
                            val.cmdDir = SyncsDir.forward
                            val.doRoll = true
                            val.cmdDuration = durationS

                        case .stop:
                            val.cmdHeading = SyncsHeading(UInt16(self.robot.heading))
                            val.doStop = true

                        case .setLED(let color):
                            val.cmdLED = SyncsColor(
                                red: color.r,
                                green: color.g,
                                blue: color.b
                            )
                            val.doLED = true
                        }

                        // Consume command
                        self.pendingCommand = nil
                    }

                    //------------------------------------------------------
                    // 2) PAPPE LOGIC (NO SWIFT HERE!)
                    //------------------------------------------------------

                    // Move robot
                    `if` { val.doRoll as Bool } then: {
                        run(Syncs.RollForSeconds, [
                            val.cmdSpeed,
                            val.cmdHeading,
                            val.cmdDir,
                            val.cmdDuration
                        ])
                    }
                    
                    // Stop robot
                    `if` { val.doStop as Bool } then: {
                        run(Syncs.StopRoll, [
                            val.cmdHeading
                        ])
                    }

                    // LED update
                    `if` { val.doLED as Bool } then: {
                        run(Syncs.SetMainLED, [
                            val.cmdLED
                        ])
                    }

                    //------------------------------------------------------
                    // 4) Small pause between iterations
                    //------------------------------------------------------
                    run(Syncs.WaitMilliseconds, [10])

                } until: { false }
            }
        }

        //------------------------------------------------------
        // 3) Start the controller
        //------------------------------------------------------
        controller?.start()
    }

    // MARK: - Disconnect

    func disconnect() {
        controller?.stop()
        controller = nil
    }

    // MARK: - Public command API

    func send(_ command: RobotCommand) {
        pendingCommand = command
    }
}
