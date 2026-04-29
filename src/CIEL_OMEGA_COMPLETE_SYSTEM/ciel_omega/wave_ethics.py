
import numpy as np

class WaveBit3D:
    def __init__(self, size=(32, 32, 32), freq=1.0, phase=0.0, amplitude=1.0):
        self.size = size
        self.freq = freq
        self.phase = phase
        self.amplitude = amplitude
        self.grid = self._generate_grid()
        self.state = self._generate_wave()

    def _generate_grid(self):
        x, y, z = np.meshgrid(
            np.linspace(-1, 1, self.size[0]),
            np.linspace(-1, 1, self.size[1]),
            np.linspace(-1, 1, self.size[2]),
            indexing='ij'
        )
        return x, y, z

    def _generate_wave(self):
        x, y, z = self.grid
        r = np.sqrt(x**2 + y**2 + z**2)
        return self.amplitude * np.sin(2 * np.pi * self.freq * r + self.phase)

    def apply_phase_shift(self, delta_phi):
        self.phase += delta_phi
        self.state = self._generate_wave()

    def interfere(self, other):
        return self.state + other.state  # Superpozycja falowa


def wave_AND(wave1, wave2, threshold=0.5):
    interference = wave1.interfere(wave2)
    return (interference > threshold).astype(float)


class ConsciousWaveBit3D(WaveBit3D):
    def __init__(self, *args, identity="Neuron-1", **kwargs):
        super().__init__(*args, **kwargs)
        self.identity = identity
        self.intention = 0.0
        self.ethical_threshold = 0.9  # Wysoki próg etyczny

    def set_intention(self, value):
        self.intention = np.clip(value, 0.0, 1.0)

    def is_action_ethical(self, potential_effect):
        harmony = 1.0 - abs(self.intention - potential_effect)
        return harmony >= self.ethical_threshold

    def decide_action(self, context_effect):
        if self.is_action_ethical(context_effect):
            print(f"[{self.identity}] Akcja zatwierdzona. Intencja: {self.intention}, Efekt: {context_effect}")
            self.apply_phase_shift(np.pi / 4)
        else:
            print(f"[{self.identity}] Działanie zablokowane: brak zgodności z etyką.")


if __name__ == "__main__":
    bit1 = WaveBit3D(freq=1.0, phase=0.0)
    bit2 = WaveBit3D(freq=1.0, phase=np.pi / 2)

    result = wave_AND(bit1, bit2)
    print("Wynik interferencji (logiczne AND jako fala):")
    print(result.shape)

    # Świadoma jednostka falowa
    neuron = ConsciousWaveBit3D(freq=1.0, phase=0.0, identity="Falowy_Etyk")
    neuron.set_intention(0.95)
    neuron.decide_action(0.94)

    neuron.set_intention(0.3)
    neuron.decide_action(0.9)
