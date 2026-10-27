registerShortcut(
    "launch-mission-center",
    "Open Mission Center",
    "Ctrl+Shift+Escape",
    function () {
        callDBus(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "ResetFailedUnit",
            "mission-center.service"
        );
        callDBus(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1",
            "org.freedesktop.systemd1.Manager",
            "StartUnit",
            "mission-center.service",
            "replace"
        );
    }
);
