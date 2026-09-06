"""
acf.animation - AnimationEngine, a real frame-stepping controller
(play/pause/stop/next_frame/previous_frame/loop) over
acf.time.time_manager.TimeManager (already audited as real - this
class is its one real caller). Already fixed for a real loop-mode bug
(set_loop() was never consulted by next_frame()).
"""
