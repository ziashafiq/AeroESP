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

    const root = document.documentElement;

    const toggle =
        document.querySelector(
            "[data-theme-toggle]"
        );

    const menu =
        document.querySelector(
            "[data-theme-menu]"
        );

    const label =
        document.querySelector(
            "[data-theme-label]"
        );

    const icon =
        document.querySelector(
            "[data-theme-icon]"
        );

    const options =
        document.querySelectorAll(
            "[data-theme-option]"
        );

    const media =
        window.matchMedia(
            "(prefers-color-scheme: dark)"
        );


    function preference() {

        return (
            localStorage.getItem(
                "aeroesp-theme"
            )
            ||
            "system"
        );
    }


    function resolveTheme(value) {

        if (value === "system") {

            return media.matches
                ? "dark"
                : "light";
        }

        return value;
    }


    function updateMeta(theme) {

        const meta =
            document.querySelector(
                "#theme-color-meta"
            );

        if (!meta) {
            return;
        }

        meta.setAttribute(
            "content",
            theme === "dark"
                ? "#06111f"
                : "#f5f8fb"
        );
    }


    function updateControl(value) {

        if (label) {

            label.textContent =
                value === "dark"
                    ? "Dark"
                    : value === "light"
                    ? "Light"
                    : "System";
        }

        if (icon) {

            icon.textContent =
                value === "dark"
                    ? "☾"
                    : value === "light"
                    ? "☀"
                    : "◐";
        }

        options.forEach(
            (option) => {

                option.classList.toggle(
                    "is-active",
                    option.dataset.themeOption
                    === value
                );
            }
        );
    }


    function applyTheme(value) {

        const resolved =
            resolveTheme(value);

        root.dataset.theme =
            resolved;

        root.dataset.themePreference =
            value;

        updateMeta(resolved);

        updateControl(value);
    }


    function setTheme(value) {

        localStorage.setItem(
            "aeroesp-theme",
            value
        );

        applyTheme(value);
    }


    applyTheme(
        preference()
    );


    if (toggle && menu) {

        toggle.addEventListener(
            "click",
            (event) => {

                event.stopPropagation();

                menu.hidden =
                    !menu.hidden;
            }
        );
    }


    options.forEach(
        (option) => {

            option.addEventListener(
                "click",
                () => {

                    setTheme(
                        option.dataset.themeOption
                    );

                    if (menu) {
                        menu.hidden = true;
                    }
                }
            );
        }
    );


    document.addEventListener(
        "click",
        () => {

            if (menu) {
                menu.hidden = true;
            }
        }
    );


    if (menu) {

        menu.addEventListener(
            "click",
            (event) => {

                event.stopPropagation();
            }
        );
    }


    media.addEventListener(
        "change",
        () => {

            if (
                preference()
                === "system"
            ) {

                applyTheme(
                    "system"
                );
            }
        }
    );

})();
