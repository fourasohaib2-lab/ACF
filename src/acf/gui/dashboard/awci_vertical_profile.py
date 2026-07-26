"""
AWCI Vertical Profile Widget
============================

Shows AWCI complexity by flight level.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QBrush, QLinearGradient

from typing import Dict, Optional, List


class AWCIVerticalProfile(QWidget):
    """
    Vertical profile of AWCI complexity by flight level.
    
    Shows how complexity varies with altitude.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self._profile = {}
        self._highlight_level = None
        self._title = "Profil Vertical AWCI"
        
        self.setMinimumSize(200, 250)
        self.setStyleSheet("background: transparent;")
    
    def set_profile(self, profile: Dict[str, float]):
        """
        Set vertical profile data.
        
        Parameters
        ----------
        profile : dict
            {level: score} where level is string like 'FL100', 'FL300'
        """
        self._profile = profile
        self.update()
    
    def set_highlight(self, level: str):
        """Highlight a specific flight level."""
        self._highlight_level = level
        self.update()
    
    def set_title(self, title: str):
        """Set widget title."""
        self._title = title
        self.update()
    
    def paintEvent(self, event):
        """Draw the vertical profile."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # Draw title
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(QColor(200, 200, 220), 1))
        painter.drawText(10, 20, self._title)
        
        if not self._profile:
            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(10, height // 2, "Aucune donnée")
            painter.end()
            return
        
        # Sort levels by altitude (FL100 < FL200 < FL300...)
        def parse_fl(level: str) -> int:
            try:
                return int(level.replace('FL', ''))
            except:
                return 0
        
        sorted_items = sorted(self._profile.items(), key=lambda x: parse_fl(x[0]))
        
        # Draw profile
        margin_left = 50
        margin_right = 20
        margin_top = 35
        margin_bottom = 20
        
        plot_width = width - margin_left - margin_right
        plot_height = height - margin_top - margin_bottom
        
        if plot_width < 10 or plot_height < 10:
            painter.end()
            return
        
        # Find min/max scores
        scores = list(self._profile.values())
        min_score = 0
        max_score = max(100, max(scores) + 10)
        
        # Draw bars
        bar_width = min(20, plot_width / len(sorted_items) * 0.7)
        bar_spacing = bar_width * 0.3
        
        font.setPointSize(7)
        font.setBold(False)
        painter.setFont(font)
        
        for i, (level, score) in enumerate(sorted_items):
            x = margin_left + i * (bar_width + bar_spacing) + bar_spacing / 2
            
            # Normalize score to height
            normalized = score / max_score
            bar_height = normalized * plot_height
            y = margin_top + plot_height - bar_height
            
            # Determine color based on score
            if score >= 85:
                color = QColor(255, 0, 0)
            elif score >= 65:
                color = QColor(255, 100, 0)
            elif score >= 50:
                color = QColor(255, 200, 0)
            elif score >= 35:
                color = QColor(100, 200, 50)
            else:
                color = QColor(0, 200, 100)
            
            # Highlight if this level is selected
            is_highlight = (self._highlight_level == level)
            
            # Draw bar
            if is_highlight:
                painter.setBrush(QBrush(color.lighter(130)))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
            else:
                painter.setBrush(QBrush(color))
                painter.setPen(QPen(Qt.NoPen))
            
            painter.drawRect(int(x), int(y), int(bar_width), int(bar_height))
            
            # Draw score text
            painter.setPen(QPen(QColor(200, 200, 220), 1))
            score_text = f"{int(score)}"
            painter.drawText(int(x), int(y - 12), int(bar_width), 12, Qt.AlignCenter, score_text)
            
            # Draw level label
            painter.setPen(QPen(QColor(150, 150, 180), 1))
            painter.drawText(int(x), int(margin_top + plot_height + 5), int(bar_width), 12, Qt.AlignCenter, level)
        
        # Draw grid lines
        painter.setPen(QPen(QColor(50, 50, 80), 1, Qt.DashLine))
        for grid_score in [25, 50, 75]:
            y = margin_top + plot_height - (grid_score / max_score) * plot_height
            painter.drawLine(margin_left, int(y), width - margin_right, int(y))
            
            painter.setPen(QPen(QColor(100, 100, 130), 1))
            painter.drawText(5, int(y) + 4, 35, 12, Qt.AlignRight, f"{grid_score}")
        
        painter.end()
    
    def sizeHint(self):
        return QSize(250, 300)
