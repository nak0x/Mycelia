//
//  AppRoot.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

@main
struct AppRoot: App {
    @State private var serverStore = ServerStore()
    @State private var logStore = LogStore()
    @State private var wsHub = WebSocketHub()
    @State private var http = HTTPClient()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(serverStore)
                .environment(logStore)
                .environment(wsHub)
                .environment(http)
                .task {
                    wsHub.bind(serverStore: serverStore, logStore: logStore)
                    wsHub.connectAll()
                }
        }
    }
}
