# Decisions

- 2026-11-03: Detection uses the CAM1 main stream (H.265, 2304x1296, 20 fps). If the GPU is slow, the pipeline skips every second frame.
- 2026-11-04: Before an agent records from a camera, it must tell the user in the channel. Then it waits until the user is ready. The message gives the start time, the automatic stop time, and what the user must do (for example, carry cartons). A run on a clip that is already recorded does not need a message.
