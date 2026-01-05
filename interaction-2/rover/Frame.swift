//
//  Frame.swift
//  IOTTools
//
//  Created by Jocelyn Marcilloux-Buisson on 15/12/2025.
//

import Foundation

// MARK: - Frame principale
struct Frame: Codable {
    let metadata: Metadata
    let action: String
    let value: FrameValue
    
    init(senderId: String, action: String, value: FrameValue) {
        let timestamp = Date().timeIntervalSince1970
        
        self.metadata = Metadata(
            senderId: senderId,
            timestamp: timestamp
        )
        self.action = action
        self.value = value
    }
    
    func toJSON() -> String? {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .withoutEscapingSlashes]
        guard let data = try? encoder.encode(self),
              let jsonString = String(data: data, encoding: .utf8) else {
            return nil
        }
        return jsonString
    }
}

// MARK: - Metadata
struct Metadata: Codable {
    let senderId: String
    let timestamp: TimeInterval
    
    init(senderId: String, timestamp: TimeInterval) {
        self.senderId = senderId
        self.timestamp = timestamp
    }
}

// MARK: - FrameValue
enum FrameValue: Codable {
    case bool(Bool)
    case int(Int)
    case float(Double)
    case string(String)
    case intArray([Int])
    case dictionary([String: FrameValue]) // Support pour les objets complexes
    case null
    
    init(from decoder: Swift.Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if container.decodeNil() { self = .null; return }
        if let x = try? container.decode(Bool.self) { self = .bool(x); return }
        if let x = try? container.decode(Int.self) { self = .int(x); return }
        if let x = try? container.decode(Double.self) { self = .float(x); return }
        if let x = try? container.decode(String.self) { self = .string(x); return }
        if let x = try? container.decode([Int].self) { self = .intArray(x); return }
        if let x = try? container.decode([String: FrameValue].self) { self = .dictionary(x); return }
        
        throw DecodingError.typeMismatch(FrameValue.self, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Type incompatible"))
    }
    
    func encode(to encoder: Swift.Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .bool(let x):   try container.encode(x)
        case .int(let x):    try container.encode(x)
        case .float(let x):  try container.encode(x)
        case .string(let x): try container.encode(x)
        case .intArray(let x): try container.encode(x)
        case .dictionary(let x): try container.encode(x)
        case .null: try container.encodeNil()
        }
    }
    
    var anyValue: Any {
        switch self {
        case .bool(let val): return val
        case .int(let val): return val
        case .float(let val): return val
        case .string(let val): return val
        case .intArray(let val): return val
        case .dictionary(let val): return val
        case .null: return "null"
        }
    }
    
    var intValue: Int? {
        if case .int(let val) = self { return val }
        return nil
    }
    
    var stringValue: String? {
        if case .string(let val) = self { return val }
        return nil
    }
    
    var intArrayValue: [Int]? {
        if case .intArray(let val) = self { return val }
        return nil
    }
    
    var dictionaryValue: [String: FrameValue]? {
        if case .dictionary(let val) = self { return val }
        return nil
    }
}
