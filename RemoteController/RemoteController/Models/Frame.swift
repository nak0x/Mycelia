//
//  Frame.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import Foundation

struct Frame: Codable, Hashable {
    var metadata: Metadata
    var payload: [Payload]

    struct Metadata: Codable, Hashable {
        var senderId: String
        var receiverId: String?
        var timestamp: Int64
        var messageId: String
        var type: String
        var status: String?
    }

    struct Payload: Codable, Hashable, Identifiable {
        var id: UUID = UUID()
        var datatype: String
        var value: String
        var slug: String

        enum CodingKeys: String, CodingKey {
            case datatype, value, slug
        }
    }

    func toJSONString(pretty: Bool = false) throws -> String {
        let enc = JSONEncoder()
        if pretty { enc.outputFormatting = [.prettyPrinted, .sortedKeys] }
        let data = try enc.encode(self)
        return String(decoding: data, as: UTF8.self)
    }
}
