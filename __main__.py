import logging
import os
import sys

sys.path.append(os.path.dirname(__file__))
logging.basicConfig(level=logging.DEBUG)

from audio_input import AudioInput  # NOQA
from viz_container import VizContainer  # NOQA


def main():
    ai = AudioInput()
    ai.init_stream()
    vc = VizContainer(ai)
    vc.start()

if __name__ == "__main__":
    main()
