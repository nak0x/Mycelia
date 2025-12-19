//
//  LogsView.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

struct LogsView: View {
    @Environment(LogStore.self) private var logStore

    @State private var filter: LogKind? = nil
    @State private var searchText = ""

    var body: some View {
        NavigationStack {
            List(filtered) { e in
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(e.title).font(.headline)
                        Spacer()
                        Text(e.kind.rawValue).font(.caption).foregroundStyle(.secondary)
                    }
                    if let s = e.serverName {
                        Text(s).font(.caption).foregroundStyle(.secondary)
                    }
                    Text(e.body)
                        .font(.system(.caption, design: .monospaced))
                        .textSelection(.enabled)
                        .lineLimit(8)
                }
                .padding(.vertical, 4)
            }
            .searchable(text: $searchText)
            .toolbar {
                #if os(iOS)
                ToolbarItem(placement: .topBarLeading) {
                    filterMenu
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Vider") { logStore.clear() }
                }
                #else
                ToolbarItem(placement: .automatic) {
                    filterMenu
                }
                ToolbarItem(placement: .automatic) {
                    Button("Vider") { logStore.clear() }
                }
                #endif
            }
            .navigationTitle("Logs")
        }
    }

    private var filtered: [LogEntry] {
        logStore.entries.filter { e in
            let okKind = filter == nil || e.kind == filter
            let okSearch = searchText.isEmpty
                || e.title.localizedCaseInsensitiveContains(searchText)
                || e.body.localizedCaseInsensitiveContains(searchText)
                || (e.serverName?.localizedCaseInsensitiveContains(searchText) ?? false)
            return okKind && okSearch
        }
    }
    
    private var filterMenu: some View {
        Menu {
            Button("Tout") { filter = nil }
            Divider()
            ForEach([LogKind.wsIn, .wsOut, .httpIn, .httpOut, .error, .info], id: \.rawValue) { k in
                Button(k.rawValue) { filter = k }
            }
        } label: {
            Label("Filtre", systemImage: "line.3.horizontal.decrease.circle")
        }
    }
}
