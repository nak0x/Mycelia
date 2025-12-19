//
//  ServerStore.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import Foundation

@Observable
final class ServerStore {
    var servers: [ServerEndpoint] = [] {
        didSet { persist() }
    }

    private let storageKey = "servers_v2"

    init() {
        load()
        if servers.isEmpty {
            servers = [
                ServerEndpoint(
                    name: "Local",
                    wsURL: URL(string: "ws://localhost:8000/ws")!,
                    httpBaseURL: URL(string: "http://localhost:8000")!,
                    isEnabled: true
                )
            ]
        }
    }

    func enabledServers() -> [ServerEndpoint] { servers.filter { $0.isEnabled } }

    func add(_ s: ServerEndpoint) { servers.append(s) }
    func remove(id: UUID) { servers.removeAll { $0.id == id } }

    func update(_ s: ServerEndpoint) {
        guard let idx = servers.firstIndex(where: { $0.id == s.id }) else { return }
        servers[idx] = s
    }

    private func persist() {
        do {
            let data = try JSONEncoder().encode(servers)
            UserDefaults.standard.set(data, forKey: storageKey)
        } catch { }
    }

    private func load() {
        guard let data = UserDefaults.standard.data(forKey: storageKey) else { return }
        do { servers = try JSONDecoder().decode([ServerEndpoint].self, from: data) }
        catch { servers = [] }
    }
}
