import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

Gst.init(None)

# This function will be called when the pipeline changes states.
def on_state_changed(bus, message):
    old, new, pending = message.parse_state_changed()
    print(f"Pipeline state changed from {Gst.Element.state_get_name(old)} to {Gst.Element.state_get_name(new)}")

source = Gst.ElementFactory.make("filesrc", "source")
decoder = Gst.ElementFactory.make("decodebin", "decoder")
videoscale = Gst.ElementFactory.make("videoscale", "videoscale")
capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
sink = Gst.ElementFactory.make("autovideosink", "sink")

# Create the empty pipeline
pipeline = Gst.Pipeline.new("test-pipeline")

if not pipeline or not source or not decoder or not videoscale or not capsfilter or not sink:
    print("Not all elements could be created.")
    exit(-1)

# Set the source file location
source.set_property("location", "video.mp4")

pipeline.add(source)
pipeline.add(decoder)
pipeline.add(videoscale)
pipeline.add(capsfilter)
pipeline.add(sink)
source.link(decoder)
decoder.link(videoscale)
videoscale.link(capsfilter)
capsfilter.link(sink)

# Define a flag to ensure pad linking only happens once
pad_linked = False

# This function will be called when a new pad is added to the decoder
def on_pad_added(element, pad):
    global pad_linked
    if not pad_linked:
        pad_linked = True
        pad.link(videoscale.get_static_pad("sink"))
        decoder.disconnect(signal_id)  # Disconnect the signal handler using the signal ID

# Connect the "pad-added" signal to the on_pad_added function and capture the signal ID
signal_id = decoder.connect("pad-added", on_pad_added)

videoscale.set_property("add-borders", True)

caps = Gst.Caps.from_string("video/x-raw,width=1080,height=720")
capsfilter.set_property("caps", caps)

pipeline.set_state(Gst.State.PLAYING)

bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# Free resources
pipeline.set_state(Gst.State.NULL)
