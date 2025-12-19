//
//  ServerEndpoint.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import Foundation

struct ServerEndpoint: Identifiable, Codable, Hashable {
    var id: UUID = UUID()
    var name: String
    var wsURL: URL
    var httpBaseURL: URL
    var isEnabled: Bool = true
}
