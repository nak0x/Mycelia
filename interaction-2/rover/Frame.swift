//
//  Frame.swift
//  IOTTools
//
//  Created by Jocelyn Marcilloux-Buisson on 15/12/2025.
//

import Foundation

// MARK: - Frame principale
/// Représente une frame WebSocket complète avec metadata et payload
struct Frame: Codable {
    let metadata: Metadata
    let payload: [Payload]
    
    /// Crée une frame pour envoyer au serveur/robot (Constructeur utilitaire)
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
    
    // NOTE: Pas besoin de init(from:) ou encode(to:) manuels ici.
    // Swift le fait automatiquement car Metadata et [Payload] sont Codable.
    
    /// Convertit la frame en JSON String (pour le debug ou l'envoi manuel)
    func toJSON() -> String? {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted // Optionnel, pour la lisibilité
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
/// Un élément de payload avec son type, sa valeur et son slug
struct Payload: Codable {
    let datatype: String
    let value: PayloadValue
    let slug: String
    
    enum CodingKeys: String, CodingKey {
        case datatype
        case value
        case slug
    }
    
    // Init membre à membre standard
    init(datatype: String, value: PayloadValue, slug: String) {
        self.datatype = datatype
        self.value = value
        self.slug = slug
    }
    
    // Init pour le décodage (C'est ici que la magie opère)
    init(from decoder: Swift.Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        // 1. On décode les champs simples
        slug = try container.decode(String.self, forKey: .slug)
        datatype = try container.decode(String.self, forKey: .datatype)
        
        // 2. On décode la valeur dynamiquement selon le datatype reçu
        // On normalise en minuscule pour être tolérant
        switch datatype.lowercased() {
        case "bool", "boolean":
            let boolVal = try container.decode(Bool.self, forKey: .value)
            value = .bool(boolVal)
            
        case "int", "integer":
            let intVal = try container.decode(Int.self, forKey: .value)
            value = .int(intVal)
            
        case "float", "double":
            let doubleVal = try container.decode(Double.self, forKey: .value)
            value = .float(doubleVal)
            
        case "string":
            let stringVal = try container.decode(String.self, forKey: .value)
            value = .string(stringVal)
            
        default:
            // Fallback : On tente de lire en String si le type est inconnu,
            // ou on lance une erreur si tu préfères être strict.
            if let stringVal = try? container.decode(String.self, forKey: .value) {
                value = .string(stringVal)
            } else {
                // Si on arrive vraiment pas à décoder, on met une chaîne vide ou on throw
                value = .string("")
                print("⚠️ Erreur décodage Payload: Type inconnu '\(datatype)' et impossible de lire en String.")
            }
        }
    }
    
    // Encode manuel nécessaire car PayloadValue est un enum complexe
    func encode(to encoder: Swift.Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(datatype, forKey: .datatype)
        try container.encode(slug, forKey: .slug)
        
        switch value {
        case .bool(let val):
            try container.encode(val, forKey: .value)
        case .int(let val):
            try container.encode(val, forKey: .value)
        case .float(let val):
            try container.encode(val, forKey: .value)
        case .string(let val):
            try container.encode(val, forKey: .value)
        }
    }
}

// MARK: - PayloadValue
/// Valeur typée du payload (Enum avec valeurs associées)
enum PayloadValue: Codable {
    case bool(Bool)
    case int(Int)
    case float(Double)
    case string(String)
    
    // Nécessaire pour satisfaire Codable sur un enum avec valeurs associées
    // (Swift ne le synthétise pas toujours automatiquement pour les enums complexes sans clés brutes)
    init(from decoder: Swift.Decoder) throws {
        let container = try decoder.singleValueContainer()
        if let x = try? container.decode(Bool.self) {
            self = .bool(x)
            return
        }
        if let x = try? container.decode(Int.self) {
            self = .int(x)
            return
        }
        if let x = try? container.decode(Double.self) {
            self = .float(x)
            return
        }
        if let x = try? container.decode(String.self) {
            self = .string(x)
            return
        }
        throw DecodingError.typeMismatch(PayloadValue.self, DecodingError.Context(codingPath: decoder.codingPath, debugDescription: "Type incompatible"))
    }
    
    func encode(to encoder: Swift.Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case .bool(let x): try container.encode(x)
        case .int(let x): try container.encode(x)
        case .float(let x): try container.encode(x)
        case .string(let x): try container.encode(x)
        }
    }
    
    /// Récupère la valeur sous forme de Any (utile pour les prints)
    var anyValue: Any {
        switch self {
        case .bool(let val): return val
        case .int(let val): return val
        case .float(let val): return val
        case .string(let val): return val
        }
    }
    
    // Helpers typés
    var intValue: Int? {
        if case .int(let val) = self { return val }
        return nil
    }
    
    var stringValue: String? {
        if case .string(let val) = self { return val }
        return nil
    }
}

// MARK: - Extensions Helpers pour la création rapide
extension Payload {
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
