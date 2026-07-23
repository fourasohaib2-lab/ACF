#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "======================================="
echo " ACF Sprint 08 - Partie 7"
echo " Animation Engine"
echo "======================================="

####################################################
# DOSSIER
####################################################

mkdir -p "$PROJECT/src/acf/animation"

touch "$PROJECT/src/acf/animation/__init__.py"

####################################################
# ANIMATION ENGINE
####################################################

cat > "$PROJECT/src/acf/animation/animation_engine.py" << 'EOF'
"""
Animation Engine
"""

from acf.time.time_manager import TimeManager


class AnimationEngine:

    def __init__(self, time_manager=None):

        self.time_manager = time_manager or TimeManager()

        self.running = False

        self.loop = False

    ##################################################

    def play(self):

        self.running = True

    ##################################################

    def pause(self):

        self.running = False

    ##################################################

    def stop(self):

        self.running = False

        self.time_manager.first()

    ##################################################

    def next_frame(self):

        return self.time_manager.next()

    ##################################################

    def previous_frame(self):

        return self.time_manager.previous()

    ##################################################

    def current_frame(self):

        return self.time_manager.current()

    ##################################################

    def set_loop(self, enabled=True):

        self.loop = bool(enabled)
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_animation_engine.py" << 'EOF'
from datetime import datetime, timedelta

from acf.animation.animation_engine import AnimationEngine
from acf.time.time_manager import TimeManager


def test_play_pause():

    engine = AnimationEngine()

    assert engine.running is False

    engine.play()

    assert engine.running is True

    engine.pause()

    assert engine.running is False


def test_navigation():

    manager = TimeManager()

    manager.load([
        datetime(2026,1,1)+timedelta(hours=i)
        for i in range(4)
    ])

    engine = AnimationEngine(manager)

    assert engine.current_frame() == manager.current()

    engine.next_frame()

    assert engine.current_frame() == manager.current()

    engine.stop()

    assert manager.index == 0
EOF

####################################################
# EXEMPLE
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_animation.py" << 'EOF'
from datetime import datetime, timedelta

from acf.animation.animation_engine import AnimationEngine
from acf.time.time_manager import TimeManager

manager = TimeManager()

manager.load([
    datetime(2026,1,1,0)+timedelta(hours=3*i)
    for i in range(8)
])

engine = AnimationEngine(manager)

print("Current :", engine.current_frame())

engine.play()

print("Running :", engine.running)

engine.next_frame()

print("Next :", engine.current_frame())

engine.stop()

print("After stop :", engine.current_frame())
EOF

echo
echo "Animation Engine successfully installed."
