/* ==========================================================
   AeroESP chart theming

   Charts are drawn to a canvas, so CSS custom properties cannot
   reach them: a var() in a Chart.js colour option is just a string
   the canvas cannot resolve. Every colour is therefore read out of
   the live computed style here and handed over as a concrete value.

   That is also why this file listens for changes. data-theme and
   data-palette are attributes on <html>, and when either moves the
   tokens behind them move with it - but the pixels already on the
   canvas do not. A MutationObserver re-reads the tokens and
   re-renders, which is what keeps a chart in step with the theme
   toggle and the palette picker instead of stranding it on the
   colours that happened to be current when the page loaded.
   ========================================================== */

(() => {

    "use strict";

    if (typeof window.Chart === "undefined") {
        return;
    }

    const root = document.documentElement;

    const registry = [];

    function token(name, fallback) {
        const value = getComputedStyle(root)
            .getPropertyValue(name)
            .trim();

        return value || fallback;
    }

    function alpha(rgbToken, amount) {
        const triple = token(rgbToken, "");

        if (!triple) {
            return `rgba(72, 185, 232, ${amount})`;
        }

        return `rgba(${triple}, ${amount})`;
    }

    function palette() {
        return {
            accent: token("--theme-accent", "#48b9e8"),
            accentSoft: alpha("--theme-accent-rgb", 0.28),
            accentWash: alpha("--theme-accent-rgb", 0.12),
            strong: token("--theme-accent-strong", "#007eb4"),
            text: token("--theme-text", "#10243a"),
            textSoft: token("--theme-text-soft", "#68798b"),
            grid: token("--theme-border", "rgba(15,42,67,.11)"),
            surface: token("--theme-surface", "#ffffff"),
            success: token("--success", "#14855f"),
            warning: token("--warning", "#b77418"),
            danger: token("--danger", "#c84949"),

            /* Bars on a dark surface go muddy when a light accent is
               blended down to a low alpha, so an ordered scale asks
               for its own steps rather than reusing the wash tokens. */
            at(amount) {
                return alpha("--theme-accent-rgb", amount);
            },
        };
    }

    /* Shared look, applied to every chart on the site so they read as
       one family rather than five different libraries' defaults. */
    function baseOptions(colours) {
        return {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    labels: {
                        color: colours.textSoft,
                        boxWidth: 12,
                        boxHeight: 12,
                        usePointStyle: true,
                        font: { family: "Inter, Segoe UI, Arial, sans-serif" },
                    },
                },
                tooltip: {
                    backgroundColor: colours.text,
                    titleColor: colours.surface,
                    bodyColor: colours.surface,
                    cornerRadius: 8,
                    padding: 10,
                    displayColors: false,
                },
            },

            scales: {
                x: {
                    ticks: {
                        color: colours.textSoft,
                        font: { family: "Inter, Segoe UI, Arial, sans-serif" },
                    },
                    grid: { display: false },
                    border: { color: colours.grid },
                },
                y: {
                    ticks: {
                        color: colours.textSoft,
                        font: { family: "Inter, Segoe UI, Arial, sans-serif" },
                    },
                    grid: { color: colours.grid },
                    border: { display: false },
                },
            },
        };
    }

    function merge(target, source) {
        Object.keys(source).forEach((key) => {
            const value = source[key];

            if (
                value &&
                typeof value === "object" &&
                !Array.isArray(value)
            ) {
                target[key] = merge(target[key] || {}, value);
            } else {
                target[key] = value;
            }
        });

        return target;
    }

    /**
     * build(canvasId, factory)
     *
     * factory(colours) returns a Chart.js config. It is called again
     * on every theme or palette change, so it must read its colours
     * from the argument rather than closing over them.
     */
    function build(canvasId, factory) {
        const canvas = document.getElementById(canvasId);

        if (!canvas) {
            return null;
        }

        function render() {
            const colours = palette();
            const config = factory(colours);

            config.options = merge(
                baseOptions(colours),
                config.options || {}
            );

            return new window.Chart(canvas, config);
        }

        let chart = render();

        registry.push({
            destroy() {
                chart.destroy();
            },
            rebuild() {
                chart.destroy();
                chart = render();
            },
        });

        return chart;
    }

    let pending = null;

    const observer = new MutationObserver(() => {
        /* The theme engine writes data-theme and data-palette in the
           same tick; coalescing avoids rebuilding every chart twice. */
        window.clearTimeout(pending);

        pending = window.setTimeout(() => {
            registry.forEach((entry) => entry.rebuild());
        }, 40);
    });

    observer.observe(root, {
        attributes: true,
        attributeFilter: ["data-theme", "data-palette"],
    });

    window.AeroCharts = {
        build: build,
        palette: palette,

        /* Reading a JSON payload the server rendered with json_script.
           Kept here so no page has to hand-roll it, and so a missing
           element degrades to null instead of throwing. */
        data(elementId) {
            const node = document.getElementById(elementId);

            if (!node) {
                return null;
            }

            try {
                return JSON.parse(node.textContent);
            } catch (error) {
                return null;
            }
        },
    };

})();
