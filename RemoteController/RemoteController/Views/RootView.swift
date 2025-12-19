//
//  RootView.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

struct RootView: View {
    var body: some View {
        TabView {
            ServersView()
                .tabItem { Label("Serveurs", systemImage: "server.rack") }

            FrameBuilderView()
                .tabItem { Label("Trame", systemImage: "paperplane") }

            HTTPComposerView()
                .tabItem { Label("HTTP", systemImage: "globe") }

            LogsView()
                .tabItem { Label("Logs", systemImage: "text.bubble") }
        }
    }
}
