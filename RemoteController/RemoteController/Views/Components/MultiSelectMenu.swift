//
//  MultiSelectMenu.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import SwiftUI

struct MultiSelectMenu<Item: Identifiable & Hashable>: View {
    let title: String
    let items: [Item]
    @Binding var selected: Set<Item>
    let label: (Item) -> String

    var body: some View {
        Menu {
            ForEach(items) { item in
                Button {
                    if selected.contains(item) { selected.remove(item) }
                    else { selected.insert(item) }
                } label: {
                    HStack {
                        Text(label(item))
                        Spacer()
                        if selected.contains(item) { Image(systemName: "checkmark") }
                    }
                }
            }

            if !selected.isEmpty {
                Divider()
                Button("Tout désélectionner") { selected.removeAll() }
            }
        } label: {
            HStack {
                Text(title)
                Spacer()
                Text(selected.isEmpty ? "Aucun" : "\(selected.count) sélectionné(s)")
                    .foregroundStyle(.secondary)
            }
        }
    }
}
