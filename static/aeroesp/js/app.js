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



    /* ==========================================================
       AeroESP Theme Engine

       Part of this same scope on purpose. The sidebar handlers at the
       end of this file (Escape-to-close, the back/forward reset) read
       body, menuButton, sidebar and closeSidebar, which are declared
       above. While this lived in a second IIFE those were out of
       scope, so it threw ReferenceError on every page load and both
       handlers were silently dead.
       ========================================================== */

    const KEY = "aeroesp-theme";
    const root = document.documentElement;
    const media = window.matchMedia("(prefers-color-scheme: dark)");

    const buttons = Array.from(
        document.querySelectorAll("[data-theme-option]")
    );

    /* In-app WebViews (the Google app among them) can have site data
       blocked, and there localStorage does not return null - it
       throws. Unguarded that exception killed this whole IIFE, so the
       theme buttons stopped responding and the system-change listener
       was never attached, while Chrome was unaffected. Every access is
       wrapped, with an in-memory value so the toggle still works for
       the current page even when nothing can be persisted. */
    let memoryPreference = null;

    function getPreference() {
        let value = memoryPreference;

        if (value === null) {
            try {
                value = localStorage.getItem(KEY);
            } catch (error) {
                value = null;
            }
        }

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
        memoryPreference = preference;

        try {
            localStorage.setItem(KEY, preference);
        } catch (error) {
            /* Not persistable here; the in-memory value still drives
               this page, and the button stays responsive. */
        }

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

    /* MediaQueryList.addEventListener is comparatively recent; older
       WebViews only expose the deprecated addListener, and calling the
       missing method throws - taking the rest of this script with it. */
    const onSystemChange = () => {
        if (getPreference() === "system") {
            apply("system");
        }
    };

    if (typeof media.addEventListener === "function") {
        media.addEventListener("change", onSystemChange);
    } else if (typeof media.addListener === "function") {
        media.addListener(onSystemChange);
    }

    apply(getPreference());



    /* ==========================================================
       AeroESP Palette Engine

       Light/dark and palette are independent axes: the theme decides
       the surfaces, the palette decides the accent on top of them.
       Both are stamped on <html> and the whole stylesheet follows
       from six custom properties, so nothing here touches styling
       directly.

       Where the choice lives depends on who is asking. A signed-in
       user's palette is rendered into the document by the server -
       authoritative, follows them to any device, and no flash of the
       default on first paint. A guest's lives in localStorage only.
       ========================================================== */

    const PALETTE_KEY = "aeroesp-palette";

    const PALETTES = [
        "skyline",
        "copper",
        "indigo",
        "verdigris",
        "slate",
    ];

    const paletteControl =
        document.querySelector("[data-palette-control]");

    const paletteButtons = Array.from(
        document.querySelectorAll("[data-palette-option]")
    );

    let memoryPalette = null;

    function storedPalette() {
        let value = memoryPalette;

        if (value === null) {
            try {
                value = localStorage.getItem(PALETTE_KEY);
            } catch (error) {
                /* Same WebView storage trap as the theme above. */
                value = null;
            }
        }

        return PALETTES.indexOf(value) === -1 ? "skyline" : value;
    }

    function rememberPalette(palette) {
        memoryPalette = palette;

        try {
            localStorage.setItem(PALETTE_KEY, palette);
        } catch (error) {
            /* Unpersistable here; the in-memory value still applies. */
        }
    }

    function applyPalette(palette) {
        root.setAttribute("data-palette", palette);

        paletteButtons.forEach((button) => {
            const active =
                button.dataset.paletteOption === palette;

            button.classList.toggle("is-active", active);
            button.setAttribute(
                "aria-pressed",
                active ? "true" : "false"
            );
        });
    }

    function savePaletteForUser(palette) {
        if (!paletteControl) {
            return;
        }

        const endpoint = paletteControl.dataset.paletteEndpoint;

        if (!endpoint) {
            /* Anonymous visitor: localStorage is the whole story. */
            return;
        }

        const token = paletteControl.querySelector(
            "input[name=csrfmiddlewaretoken]"
        );

        const body = new FormData();
        body.append("palette", palette);

        /* Fire and forget. The attribute is already applied, so a
           failed write costs the user nothing on this device - it
           only means the choice will not follow them to the next. */
        try {
            fetch(endpoint, {
                method: "POST",
                body: body,
                credentials: "same-origin",
                headers: token
                    ? { "X-CSRFToken": token.value }
                    : {},
            }).catch(() => undefined);
        } catch (error) {
            /* No fetch, or blocked: nothing further to do. */
        }
    }

    function setPalette(palette) {
        if (PALETTES.indexOf(palette) === -1) {
            return;
        }

        rememberPalette(palette);
        applyPalette(palette);
        savePaletteForUser(palette);
    }

    paletteButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();

            setPalette(button.dataset.paletteOption);
        });
    });

    /* A server-rendered palette wins over whatever this browser has
       stored: it is the account's setting, and the account is what
       the user changed. Storage is then brought into line so the
       pre-paint bootstrap agrees on the next load. */
    const serverPalette =
        root.dataset.paletteSource === "user"
            ? root.dataset.palette
            : null;

    if (serverPalette && PALETTES.indexOf(serverPalette) !== -1) {
        rememberPalette(serverPalette);
        applyPalette(serverPalette);
    } else {
        applyPalette(storedPalette());
    }



    /* ==========================================================
       Avatar picker

       Signed-in users only - there is nowhere to put a guest's
       choice, and nowhere it would be shown. The chosen mark appears
       in three places, so the page is reloaded rather than patched:
       swapping three DOM nodes by hand is how they drift apart.
       ========================================================== */

    const avatarControl =
        document.querySelector("[data-avatar-control]");

    if (avatarControl) {

        const avatarButtons = Array.from(
            avatarControl.querySelectorAll("[data-avatar-option]")
        );

        const markActive = (choice) => {
            avatarButtons.forEach((button) => {
                const active =
                    button.dataset.avatarOption === choice;

                button.classList.toggle("is-active", active);
                button.setAttribute(
                    "aria-checked",
                    active ? "true" : "false"
                );
            });
        };

        markActive(avatarControl.dataset.avatarCurrent || "INITIAL");

        avatarButtons.forEach((button) => {
            button.addEventListener("click", (event) => {
                event.preventDefault();

                const choice = button.dataset.avatarOption;
                const endpoint =
                    avatarControl.dataset.avatarEndpoint;

                markActive(choice);

                if (!endpoint) {
                    return;
                }

                const token = avatarControl.querySelector(
                    "input[name=csrfmiddlewaretoken]"
                );

                const body = new FormData();
                body.append("avatar", choice);

                try {
                    fetch(endpoint, {
                        method: "POST",
                        body: body,
                        credentials: "same-origin",
                        headers: token
                            ? { "X-CSRFToken": token.value }
                            : {},
                    })
                        .then((response) => {
                            if (response.ok) {
                                window.location.reload();
                            }
                        })
                        .catch(() => undefined);
                } catch (error) {
                    /* No fetch here; the selection still shows. */
                }
            });
        });
    }



    /* ===============================================
       UI-08 Accessibility + responsive polish
       =============================================== */

    window.addEventListener(
        "resize",
        () => {

            if (
                window.innerWidth
                > 860
                &&
                body.classList.contains(
                    "sidebar-open"
                )
            ) {
                closeSidebar();
            }
        }
    );


    if (
        menuButton
        &&
        sidebar
    ) {

        menuButton.addEventListener(
            "click",
            () => {

                if (
                    body.classList.contains(
                        "sidebar-open"
                    )
                ) {

                    window.requestAnimationFrame(
                        () => {

                            const target =
                                sidebar.querySelector(
                                    "a, button"
                                );

                            if (target) {
                                target.focus();
                            }
                        }
                    );
                }
            }
        );
    }


    document.addEventListener(
        "keydown",
        (event) => {

            if (
                event.key === "Escape"
                &&
                body.classList.contains(
                    "sidebar-open"
                )
            ) {

                closeSidebar();

                if (menuButton) {
                    menuButton.focus();
                }
            }
        },
        true
    );


    /*
    Prevent stale mobile navigation state
    when returning through browser history.
    */

    window.addEventListener(
        "pageshow",
        () => {

            if (
                window.innerWidth
                > 860
            ) {
                closeSidebar();
            }
        }
    );


})();
