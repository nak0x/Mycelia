//
//  FrameBuilderView.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

struct FrameBuilderView: View {
    @Environment(ServerStore.self) private var serverStore
    @Environment(WebSocketHub.self) private var wsHub
    @Environment(LogStore.self) private var logStore

    @State private var selectedServers: Set<ServerEndpoint> = []

    @State private var senderId = "device-a"
    @State private var receiverId = ""
    @State private var type = "event"
    @State private var status = ""
    @State private var messageId = UUID().uuidString

    @State private var payloads: [Frame.Payload] = [
        .init(datatype: "string", value: "hello", slug: "greeting")
    ]

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

                Section("Metadata") {
                    TextField("senderId", text: $senderId)
                    TextField("receiverId (optionnel)", text: $receiverId)
                    TextField("type", text: $type)
                    TextField("status (optionnel)", text: $status)

                    HStack {
                        TextField("messageId", text: $messageId)
                        Button { messageId = UUID().uuidString } label: {
                            Image(systemName: "arrow.clockwise")
                        }
                        .buttonStyle(.borderless)
                    }
                }

                Section("Payload") {
                    ForEach($payloads) { $p in
                        VStack(alignment: .leading, spacing: 8) {
                            TextField("slug", text: $p.slug)
                            TextField("datatype", text: $p.datatype)
                            TextField("value", text: $p.value)
                        }
                    }
                    .onDelete { payloads.remove(atOffsets: $0) }

                    Button("Ajouter un payload") {
                        payloads.append(.init(datatype: "string", value: "", slug: ""))
                    }
                }

                Section {
                    Button("Envoyer (WebSocket)") {
                        Task {
                            let frame = buildFrame()
                            await wsHub.send(frame: frame, to: Array(selectedServers))
                        }
                    }
                    .disabled(selectedServers.isEmpty)

                    Button("Aperçu JSON (dans logs)") {
                        do {
                            let json = try buildFrame().toJSONString(pretty: true)
                            logStore.add(.init(serverName: nil, kind: .info, title: "Frame preview", body: json))
                        } catch {
                            logStore.add(.init(serverName: nil, kind: .error, title: "Frame preview error", body: "\(error)"))
                        }
                    }
                }
            }
            .navigationTitle("Trame")
        }
    }

    private func buildFrame() -> Frame {
        let nowMs = Int64(Date().timeIntervalSince1970 * 1000.0)
        return Frame(
            metadata: .init(
                senderId: senderId,
                receiverId: receiverId.isEmpty ? nil : receiverId,
                timestamp: nowMs,
                messageId: messageId,
                type: type,
                status: status.isEmpty ? nil : status
            ),
            payload: payloads.map { .init(datatype: $0.datatype, value: $0.value, slug: $0.slug) }
        )
    }
}
