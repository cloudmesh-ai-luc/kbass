"use strict";

const API = {
    health: "/health",
    incidents: "/api/incidents",
    applications: "/api/applications",
};

const REFRESH_INTERVAL_MS = 15000;

function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
}

async function fetchJSON(url) {
    const response = await fetch(url, {
        headers: { Accept: "application/json" },
        cache: "no-store",
    });

    if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
}

async function updateHealth() {
    const element = document.getElementById("health-status");

    try {
        const data = await fetchJSON(API.health);
        const healthy = data.status === "healthy";

        setText("health-status", healthy ? "Healthy" : "Degraded");
        element.className = healthy ? "status-healthy" : "status-error";
    } catch (error) {
        setText("health-status", "Unavailable");
        element.className = "status-error";
    }
}

function createCell(value, className = "") {
    const cell = document.createElement("td");
    cell.textContent = value ?? "—";
    if (className) cell.className = className;
    return cell;
}

function renderIncidents(incidents) {
    const tbody = document.getElementById("incident-table");
    tbody.replaceChildren();

    if (incidents.length === 0) {
        const row = document.createElement("tr");
        const cell = createCell("No active or pending incidents.");
        cell.colSpan = 5;
        cell.className = "empty-state";
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    for (const incident of incidents) {
        const row = document.createElement("tr");
        const severity = String(incident.severity || "unknown");
        const severityClass = ["critical", "warning", "info"].includes(severity)
            ? `severity-${severity}`
            : "";

        let detected = "—";
        if (incident.active_at) {
            const date = new Date(incident.active_at);
            if (!Number.isNaN(date.getTime())) {
                detected = date.toLocaleString();
            }
        }

        row.append(
            createCell(incident.name),
            createCell(severity, severityClass),
            createCell(incident.state),
            createCell(incident.summary),
            createCell(detected),
        );

        tbody.appendChild(row);
    }
}

async function updateIncidents() {
    try {
        const data = await fetchJSON(API.incidents);

        if (data.status !== "success" || !Array.isArray(data.incidents)) {
            throw new Error("Invalid incident response");
        }

        const incidents = data.incidents;
        const critical = incidents.filter(
            incident => incident.severity === "critical"
        ).length;

        setText("incident-count", incidents.length);
        setText("critical-count", critical);
        setText("monitoring-status", "Connected");
        renderIncidents(incidents);
    } catch (error) {
        setText("incident-count", "—");
        setText("critical-count", "—");
        setText("monitoring-status", "Unavailable");

        const tbody = document.getElementById("incident-table");
        const row = document.createElement("tr");
        const cell = createCell("Unable to retrieve Prometheus incidents.");
        cell.colSpan = 5;
        cell.className = "empty-state";
        row.appendChild(cell);
        tbody.replaceChildren(row);
    }
}

function renderApplications(applications) {
    const tbody = document.getElementById("application-table");
    tbody.replaceChildren();

    if (applications.length === 0) {
        const row = document.createElement("tr");
        const cell = createCell("No applications registered yet.");
        cell.colSpan = 3;
        cell.className = "empty-state";
        row.appendChild(cell);
        tbody.appendChild(row);
        return;
    }

    for (const application of applications) {
        const row = document.createElement("tr");

        row.append(
            createCell(application.name),
            createCell(application.environment),
            createCell(application.enabled ? "Enabled" : "Disabled",
                application.enabled ? "status-healthy" : "severity-warning"),
        );

        tbody.appendChild(row);
    }
}

async function updateApplications() {
    try {
        const data = await fetchJSON(API.applications);

        if (!Array.isArray(data.applications)) {
            throw new Error("Invalid applications response");
        }

        setText("application-count",
            `${data.applications.length} registered`);
        renderApplications(data.applications);
    } catch (error) {
        setText("application-count", "Unavailable");

        const row = document.createElement("tr");
        const cell = createCell("Unable to load registered applications.");
        cell.colSpan = 3;
        cell.className = "empty-state";
        row.appendChild(cell);

        document.getElementById("application-table")
            .replaceChildren(row);
    }
}

let refreshInProgress = false;

async function refreshDashboard() {
    if (refreshInProgress) return;

    refreshInProgress = true;

    const button = document.getElementById("refresh-button");
    button.disabled = true;

    try {
        await Promise.all([updateHealth(), updateIncidents(), updateApplications()]);
        setText("last-updated", `Updated ${new Date().toLocaleTimeString()}`);
    } finally {
        button.disabled = false;
        refreshInProgress = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("refresh-button")
        .addEventListener("click", refreshDashboard);

    refreshDashboard();
    setInterval(refreshDashboard, REFRESH_INTERVAL_MS);
});

// Browser administrator authentication
let adminCsrfToken = null;

function setAdminAuthenticated(authenticated) {
    const loginForm = document.getElementById("admin-login-form");
    const logoutButton = document.getElementById("admin-logout-button");
    const registrationForm = document.getElementById("application-form");

    loginForm.hidden = authenticated;
    logoutButton.hidden = !authenticated;

    for (const control of registrationForm.elements) {
        control.disabled = !authenticated;
    }

    const submitButton = registrationForm.querySelector(
        'button[type="submit"]'
    );
    submitButton.textContent = authenticated
        ? "Register Application"
        : "Registration Requires Sign In";
}

async function handleAdminLogin(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const tokenInput = document.getElementById("admin-token");
    const button = document.getElementById("admin-login-button");
    const token = tokenInput.value;

    button.disabled = true;
    setText("admin-auth-status", "Signing in...");

    try {
        const response = await fetch("/api/auth/login", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
            body: JSON.stringify({ token }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        if (typeof data.csrf_token !== "string" || !data.csrf_token) {
            throw new Error("Missing CSRF token");
        }

        adminCsrfToken = data.csrf_token;
        setAdminAuthenticated(true);
        setText("admin-auth-status", "Administrator authenticated.");
    } catch (error) {
        adminCsrfToken = null;
        setAdminAuthenticated(false);
        setText("admin-auth-status", `Sign in failed: ${error.message}`);
    } finally {
        tokenInput.value = "";
        button.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setAdminAuthenticated(false);
    document.getElementById("admin-login-form")
        .addEventListener("submit", handleAdminLogin);
});

// End the administrator session securely.
async function handleAdminLogout() {
    const button = document.getElementById("admin-logout-button");

    if (!adminCsrfToken) {
        setAdminAuthenticated(false);
        setText("admin-auth-status", "Please sign in again.");
        return;
    }

    button.disabled = true;
    setText("admin-auth-status", "Signing out...");

    try {
        const response = await fetch("/api/auth/logout", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                Accept: "application/json",
                "X-CSRF-Token": adminCsrfToken,
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        adminCsrfToken = null;
        setAdminAuthenticated(false);
        setText("admin-auth-status", "Signed out successfully.");
    } catch (error) {
        setText(
            "admin-auth-status",
            `Sign out failed: ${error.message}`
        );
    } finally {
        button.disabled = false;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("admin-logout-button")
        .addEventListener("click", handleAdminLogout);
});

// Register an application using the authenticated browser session.
async function handleApplicationRegistration(event) {
    event.preventDefault();

    const form = event.currentTarget;
    const submitButton = form.querySelector('button[type="submit"]');

    if (!adminCsrfToken) {
        setAdminAuthenticated(false);
        setText("admin-auth-status", "Please sign in before registering.");
        return;
    }

    const fields = new FormData(form);
    const payload = {
        name: String(fields.get("name") || "").trim(),
        environment: String(fields.get("environment") || ""),
        health_url: String(fields.get("health_url") || "").trim(),
        metrics_url: String(fields.get("metrics_url") || "").trim() || null,
    };

    submitButton.disabled = true;
    submitButton.textContent = "Registering...";

    try {
        const response = await fetch(API.applications, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
                "X-CSRF-Token": adminCsrfToken,
            },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (response.status === 401 || response.status === 403) {
            adminCsrfToken = null;
            setAdminAuthenticated(false);
            throw new Error("Session expired or unauthorized. Please sign in again.");
        }

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        form.reset();
        setText(
            "application-registration-status",
            `Application registered successfully (ID: ${data.id}).`
        );

        await updateApplications();
    } catch (error) {
        setText(
            "application-registration-status",
            `Registration failed: ${error.message}`
        );
    } finally {
        submitButton.disabled = !adminCsrfToken;
        submitButton.textContent = "Register Application";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("application-form")
        .addEventListener("submit", handleApplicationRegistration);
});

// Restore an existing administrator session after a page refresh.
async function restoreAdminSession() {
    try {
        const response = await fetch("/api/auth/session", {
            method: "GET",
            credentials: "same-origin",
            headers: {
                Accept: "application/json",
            },
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (
            data.status !== "authenticated" ||
            typeof data.csrf_token !== "string" ||
            !data.csrf_token
        ) {
            throw new Error("Invalid session response");
        }

        adminCsrfToken = data.csrf_token;
        setAdminAuthenticated(true);
        setText("admin-auth-status", "Administrator session restored.");
    } catch (error) {
        adminCsrfToken = null;
        setAdminAuthenticated(false);
        setText("admin-auth-status", "Sign in to manage applications.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    restoreAdminSession();
});


// Periodically validate administrator authentication.
async function validateAdminSession() {
    if (!adminCsrfToken) return;

    try {
        const response = await fetch("/api/auth/session", {
            method: "GET",
            credentials: "same-origin",
            headers: { Accept: "application/json" },
            cache: "no-store",
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (
            data.status !== "authenticated" ||
            typeof data.csrf_token !== "string" ||
            !data.csrf_token
        ) {
            throw new Error("Invalid administrator session");
        }

        adminCsrfToken = data.csrf_token;
    } catch (error) {
        adminCsrfToken = null;
        setAdminAuthenticated(false);
        setText(
            "admin-auth-status",
            "Your session could not be verified. Please sign in again."
        );
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setInterval(validateAdminSession, 60000);
});
