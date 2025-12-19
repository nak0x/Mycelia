//
//  ServersView.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

struct ServersView: View {
    @Environment(ServerStore.self) private var serverStore
    @Environment(WebSocketHub.self) private var wsHub

    @State private var draftName = "MyServer"
    @State private var draftWS = "ws://localhost:8000/ws"
    @State private var draftHTTP = "http://localhost:8000/health"

    var body: some View {
        NavigationStack {
            List {
                Section("Ajouter un serveur") {
                    TextField("Nom", text: $draftName)
                    TextField("WS URL (ws/wss)", text: $draftWS)
                        .platformNoAutocap()
                    TextField("HTTP Base URL (http/https)", text: $draftHTTP)
                        .platformNoAutocap()

                    Button("Ajouter") {
                        guard !draftName.isEmpty,
                              let ws = URL(string: draftWS),
                              let http = URL(string: draftHTTP) else { return }

                        let s = ServerEndpoint(name: draftName, wsURL: ws, httpBaseURL: http, isEnabled: true)
                        serverStore.add(s)
                        wsHub.connect(s)

                        draftName = ""; draftWS = ""; draftHTTP = ""
                    }
                }

                Section("Serveurs") {
                    ForEach(serverStore.servers) { s in
                        HStack {
                            VStack(alignment: .leading, spacing: 4) {
                                Text(s.name).font(.headline)
                                Text("WS: \(s.wsURL.absoluteString)").font(.caption).foregroundStyle(.secondary)
                                Text("HTTP: \(s.httpBaseURL.absoluteString)").font(.caption).foregroundStyle(.secondary)
                            }
                            Spacer()

                            Toggle("Actif", isOn: enabledBinding(for: s.id))
                                .labelsHidden()
                        }
                    }
                    .onDelete { idxSet in
                        for idx in idxSet {
                            let s = serverStore.servers[idx]
                            wsHub.disconnect(s.id)
                        }
                        serverStore.servers.remove(atOffsets: idxSet)
                    }
                }
            }
            .navigationTitle("Serveurs")
        }
    }

    private func enabledBinding(for id: UUID) -> Binding<Bool> {
        Binding(
            get: { serverStore.servers.first(where: { $0.id == id })?.isEnabled ?? false },
            set: { newValue in
                guard let idx = serverStore.servers.firstIndex(where: { $0.id == id }) else { return }
                serverStore.servers[idx].isEnabled = newValue

                let s = serverStore.servers[idx]
                if newValue { wsHub.connect(s) } else { wsHub.disconnect(s.id) }
            }
        )
    }
}
