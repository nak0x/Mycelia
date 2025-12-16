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
    let payload: [Payload]
    
    init(senderId: String, receiverId: String, type: String = "ws-data", payloads: [Payload]) {
        let timestamp = Date().timeIntervalSince1970
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyyMMdd"
        let dateStr = dateFormatter.string(from: Date())
        
        self.metadata = Metadata(
            senderId: senderId,
            timestamp: timestamp,
            messageId: "MSG-\(dateStr)-\(Int.random(in: 1000...9999))",
            type: type,
            receiverId: receiverId,
            status: Status(connection: 200)
        )
        self.payload = payloads
    }
    
    func toJSON() -> String? {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
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
    let messageId: String
    let type: String
    let receiverId: String
    let status: Status
}

// MARK: - Status
struct Status: Codable {
    let connection: Int
}

// MARK: - Payload
struct Payload: Codable {
    let datatype: String
    let value: PayloadValue
    let slug: String
    
    enum CodingKeys: String, CodingKey {
        case datatype
        case value
        case slug
    }
    
    init(datatype: String, value: PayloadValue, slug: String) {
        self.datatype = datatype
        self.value = value
        self.slug = slug
    }
    
    init(from decoder: Swift.Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        slug = try container.decode(String.self, forKey: .slug)
        datatype = try container.decode(String.self, forKey: .datatype)
        
        switch datatype.lowercased() {
        case "bool", "boolean":
            let val = try container.decode(Bool.self, forKey: .value)
            value = .bool(val)
            
        case "int", "integer":
            let val = try container.decode(Int.self, forKey: .value)
            value = .int(val)
            
        case "float", "double":
            let val = try container.decode(Double.self, forKey: .value)
            value = .float(val)
            
        case "string":
            let val = try container.decode(String.self, forKey: .value)
            value = .string(val)
            
        // NOUVEAU : Gestion des tableaux d'entiers
        case "iarray", "intarray":
            // Essaye de décoder [Int] directement
            if let ints = try? container.decode([Int].self, forKey: .value) {
                value = .intArray(ints)
            }
            // Sinon, essaye de décoder [String] et convertit en [Int] (ex: ["100", "10"])
            else if let strs = try? container.decode([String].self, forKey: .value) {
                let ints = strs.compactMap { Int($0) }
                value = .intArray(ints)
            } else {
                // Fallback vide si échec
                value = .intArray([])
                print("⚠️ Erreur décodage iarray pour \(slug)")
            }
            
        default:
            if let stringVal = try? container.decode(String.self, forKey: .value) {
                value = .string(stringVal)
            } else {
                value = .string("")
            }
        }
    }
    
    func encode(to encoder: Swift.Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(datatype, forKey: .datatype)
        try container.encode(slug, forKey: .slug)
        
        switch value {
        case .bool(let val):   try container.encode(val, forKey: .value)
        case .int(let val):    try container.encode(val, forKey: .value)
        case .float(let val):  try container.encode(val, forKey: .value)
        case .string(let val): try container.encode(val, forKey: .value)
        case .intArray(let val): try container.encode(val, forKey: .value)
        }
    }
}

// MARK: - PayloadValue
enum PayloadValue: Codable {
    case bool(Bool)
    case int(Int)
    case float(Double)
    case string(String)
    case intArray([Int]) // NOUVEAU CAS
    
    init(from decoder: Swift.Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if let x = try? container.decode(Bool.self) { self = .bool(x); return }
        if let x = try? container.decode(Int.self) { self = .int(x); return }
        if let x = try? container.decode(Double.self) { self = .float(x); return }
        if let x = try? container.decode(String.self) { self = .string(x); return }
        
        // Pour les tableaux, on doit utiliser un conteneur non-keyed si singleValue échoue
        if let x = try? container.decode([Int].self) { self = .intArray(x); return }
        
        throw DecodingError.typeMismatch(PayloadValue.self, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Type incompatible"))
    }
    
    func encode(to encoder: Swift.Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .bool(let x):   try container.encode(x)
        case .int(let x):    try container.encode(x)
        case .float(let x):  try container.encode(x)
        case .string(let x): try container.encode(x)
        case .intArray(let x): try container.encode(x)
        }
    }
    
    var anyValue: Any {
        switch self {
        case .bool(let val): return val
        case .int(let val): return val
        case .float(let val): return val
        case .string(let val): return val
        case .intArray(let val): return val
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
    
    // Helper pour récupérer le tableau
    var intArrayValue: [Int]? {
        if case .intArray(let val) = self { return val }
        return nil
    }
}

// MARK: - Extensions Helpers pour Payload
extension Payload {
    
    var intValue: Int? {
        return value.intValue
    }
    
    var stringValue: String? {
        return value.stringValue
    }
    
    var intArrayValue: [Int]? {
        return value.intArrayValue
    }
    
    static func bool(_ value: Bool, slug: String) -> Payload {
        return Payload(datatype: "bool", value: .bool(value), slug: slug)
    }
    
    static func int(_ value: Int, slug: String) -> Payload {
        return Payload(datatype: "int", value: .int(value), slug: slug)
    }
    
    static func float(_ value: Double, slug: String) -> Payload {
        return Payload(datatype: "float", value: .float(value), slug: slug)
    }
    
    static func string(_ value: String, slug: String) -> Payload {
        return Payload(datatype: "string", value: .string(value), slug: slug)
    }
}
