import SwiftUI

struct RobotView: View {

    // MARK: - UI State
    @State private var useRover: Bool = true
    @State private var bluetoothName: String = "RV-B456"
    @State private var robot: Robot? = nil

    @State private var sensorText: String = ""
    @State private var batteryText: String = ""

    @State private var selectedColor: RobotColor = .off

    var body: some View {
        VStack(spacing: 20) {

            // ----------------------------
            // Choix du type de robot
            // ----------------------------
            Toggle(isOn: $useRover) {
                Text(useRover ? "Mode Rover (RVR)" : "Mode Sphero Mini")
                    .font(.headline)
            }
            .padding()

            // Nom Bluetooth
            TextField("Nom Bluetooth", text: $bluetoothName)
                .padding()
                .textFieldStyle(.roundedBorder)

            // ----------------------------
            // Bouton connect / disconnect
            // ----------------------------
            Button(action: {
                if let rob = robot, rob.isConnected {
                    rob.disconnect()
                    robot = nil
                } else {
                    createAndConnectRobot()
                }
            }) {
                Text(robot?.isConnected == true ? "Déconnexion" : "Connexion")
                    .font(.title3)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(robot?.isConnected == true ? Color.red : Color.green)
                    .foregroundColor(.white)
                    .cornerRadius(12)
            }
            .padding(.horizontal)

            // ----------------------------
            // Commandes si connecté
            // ----------------------------
            if let rob = robot, rob.isConnected {

                Text("Heading actuel : \(rob.heading)°")

                HStack(spacing: 20) {
                    Button("Gauche") { rob.turn(degrees: -15) }
                    Button("Avant")  { rob.forward(speed: 100) }
                    Button("Droite") { rob.turn(degrees: 15) }
                }
                .buttonStyle(.borderedProminent)

                HStack(spacing: 20) {
                    Button("Reculer") { rob.backward(speed: 80) }
                    Button("Stop")    { rob.stop() }
                }
                .buttonStyle(.bordered)

                // LED
                VStack {
                    Text("LED Couleur :")
                    Picker("LED", selection: $selectedColor) {
                        Text("Off").tag(RobotColor.off)
                        Text("Rouge").tag(RobotColor.red)
                        Text("Vert").tag(RobotColor.green)
                        Text("Bleu").tag(RobotColor.blue)
                        Text("Blanc").tag(RobotColor.white)
                    }
                    .pickerStyle(.segmented)
                    .padding()

                    Button("Appliquer LED") {
                        rob.setMainLED(color: selectedColor)
                    }
                    .buttonStyle(.borderedProminent)
                }

                // ----------------------------
                // Données capteurs en temps réel
                // ----------------------------
                VStack(spacing: 8) {
                    Text("🛰 Capteurs")
                        .font(.headline)
                    Text(sensorText)
                        .font(.system(size: 14))
                        .multilineTextAlignment(.center)
                }

                // Batterie
                VStack {
                    Text("🔋 Batterie")
                        .font(.headline)
                    Text(batteryText)
                        .font(.system(size: 14))
                }
            }

            Spacer()
        }
        .padding()
    }

    // MARK: - Création + Connexion du robot

    private func createAndConnectRobot() {
        // Crée le bon robot selon le toggle
        let rob: Robot = useRover
            ? Rover(bluetoothName: bluetoothName)
            : Sphero(bluetoothName: bluetoothName)

        rob.onSensorUpdate = { sample in
            DispatchQueue.main.async {
                self.sensorText =
                """
                x: \(sample.x)
                y: \(sample.y)
                yaw: \(sample.yaw)
                vx: \(sample.vx)
                vy: \(sample.vy)
                """
            }
        }

        rob.onBatteryUpdate = { state in
            DispatchQueue.main.async {
                switch state {
                case .ok:       batteryText = "OK 👍"
                case .low:      batteryText = "Faible ⚠️"
                case .critical: batteryText = "Critique ❗"
                case .unknown:  batteryText = "Inconnu"
                }
            }
        }

        // Sauvegarde + connexion
        self.robot = rob
        rob.connect()
    }
}

#Preview {
    RobotView()
}
