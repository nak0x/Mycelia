//
//  HTTPResponse.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//


import Foundation

struct HTTPResponse {
    let statusCode: Int
    let body: String
}

@Observable
final class HTTPClient {
    private let session: URLSession = .shared

    func request(
        baseURL: URL,
        path: String,
        method: String,
        jsonBody: String?
    ) async throws -> HTTPResponse {
        var url = baseURL
        let p = path.hasPrefix("/") ? String(path.dropFirst()) : path
        url.appendPathComponent(p)

        var req = URLRequest(url: url)
        req.httpMethod = method.uppercased()
        req.setValue("application/json", forHTTPHeaderField: "Accept")

        if let jsonBody, !jsonBody.isEmpty, method.uppercased() != "GET" {
            req.setValue("application/json", forHTTPHeaderField: "Content-Type")
            req.httpBody = jsonBody.data(using: .utf8)
        }

        let (data, resp) = try await session.data(for: req)
        let http = resp as? HTTPURLResponse

        return HTTPResponse(
            statusCode: http?.statusCode ?? -1,
            body: String(decoding: data, as: UTF8.self)
        )
    }
}
