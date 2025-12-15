//
//  RobotColor.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//


import Foundation

/// Generic color rgb.
/// It will be converted to `SyncsColor` on the Synchrosphere package.
struct RobotColor: Hashable {
    let r: UInt8
    let g: UInt8
    let b: UInt8

    init(r: UInt8, g: UInt8, b: UInt8) {
        self.r = r
        self.g = g
        self.b = b
    }

    static let off   = RobotColor(r: 0, g: 0, b: 0)
    static let red   = RobotColor(r: 255, g: 0, b: 0)
    static let green = RobotColor(r: 0, g: 255, b: 0)
    static let blue  = RobotColor(r: 0, g: 0, b: 255)
    static let white = RobotColor(r: 255, g: 255, b: 255)
}
