//
//  WebSocketManager.swift
//  IOTTools
//
//  Created by Jocelyn Marcilloux-Buisson on 15/12/2025.
//


import Foundation

/// Gestionnaire très simple de connexion WebSocket pour iOS
///
/// - Se connecte à une URL WebSocket
/// - Permet d'envoyer des messages texte (JSON) au serveur
/// - Garde quelques logs en mémoire pour le debug
class WebSocketManager {
    
    // MARK: - Properties
    
    /// URL du serveur WebSocket
    private(set) var serverURL: String
    
    /// Device ID de cette app (sera le senderId des frames envoyées)
    private(set) var deviceId: String
    
    /// État de la connexion
    private(set) var isConnected: Bool = false
    
    /// Dernière erreur rencontrée
    private(set) var lastError: String?
    
    /// Messages de log pour debug
    private(set) var logs: [String] = []
    
    /// WebSocket task
    private var webSocketTask: URLSessionWebSocketTask?
    
    /// Session URL pour le WebSocket
    private var urlSession: URLSession?
    
    /// Callback appelé quand la connexion change d'état
    var onConnectionChanged: ((Bool) -> Void)?
    
    // MARK: - Init
    
    init(serverURL: String, deviceId: String) {
        self.serverURL = serverURL
        self.deviceId = deviceId
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 30
        self.urlSession = URLSession(configuration: config)
    }
    
    // MARK: - Connection
    
    /// Se connecte au serveur WebSocket
    func connect() {
        guard let url = URL(string: serverURL) else {
            addLog("❌ URL invalide: \(serverURL)")
            lastError = "URL invalide"
            return
        }
        
        addLog("🔄 Connexion à \(serverURL)...")
        
        webSocketTask = urlSession?.webSocketTask(with: url)
        webSocketTask?.resume()
        
        isConnected = true
        lastError = nil
        onConnectionChanged?(true)
        addLog("✅ Connecté au serveur WebSocket")
        
        // Commence éventuellement à écouter les messages (pur log côté client)
        receiveMessage()
    }
    
    /// Se déconnecte du serveur WebSocket
    func disconnect() {
        guard isConnected else { return }
        
        addLog("🔌 Déconnexion...")
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        webSocketTask = nil
        
        isConnected = false
        onConnectionChanged?(false)
        addLog("❌ Déconnecté du serveur")
    }
    
    // MARK: - Receive Messages
    
    /// Écoute les messages entrants (récursif) — purement pour logs
    private func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            guard let self = self else { return }
            
            switch result {
            case .success(let message):
                self.handleMessage(message)
                // Continue à écouter
                self.receiveMessage()
                
            case .failure(let error):
                self.addLog("❌ Erreur de réception: \(error.localizedDescription)")
                self.lastError = error.localizedDescription
                self.isConnected = false
                self.onConnectionChanged?(false)
            }
        }
    }
    
    /// Traite un message WebSocket reçu et l'ajoute aux logs
    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .string(let text):
            addLog("📥 Message reçu: \(text)")
            
        case .data(let data):
            if let text = String(data: data, encoding: .utf8) {
                addLog("📥 Message reçu (data): \(text)")
            } else {
                addLog("⚠️ Impossible de décoder les données")
            }
            
        @unknown default:
            addLog("⚠️ Type de message inconnu")
        }
    }
    
    // MARK: - Envoi de messages
    
    /// Envoie un texte brut (généralement une chaîne JSON) au serveur
    func send(text: String) {
        guard isConnected else {
            addLog("⚠️ Pas connecté, impossible d'envoyer")
            return
        }
        
        let message = URLSessionWebSocketTask.Message.string(text)
        webSocketTask?.send(message) { [weak self] error in
            if let error = error {
                self?.addLog("❌ Erreur d'envoi: \(error.localizedDescription)")
            } else {
                self?.addLog("📤 Message envoyé")
            }
        }
    }
    
    // MARK: - Logs
    
    /// Ajoute un message au log (max 50 messages)
    private func addLog(_ message: String) {
        let timestamp = Date().formatted(date: .omitted, time: .standard)
        let logMessage = "[\(timestamp)] \(message)"
        
        DispatchQueue.main.async {
            self.logs.append(logMessage)
            if self.logs.count > 50 {
                self.logs.removeFirst()
            }
        }
        
        print(logMessage)
    }
    
    /// Efface tous les logs
    func clearLogs() {
        logs.removeAll()
    }
}

