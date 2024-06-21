from tortoise.utils.audio import load_voices
from torchaudio import save
from uuid import uuid4
from tortoise.utils.wav2vec_alignment import Wav2VecAlignment
import torch


class Generator:
    def __init__(self, tts):
        self.tts = tts
    def _generate(self, text, voice, count):
        voice_sel = [voice]
        voice_samples, conditioning_latents = load_voices(voice_sel)

        gen, dbg_state = self.tts.tts_with_preset(
            text,
            k=count,
            voice_samples=voice_samples,
            conditioning_latents=conditioning_latents,
            preset='fast',
            use_deterministic_seed=None,
            return_deterministic_state=True,
            cvvp_amount=0
        )

        if not isinstance(gen, list):
            gen = [gen]
        return gen


    def simple(self, text, voice, count):
        print(f'Voiceover simple, text `{text}` with voice `{voice}`')
        gen = self._generate(text, voice, count)
        print('Generated. Saving...')
        fnames = []
        for g in gen:
            fname = str(uuid4()) + ".wav"
            save(f'/stash/{fname}', g.squeeze(0).cpu(), 24000)
            fnames.append(fname)
        return fnames


    def alignment(self, text, voice, count):
        print(f'Voiceover aligned, text `{text}` with voice `{voice}`')
        alignment = Wav2VecAlignment()
        gen = self._generate(text, voice, count)
        print('Generated. Saving...')
        fnames = []
        for g in gen:
            fname = str(uuid4()) + ".wav.bin"
            alignments = alignment.align(g.squeeze(1), text, 24000)
            data = dict(audio = g, alignment = alignments)
            torch.save(data, f'/stash/{fname}')
            fnames.append(fname)

        return fnames