# Project Proposal

## AI-Assisted Cloud Monitoring and Troubleshooting Dashboard

**Student:** Khalidou Bass  
**Course:** COMP 488 – Cloud Computing, DevOps, and AI  
**Instructor:** Gregor von Laszewski  
**Date:** October 2026
**Status:** Approved Project

## 1. Project Overview

The goal of this project is to develop an **AI-Assisted Cloud Monitoring and Troubleshooting Dashboard** that monitors a containerized web application, detects common operational issues, and uses AI to help explain possible causes and recommend troubleshooting actions.

The project combines cloud computing, DevOps, monitoring, containerization, automation, and AI into a practical system for understanding and responding to application incidents.

## 2. Proposed System

The system will follow this workflow:

1. Deploy a containerized web application to a cloud environment.
2. Monitor application performance and collect relevant metrics and logs.
3. Detect selected incidents, such as high CPU usage, container crashes, or application/deployment failures.
4. Use an AI component to analyze the available monitoring information and suggest possible causes.
5. Display alerts, AI-generated explanations, and recommended troubleshooting actions through a dashboard.

![Proposed System Architecture](../images/project-overview.png)

## 3. Technologies

The project is expected to use:

- **Python / Flask:** Sample web application and application logic.
- **Docker:** Application containerization.
- **Cloud Infrastructure:** Hosting and running the application.
- **Prometheus:** Metrics collection and monitoring.
- **Grafana:** Monitoring dashboards and visualization.
- **LLM:** AI-assisted incident analysis and troubleshooting recommendations.
- **GitHub / GitHub Actions / Makefile:** Version control, automation, testing, and deployment workflows.

The final cloud deployment environment and specific AI integration will be selected during implementation based on project requirements and available resources.

## 4. Expected Outcome

The expected outcome is a working prototype demonstrating how cloud monitoring and AI can work together to identify, analyze, and troubleshoot common application issues.

The prototype will demonstrate a basic end-to-end workflow:

**Application → Monitoring → Incident Detection → AI Analysis → Troubleshooting Recommendation**

The project will also provide practical experience with cloud deployment, containerization, monitoring, DevOps automation, and AI integration.

## 5. Project Scope

The primary goal is to complete a reliable end-to-end prototype rather than build a production-scale monitoring platform.

The core implementation will focus on:

- A containerized web application.
- Collection of application and system metrics.
- A monitoring dashboard.
- Detection or simulation of selected operational incidents.
- AI-assisted explanation of incidents.
- Recommended troubleshooting actions.

Advanced features such as automated remediation, additional monitoring sources, or more sophisticated incident analysis may be added if time permits.

## 6. Development Timeline

The project will be developed incrementally during the remainder of the semester.

The implementation will progress from the basic containerized application to monitoring and visualization, followed by incident detection and AI-assisted troubleshooting. The final stage will focus on integration, testing, documentation, and demonstration.
