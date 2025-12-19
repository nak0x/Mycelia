//
//  WebSocketHub.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import Foundation

@Observable
final class WebSocketHub {
    private weak var serverStore: ServerStore?
    private weak var logStore: LogStore?

    private let session: URLSession = .shared
    private var tasks: [UUID: URLSessionWebSocketTask] = [:]
    private var listeners: [UUID: Task<Void, Never>] = [:]

    func bind(serverStore: ServerStore, logStore: LogStore) {
        self.serverStore = serverStore
        self.logStore = logStore
    }

    func connectAll() {
        guard let serverStore else { return }
        for s in serverStore.enabledServers() { connect(s) }
    }

    func connect(_ server: ServerEndpoint) {
        disconnect(server.id)

        let task = session.webSocketTask(with: server.wsURL)
        tasks[server.id] = task
        task.resume()

        logStore?.add(.init(serverName: server.name, kind: .info, title: "WS connect", body: server.wsURL.absoluteString))

        listeners[server.id] = Task { [weak self] in
            await self?.listenLoop(server: server)
        }
    }

    func disconnect(_ serverId: UUID) {
        listeners[serverId]?.cancel()
        listeners[serverId] = nil

        tasks[serverId]?.cancel(with: .goingAway, reason: nil)
        tasks[serverId] = nil
    }

    func send(frame: Frame, to servers: [ServerEndpoint]) async {
        for s in servers { await send(frame: frame, to: s) }
    }

    func send(frame: Frame, to server: ServerEndpoint) async {
        guard let task = tasks[server.id] else {
            logStore?.add(.init(serverName: server.name, kind: .error, title: "WS send failed", body: "Not connected"))
            return
        }
        do {
            let text = try frame.toJSONString(pretty: false)
            try await task.send(.string(text))
            logStore?.add(.init(serverName: server.name, kind: .wsOut, title: "WS → Frame", body: text))
        } catch {
            logStore?.add(.init(serverName: server.name, kind: .error, title: "WS send error", body: "\(error)"))
        }
    }

    private func listenLoop(server: ServerEndpoint) async {
        guard let task = tasks[server.id] else { return }

        while !Task.isCancelled {
            do {
                let msg = try await task.receive()
                switch msg {
                case .string(let text):
                    logStore?.add(.init(serverName: server.name, kind: .wsIn, title: "WS ←", body: text))
                case .data(let data):
                    logStore?.add(.init(serverName: server.name, kind: .wsIn, title: "WS ← (data)", body: data.base64EncodedString()))
                @unknown default:
                    logStore?.add(.init(serverName: server.name, kind: .wsIn, title: "WS ← (unknown)", body: ""))
                }
            } catch {
                logStore?.add(.init(serverName: server.name, kind: .error, title: "WS receive error", body: "\(error)"))
                // Reconnexion simple
                await reconnect(server)
                return
            }
        }
    }

    private func reconnect(_ server: ServerEndpoint) async {
        for delay in [1, 2, 5, 10, 20] {
            try? await Task.sleep(nanoseconds: UInt64(delay) * 1_000_000_000)
            if Task.isCancelled { return }
            connect(server)
            return
        }
    }
}
