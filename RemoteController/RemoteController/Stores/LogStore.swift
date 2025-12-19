//
//  LogKind.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import Foundation

enum LogKind: String, Codable {
    case wsIn, wsOut, httpIn, httpOut, error, info
}

struct LogEntry: Identifiable, Codable {
    var id: UUID = UUID()
    var date: Date = Date()
    var serverName: String?
    var kind: LogKind
    var title: String
    var body: String
}

@Observable
final class LogStore {
    private(set) var entries: [LogEntry] = []

    func add(_ entry: LogEntry) {
        entries.insert(entry, at: 0)
        if entries.count > 3000 { entries.removeLast(entries.count - 3000) }
    }

    func clear() { entries.removeAll() }
}
