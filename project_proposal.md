
# Project Proposal (Draft)

## AI-Assisted Cloud Monitoring and Troubleshooting Dashboard

**Student:** Khalidou Bass  
**Course:** COMP 488 – Cloud Computing, DevOps, and AI  
**Instructor:** Gregor von Laszewski  
**Date:** September 2026  
**Status:** Initial idea – open to feedback and refinement

## 1. Project Overview

This is an initial project idea that came to mind while exploring possible topics for the course. I am still considering other ideas, but for now, I would like to explore developing an **AI-Assisted Cloud Monitoring and Troubleshooting Dashboard**.

The goal is to build a simple cloud-based application that monitors a containerized web application, detects common operational issues, and uses AI to help explain possible causes and recommend troubleshooting actions.

The project would combine cloud computing, DevOps, monitoring, and AI into a practical system for understanding and responding to application incidents.

## 2. Proposed System

The system would follow a simple workflow:

1. Deploy a containerized web application to a cloud environment.
2. Monitor application performance and collect relevant logs.
3. Detect selected incidents, such as high CPU usage, container crashes, or failed deployments.
4. Use an AI component to analyze the available information and suggest possible causes.
5. Display alerts, explanations, and recommended actions through a dashboard.

![Proposed System Architecture](images/project-overview.png)

## 3. Proposed Technologies

The technologies I am considering include:

- **Python / Flask:** Sample web application and analysis logic.
- **Docker:** Application containerization.
- **Cloud Infrastructure:** Hosting and managing the application.
- **Prometheus and Grafana:** Monitoring and visualization.
- **LLM:** AI-assisted incident analysis and troubleshooting.
- **GitHub / GitHub Actions / Makefile:** Version control and deployment automation.

The specific cloud provider and final technology stack have not yet been decided.

## 4. Expected Outcome

The expected outcome is a working prototype demonstrating how cloud monitoring tools and AI can work together to detect, analyze, and troubleshoot common application issues.

The project would also provide hands-on experience with cloud deployment, containerization, monitoring, automation, and AI integration.

## 5. Tentative Timeline

I expect to have approximately **6–8 weeks** to develop and demonstrate the project.

The initial focus would be on a small working prototype. Additional features, such as automated remediation or more advanced monitoring, could be considered if time permits.

---

**Note:** This is my current project idea, and I am still exploring other possibilities. I would appreciate any feedback or suggestions on this direction.