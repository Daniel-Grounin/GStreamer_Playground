import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

def main():
    # Initialize GStreamer
    Gst.init(None)

    # Create a pipeline
    pipeline = Gst.parse_launch("videotestsrc ! autovideosink")

    # Start the pipeline
    pipeline.set_state(Gst.State.PLAYING)

    # Wait for EOS (End-of-Stream) or error
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

    # Stop the pipeline
    pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':
    main()
 
