from .dto import IAudioOutput, AudioSample

class FakeOutput(IAudioOutput):
    def __init__(self, play_for_iteration_count: int = 1):
        self.current_sample : AudioSample | None = None
        self.played_for_iterations = 0
        self.play_for_iteration_count = play_for_iteration_count

    def start_playing(self, sample: AudioSample):
        self.current_sample = sample
        self.played_for_iterations = 0

    def what_is_playing(self) -> AudioSample|None:
        if self.current_sample is None:
            return None
        if self.played_for_iterations>=self.play_for_iteration_count-1:
            self.played_for_iterations = -1
            self.current_sample = None
            return None
        self.played_for_iterations += 1
        return self.current_sample

    def set_volume(self, volume: float):
        pass
