//
//  ContentView.swift
//  IOTTools
//
//  Created by Emmanuel Moulin on 29/11/2025.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            Tab("Robot", systemImage: "robotic.vacuum") {
                RobotView()
            }
            
            Tab ("Websocket", systemImage: "wifi") {
                WebsocketView()
            }
        }
    }
}

#Preview {
    ContentView()
}
