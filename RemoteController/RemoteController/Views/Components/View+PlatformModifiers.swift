//
//  View+PlatformModifiers.swift
//  RemoteController
//
//  Created by Emmanuel Moulin on 18/12/2025.
//

import SwiftUI

extension View {
    @ViewBuilder
    func platformNoAutocap() -> some View {
        #if os(iOS)
        self.textInputAutocapitalization(.never)
            .autocorrectionDisabled(true)
        #else
        self
        #endif
    }
}
