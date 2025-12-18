//
//  SharedComponents.swift
//  IOTTools
//
//  Created by Antigravity on 18/12/2025.
//

import SwiftUI

// MARK: - Data Models

struct RobotSession: Identifiable, Equatable {
    let id = UUID()
    var targetDeviceId: String
    var robot: Robot?
    var controller: RobotWebSocketController?
    
    var isConnected: Bool {
        robot?.isConnected ?? false
    }
    
    static func == (lhs: RobotSession, rhs: RobotSession) -> Bool {
        lhs.id == rhs.id
    }
}

// MARK: - Design System

struct NeonTheme {
    static let bgMain = Color(hex: "0F1116")
    static let bgCard = Color(hex: "1A1D26")
    static let bgInput = Color(hex: "252942")
    
    static let accentPink = Color(hex: "FF0099")
    static let accentCyan = Color(hex: "00F0FF")
    static let accentYellow = Color(hex: "FFE600")
    static let accentPurple = Color(hex: "BD00FF")
    static let accentRed = Color(hex: "FF0000")
    
    static let textPrimary = Color.white
    static let textSecondary = Color.white.opacity(0.6)
}

// MARK: - Components

struct NeonCard<Content: View>: View {
    var content: Content
    var borderColor: Color
    
    init(borderColor: Color = NeonTheme.accentCyan.opacity(0.3), @ViewBuilder content: () -> Content) {
        self.borderColor = borderColor
        self.content = content()
    }
    
    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 20)
                .fill(NeonTheme.bgCard)
                .shadow(color: Color.black.opacity(0.4), radius: 10, x: 0, y: 5)
            
            RoundedRectangle(cornerRadius: 20)
                .stroke(
                    LinearGradient(
                        colors: [borderColor, borderColor.opacity(0.1)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ),
                    lineWidth: 1
                )
            
            content
                .padding(20)
        }
    }
}

struct GlowingButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    var isActive: Bool = false
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                Text(title)
                    .fontWeight(.bold)
            }
            .padding()
            .frame(maxWidth: .infinity)
            .background(
                ZStack {
                    if isActive {
                        color.opacity(0.2)
                            .blur(radius: 10)
                        
                        LinearGradient(colors: [color, color.opacity(0.8)], startPoint: .leading, endPoint: .trailing)
                    } else {
                        Color.white.opacity(0.05)
                    }
                }
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(isActive ? color : Color.white.opacity(0.1), lineWidth: 1)
            )
            .cornerRadius(12)
            .foregroundColor(isActive ? .white : NeonTheme.textSecondary)
            .shadow(color: isActive ? color.opacity(0.5) : .clear, radius: 8)
        }
    }
}

struct StatCircle: View {
    let value: String
    let label: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            ZStack {
                Circle()
                    .stroke(Color.white.opacity(0.1), lineWidth: 4)
                
                Circle()
                    .trim(from: 0, to: 0.7) // Mock value
                    .stroke(
                        AngularGradient(colors: [color.opacity(0.2), color], center: .center),
                        style: StrokeStyle(lineWidth: 4, lineCap: .round)
                    )
                    .rotationEffect(.degrees(-90))
                
                Text(value)
                    .font(.system(size: 16, weight: .bold, design: .monospaced))
                    .foregroundColor(.white)
            }
            .frame(width: 60, height: 60)
            
            Text(label)
                .font(.caption)
                .foregroundColor(NeonTheme.textSecondary)
        }
    }
}

struct CustomTextField: View {
    @Binding var text: String
    var placeholder: String
    var bg: Color
    var color: Color
    
    var body: some View {
        TextField("", text: $text)
            .padding()
            .background(bg)
            .cornerRadius(10)
            .foregroundColor(color)
            // .presentationCornerRadius(10) // Removed as it might be iOS 16.4+ specific and this is safer
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(Color.white.opacity(0.1), lineWidth: 1)
            )
            .shadow(color: Color.black.opacity(0.1), radius: 2)
            .overlay(
                HStack {
                    if text.isEmpty {
                        Text(placeholder)
                            .foregroundColor(color.opacity(0.4))
                            .padding(.leading, 16)
                            .allowsHitTesting(false)
                    }
                    Spacer()
                }
            )
    }
}

// Helpers

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
