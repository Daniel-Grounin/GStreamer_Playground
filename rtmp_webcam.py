import cv2
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

Gst.init(None)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit(-1)

# Create GStreamer elements
pipeline = Gst.Pipeline.new("webcam-stream")
appsrc = Gst.ElementFactory.make("appsrc", "app-source")
capsfilter = Gst.ElementFactory.make("capsfilter", "caps-filter")
x264enc = Gst.ElementFactory.make("x264enc", "video-encoder")
flvmux = Gst.ElementFactory.make("flvmux", "muxer")
rtmpsink = Gst.ElementFactory.make("rtmpsink", "rtmp-sink")

if not pipeline or not appsrc or not capsfilter or not x264enc or not flvmux or not rtmpsink:
    print("Error creating GStreamer elements")
    exit(-1)

# Set GStreamer properties
caps = Gst.Caps.from_string("video/x-raw,format=I420,width=320,height=240,framerate=30/1")

capsfilter.set_property("caps", caps)  # Set caps filter
rtmpsink.set_property("location", "rtmp://your-ip-address/live")  # Set RTMP server URL

pipeline.add(appsrc, capsfilter, x264enc, flvmux, rtmpsink)

appsrc.link(capsfilter)
capsfilter.link(x264enc)
x264enc.link(flvmux)
flvmux.link(rtmpsink)

# Set the pipeline to PLAYING state
pipeline.set_state(Gst.State.PLAYING)

# Create a GMainLoop for GStreamer
loop = GLib.MainLoop()

def push_frame_to_gstreamer():
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to I420 format
        appsrc.emit("push-buffer", Gst.Buffer.new_wrapped(frame.tobytes()))

try:
    # Create a thread to push frames to GStreamer
    import threading
    threading.Thread(target=push_frame_to_gstreamer).start()

    # Start the GMainLoop
    loop.run()

except KeyboardInterrupt:
    pass

# Release resources
cap.release()
pipeline.set_state(Gst.State.NULL)
