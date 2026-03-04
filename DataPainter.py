from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

import numpy as np
import plotly.graph_objects as go

import webbrowser
from pathlib import Path


####################################################
# FOREIGN = X AXIS
# HOME    = Y AXIS
####################################################


@dataclass
class ScatterRecord:
    name: str
    x: np.ndarray
    y: np.ndarray
    values: np.ndarray
    meta: Dict[str, Any] = field(default_factory=dict)


class DataPainter:

    # ==================================================
    # INIT
    # ==================================================

    def __init__(self, xlabels_foreign=None, ylabels_home=None):

        self._registry: Dict[str, ScatterRecord] = {}
        self._view = None

        # global labels (never sliced!)
        self._xlabels_foreign = (
            np.asarray(xlabels_foreign, dtype=object)
            if xlabels_foreign is not None else None
        )

        self._ylabels_home = (
            np.asarray(ylabels_home, dtype=object)
            if ylabels_home is not None else None
        )

        self._cmin = None
        self._cmax = None

    # ==================================================
    # DATA REGISTRATION
    # ==================================================

    def register_points(self, name, x, y, values, **meta):

        x = np.asarray(x, dtype=np.int32)
        y = np.asarray(y, dtype=np.int32)
        values = np.asarray(values)

        if not (len(x) == len(y) == len(values)):
            raise ValueError("x,y,values müssen gleiche Länge haben")

        # ---- global label safety check ----
        if self._xlabels_foreign is not None:
            if np.max(x) >= len(self._xlabels_foreign):
                raise ValueError("x index outside label range")

        if self._ylabels_home is not None:
            if np.max(y) >= len(self._ylabels_home):
                raise ValueError("y index outside label range")

        self._registry[name] = ScatterRecord(
            name=name,
            x=x,
            y=y,
            values=values,
            meta=meta
        )

    # ==================================================
    # VIEW WINDOW
    # ==================================================

    def set_view(self, y0_home, y1_home, x0_foreign, x1_foreign):
        self._view = (y0_home, y1_home, x0_foreign, x1_foreign)

    def _apply_view(self, record: ScatterRecord):

        if self._view is None:
            return record.x, record.y, record.values

        y0, y1, x0, x1 = self._view

        mask = (
            (record.y >= y0) &
            (record.y < y1) &
            (record.x >= x0) &
            (record.x < x1)
        )

        return (
            record.x[mask],
            record.y[mask],
            record.values[mask]
        )

    # ==================================================
    # LABEL LOOKUP  (CORE LOGIC)
    # ==================================================

    def _build_customdata(self, x, y):

        if self._xlabels_foreign is None or self._ylabels_home is None:
            return None

        # vectorized index lookup
        return np.column_stack((
            self._ylabels_home[y],
            self._xlabels_foreign[x]
        ))

    # ==================================================
    # PERFORMANCE SAFETY (LOD)
    # ==================================================

    def _lod(self, x, y, values, max_points=2500000):

        n = len(x)

        if n <= max_points:
            return x, y, values

        step = n // max_points
        idx = np.arange(0, n, step)

        return x[idx], y[idx], values[idx]

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self):

        if not self._registry:
            raise ValueError("Keine Daten registriert")

        # global colorscale
        self._cmin = min(np.min(r.values) for r in self._registry.values())
        self._cmax = max(np.max(r.values) for r in self._registry.values())

        fig = go.Figure()

        # ---------- initial trace ----------
        first = next(iter(self._registry.values()))

        x, y, values = self._apply_view(first)
        x, y, values = self._lod(x, y, values)

        custom = self._build_customdata(x, y)

        fig.add_trace(go.Scattergl(
            x=x,
            y=y,
            customdata=custom,
            mode="markers",
            marker=dict(
                size=6,
                color=values,
                colorscale="Viridis_r",
                cmin=self._cmin,
                cmax=self._cmax,
                showscale=True
            ),
            hovertemplate=(
                "X: %{customdata[1]}<br>"
                "Y: %{customdata[0]}<br>"
                "value: %{marker.color}<extra></extra>"
                if custom is not None else
                "X: %{x}<br>Y: %{y}<br>value: %{marker.color}<extra></extra>"
            )
        ))

        # ---------- slider ----------
        steps = []

        for name, record in self._registry.items():

            x, y, values = self._apply_view(record)
            x, y, values = self._lod(x, y, values)

            custom = self._build_customdata(x, y)

            steps.append(dict(
                method="restyle",
                args=[{
                    "x": [x],
                    "y": [y],
                    "marker.color": [values],
                    "customdata": [custom]
                }, [0]],
                label=name
            ))

        fig.update_layout(
            sliders=[dict(
                active=0,
                currentvalue={"prefix": "Matrix: "},
                steps=steps
            )],
            uirevision=True,
            xaxis_title="Foreign",
            yaxis_title="Home"
        )






        #fig.show()
        html = fig.to_html(include_plotlyjs="cdn")

        keyboard_js = """
        <script>
document.addEventListener("DOMContentLoaded", function () {

    const plot = document.querySelector(".plotly-graph-div");

    let sliderIndex = 0;

    function runSliderStep(index) {

        const slider = plot.layout.sliders[0];
        const step = slider.steps[index];

        sliderIndex = index;

        // 👉 Slider visuell bewegen
        Plotly.relayout(plot, {
            "sliders[0].active": index
        });

        // 👉 UND Step wirklich ausführen
        Plotly[step.method](plot, ...step.args);
    }

    document.addEventListener("keydown", function(e) {

        const slider = plot.layout.sliders[0];
        const max = slider.steps.length - 1;

        if (e.key === "ArrowRight") {
            runSliderStep(Math.min(sliderIndex + 1, max));
        }

        if (e.key === "ArrowLeft") {
            runSliderStep(Math.max(sliderIndex - 1, 0));
        }
    });

});
</script>
        """

        html = html.replace("</body>", keyboard_js + "</body>")

        file = Path("viewer.html").resolve()

        file.write_text(html, encoding="utf8")

        # 👉 automatisch öffnen
        webbrowser.open(f"file://{file}")