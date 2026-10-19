# COMP 488 — Instructor Feedback and Development Plan

**Date:** October 15, 2026  
**Project:** AI-Assisted Cloud Monitoring & Troubleshooting Dashboard  
**Context:** Intermediate project presentation

## 1. Overview

This document summarizes feedback received during the intermediate project presentation and identifies possible improvements for the next development phase.

Some points are interpretations of the discussion and require further investigation rather than immediate implementation.

## 2. Container Management — OrbStack

The instructor suggested exploring an alternative to Docker Desktop, possibly OrbStack.

### Action Items
- Investigate OrbStack and its Docker Compose compatibility.
- Compare container management, resource usage, and ease of development.
- Keep the existing Docker Compose environment operational.
- Treat migration as optional.

## 3. Monitoring — Push vs. Pull

The instructor raised the issue of monitoring latency, particularly the delay between an application failure and its detection.

The current system uses Prometheus pull-based monitoring with a five-second scrape interval.

However, scrape intervals, alert evaluation intervals, and alert `for` durations all affect when an alert becomes available.

### Action Items
- Document pull-based monitoring and its limitations.
- Investigate push-based or event-driven monitoring.
- Explain why an application that crashes cannot reliably report its own failure.
- Consider independent failure detection through container events or an external supervisor.
- Compare detection latency and notification latency.
- Implementation of an alternative monitoring approach is not required at this stage.

## 4. Timers, StopWatch, and Results Database

The instructor discussed timing measurements and a StopWatch example, possibly suggesting that experimental results could be stored for later comparison.

This interpretation requires confirmation.

### Potential Measurements
- Application failure detection latency.
- Alert firing latency.
- Incident API response time.
- LLM analysis duration.
- Container startup time.
- Notification delivery latency, if notifications are implemented.

### Action Items
- Investigate StopWatch-style timing measurements.
- Define repeatable experiments.
- Record timestamps, durations, and execution status.
- Evaluate storing results in CSV, SQLite, or PostgreSQL.
- Compare results across repeated experiments.

Prometheus already provides time-series storage. A separate database should only be introduced if there is a clear requirement for structured experiment or incident records.

## 5. LLM Integration — Local vs. Hosted

The instructor asked about the implications of using a locally hosted or externally hosted LLM.

### Action Items
- Compare local and hosted model deployment.
- Evaluate computational requirements, latency, cost, and privacy.
- Consider a provider-independent integration design.
- Start with structured incident data rather than unrestricted raw logs.
- Measure the response time of the selected approach.

## 6. Security and Log Protection

The instructor emphasized the importance of protecting sensitive information when integrating an LLM.

### Security Considerations
- Avoid exposing API keys, credentials, tokens, or personal information.
- Minimize the amount of log data sent to external services.
- Apply access controls to incident and log endpoints.
- Treat application logs as untrusted input.
- Consider prompt-injection risks.
- Do not allow an LLM to execute troubleshooting commands automatically.
- Review retention policies and access to stored incident data.

## 7. Lima — Removed from Required Scope

The instructor clarified that Lima is not necessary for this project because related work has already been completed through the Cloudmesh AI VM project.

### Decision
- Remove Lima from required project milestones.
- Continue using the existing Docker Compose environment.
- Explore OrbStack separately.
- Consider other cloud deployment environments only if time and project requirements justify them.

## 8. Proposed Priorities

### Priority 1 — Documentation and Design
- Document monitoring latency and push-versus-pull trade-offs.
- Compare local and hosted LLM security considerations.
- Update the project roadmap to remove Lima.
- Investigate OrbStack.

### Priority 2 — Experiments and Evaluation
- Validate Prometheus alert firing.
- Measure failure detection and alert latency.
- Record experimental results.
- Determine whether a separate results database is useful.

### Priority 3 — Implementation
- Integrate an LLM for incident explanation.
- Implement safeguards for sensitive incident data.
- Test and evaluate explanation quality and latency.

### Optional Extensions
- Alternative container runtime.
- Additional cloud deployment.
- Persistent incident history.
- Mobile interface.

## 9. Current Verified Progress

As of October 15, 2026:

- Flask, Prometheus, and Grafana containers are running.
- Prometheus is configured to scrape application metrics.
- Grafana monitoring dashboard is implemented.
- ApplicationDown and HighErrorRate alert rules are configured.
- Incident API and rule-based troubleshooting are implemented.
- Eight automated tests passed.
- LLM-powered troubleshooting remains planned.
- Controlled validation of alert firing remains to be completed.

## 10. Notes

This document records instructor feedback and proposed follow-up work. It does not establish every exploratory suggestion as a mandatory project requirement.
