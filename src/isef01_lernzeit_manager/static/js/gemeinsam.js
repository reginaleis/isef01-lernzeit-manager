const STATUS_TEXT = {
    not_started: "Noch nicht begonnen",
    in_progress: "In Bearbeitung",
    completed: "Abgeschlossen",
    overdue: "Überfällig",
};
const STUNDEN_PRO_ECTS = 30;
const NAVIGATION = [
    ["/", "Übersicht"],
    ["/lernziele.html", "Lernziele"],
    ["/halbjahresplan.html", "Halbjahresplan"],
    ["/monatsplan.html", "Monatsplan"],
    ["/lernzeit.html", "Lernzeit"],
    ["/auswertung.html", "Auswertung"],
    ["/erinnerungen.html", "Erinnerungen"],
];

function navigationErstellen() {
    const topbar = document.querySelector(".topbar");
    if (!topbar) {
        return;
    }

    const titel = document.createElement("p");
    titel.className = "navbar-brand mb-0";
    titel.textContent = "Lernzeit Manager";
    const nav = document.createElement("nav");
    nav.className = "nav flex-row flex-wrap gap-1";
    nav.setAttribute("aria-label", "Seitenauswahl");

    for (const [pfad, name] of NAVIGATION) {
        const link = document.createElement("a");
        link.href = pfad;
        link.textContent = name;
        const aktiv = window.location.pathname === pfad;
        link.className = aktiv
            ? "nav-link rounded bg-white text-success fw-bold"
            : "nav-link text-dark";
        if (aktiv) {
            link.setAttribute("aria-current", "page");
        }
        nav.append(link);
    }

    const resetButton = document.createElement("button");
    resetButton.type = "button";
    resetButton.className = "btn btn-outline-success ms-lg-auto";
    resetButton.textContent = "Demo Daten wiederherstellen";
    resetButton.addEventListener("click", () => demoDatenWiederherstellen(resetButton));
    topbar.replaceChildren(titel, nav, resetButton);
}

async function api(methode, pfad, daten) {
    if (location.protocol === "file:") {
        throw new Error("Öffne die Seite neu");
    }
    const optionen = { method: methode };
    if (daten !== undefined) {
        optionen.headers = { "Content-Type": "application/json" };
        optionen.body = JSON.stringify(daten);
    }
    let antwort;
    try {
        antwort = await fetch(pfad, optionen);
    } catch (error) {
        throw new Error(
            "Backend nicht erreicht!",
        );
    }
    if (!antwort.ok) {
        throw new Error(await fehlerText(antwort));
    }
    if (antwort.status === 204) {
        return null;
    }
    try {
        return await antwort.json();
    } catch (error) {
        throw new Error("Keine lesbare .JSON!");
    }
}
async function fehlerText(antwort) {
    const allgemein = "Das hat leider nicht geklappt (Fehler " + antwort.status + ").";
    if (antwort.status === 422) {
        return "Eingaben Prüfen!";
    }
    try {
        const inhalt = await antwort.json();
        return typeof inhalt.detail === "string" ? inhalt.detail : allgemein;
    } catch (error) {
        return allgemein;
    }
}
function leerZuNull(daten) {
    const ergebnis = {};
    for (const feld in daten) {
        ergebnis[feld] = daten[feld] === "" ? null : daten[feld];
    }
    return ergebnis;
}
function isoDatum(datum) {
    const monat = String(datum.getMonth() + 1).padStart(2, "0");
    const tag = String(datum.getDate()).padStart(2, "0");
    return datum.getFullYear() + "-" + monat + "-" + tag;
}
function heute() {
    return isoDatum(new Date());
}
function datumText(isoText) {
    if (!isoText) {
        return "–";
    }
    const teile = isoText.split("-");
    return teile[2] + "." + teile[1] + "." + teile[0];
}
function tageZwischen(von, bis) {
    if (!von || !bis || bis < von) {
        return 0;
    }
    const beginn = new Date(von + "T00:00:00Z");
    const ende = new Date(bis + "T00:00:00Z");
    const einTag = 24 * 60 * 60 * 1000;
    return Math.round((ende - beginn) / einTag) + 1;
}
function minutenText(minuten) {
    const stunden = Math.floor(minuten / 60);
    const rest = minuten % 60;
    if (stunden === 0) {
        return rest + " min";
    }
    return stunden + " h " + rest + " min";
}

async function demoDatenWiederherstellen(button) {
    button.disabled = true;
    try {
        await api("POST", "/api/demo/resetdata");
        window.location.reload();
    } catch (error) {
        alert(error.message);
        button.disabled = false;
    }
}

navigationErstellen();
