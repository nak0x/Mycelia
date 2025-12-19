//
//  HTTPComposerView.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

struct HTTPComposerView: View {
    @Environment(ServerStore.self) private var serverStore
    @Environment(LogStore.self) private var logStore
    @Environment(HTTPClient.self) private var http

    @State private var selectedServers: Set<ServerEndpoint> = []
    @State private var path = "/api/ping"
    @State private var method = "POST"
    @State private var includeBody = true
    @State private var jsonBody = "{\n  \"hello\": \"world\"\n}"

    private let methods = ["GET","POST","PUT","PATCH","DELETE"]

    var body: some View {
        NavigationStack {
            Form {
                Section("Cibles") {
                    MultiSelectMenu(
                        title: "Serveurs",
                        items: serverStore.enabledServers(),
                        selected: $selectedServers,
                        label: { $0.name }
                    )
                }

                Section("Requête") {
                    Picker("Méthode", selection: $method) {
                        ForEach(methods, id: \.self) { Text($0) }
                    }
                    .pickerStyle(.menu)

                    TextField("Path (ex: /api/ping)", text: $path)
                        .platformNoAutocap()

                    Toggle("Body JSON", isOn: $includeBody)

                    if includeBody && method != "GET" && method != "DELETE" {
                        TextEditor(text: $jsonBody)
                            .frame(minHeight: 130)
                            .font(.system(.body, design: .monospaced))
                    }
                }

                Section {
                    Button("Envoyer (HTTP)") {
                        Task { await sendAll() }
                    }
                    .disabled(selectedServers.isEmpty)
                }
            }
            .navigationTitle("HTTP")
        }
    }

    private func sendAll() async {
        for s in selectedServers {
            logStore.add(.init(serverName: s.name, kind: .httpOut, title: "HTTP → \(method) \(path)", body: includeBody ? jsonBody : ""))

            do {
                let resp = try await http.request(
                    baseURL: s.httpBaseURL,
                    path: path,
                    method: method,
                    jsonBody: (includeBody && method != "GET" && method != "DELETE") ? jsonBody : nil
                )
                logStore.add(.init(serverName: s.name, kind: .httpIn, title: "HTTP ← \(resp.statusCode)", body: resp.body))
            } catch {
                logStore.add(.init(serverName: s.name, kind: .error, title: "HTTP error", body: "\(error)"))
            }
        }
    }
}
