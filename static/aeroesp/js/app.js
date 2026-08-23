(() => {

    "use strict";

    const body = document.body;

    const menuButton =
        document.querySelector(
            "[data-sidebar-toggle]"
        );

    const overlay =
        document.querySelector(
            "[data-sidebar-overlay]"
        );

    const sidebar =
        document.querySelector(
            "[data-sidebar]"
        );


    function openSidebar() {

        body.classList.add(
            "sidebar-open"
        );

        if (menuButton) {
            menuButton.setAttribute(
                "aria-expanded",
                "true"
            );
        }
    }


    function closeSidebar() {

        body.classList.remove(
            "sidebar-open"
        );

        if (menuButton) {
            menuButton.setAttribute(
                "aria-expanded",
                "false"
            );
        }
    }


    function toggleSidebar() {

        if (
            body.classList.contains(
                "sidebar-open"
            )
        ) {

            closeSidebar();

        } else {

            openSidebar();
        }
    }


    if (menuButton) {

        menuButton.addEventListener(
            "click",
            toggleSidebar
        );
    }


    if (overlay) {

        overlay.addEventListener(
            "click",
            closeSidebar
        );
    }


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape"
            ) {

                closeSidebar();
            }
        }
    );


    if (sidebar) {

        sidebar
            .querySelectorAll(
                "a"
            )
            .forEach(
                (link) => {

                    link.addEventListener(
                        "click",
                        () => {

                            if (
                                window.innerWidth
                                <= 860
                            ) {

                                closeSidebar();
                            }
                        }
                    );
                }
            );
    }


    /* ===============================================
       Automatic active navigation detection
       =============================================== */

    const currentPath =
        window.location.pathname;

    const navLinks =
        Array.from(
            document.querySelectorAll(
                "[data-nav-link]"
            )
        );

    let bestMatch = null;

    let bestLength = -1;


    navLinks.forEach(
        (link) => {

            let linkPath;

            try {

                linkPath =
                    new URL(
                        link.href,
                        window.location.origin
                    ).pathname;

            } catch {

                return;
            }


            const exactMatch =
                currentPath
                === linkPath;

            const nestedMatch =
                linkPath !== "/"
                &&
                currentPath
                    .startsWith(
                        linkPath
                    );


            if (
                exactMatch
                ||
                nestedMatch
            ) {

                if (
                    linkPath.length
                    > bestLength
                ) {

                    bestMatch = link;

                    bestLength =
                        linkPath.length;
                }
            }
        }
    );


    if (bestMatch) {

        bestMatch.classList.add(
            "is-active"
        );

        bestMatch.setAttribute(
            "aria-current",
            "page"
        );
    }


    /* ===============================================
       External links
       =============================================== */

    document
        .querySelectorAll(
            'a[target="_blank"]'
        )
        .forEach(
            (link) => {

                if (
                    !link.rel
                        .includes(
                            "noopener"
                        )
                ) {

                    link.rel =
                        `${
                            link.rel
                        } noopener noreferrer`
                        .trim();
                }
            }
        );

})();

/* ==========================================================
   AeroESP Theme Engine
   ========================================================== */

(() => {
    "use strict";

    const KEY = "aeroesp-theme";
    const root = document.documentElement;
    const media = window.matchMedia("(prefers-color-scheme: dark)");

    const buttons = Array.from(
        document.querySelectorAll("[data-theme-option]")
    );

    function getPreference() {
        const value = localStorage.getItem(KEY);

        if (
            value === "light" ||
            value === "dark" ||
            value === "system"
        ) {
            return value;
        }

        return "system";
    }

    function resolvedTheme(preference) {
        if (preference === "system") {
            return media.matches ? "dark" : "light";
        }

        return preference;
    }

    function apply(preference) {
        const resolved = resolvedTheme(preference);

        root.setAttribute("data-theme", resolved);
        root.setAttribute("data-theme-preference", preference);

        buttons.forEach((button) => {
            const active =
                button.dataset.themeOption === preference;

            button.classList.toggle("is-active", active);
            button.setAttribute(
                "aria-pressed",
                active ? "true" : "false"
            );
        });

        const meta =
            document.getElementById("theme-color-meta");

        if (meta) {
            meta.content =
                resolved === "dark"
                    ? "#06111f"
                    : "#f5f8fb";
        }
    }

    function setPreference(preference) {
        localStorage.setItem(KEY, preference);
        apply(preference);
    }

    buttons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            setPreference(
                button.dataset.themeOption
            );
        });
    });

    media.addEventListener("change", () => {
        if (getPreference() === "system") {
            apply("system");
        }
    });

    apply(getPreference());

})();
