**System Architecture Document (SAD)**
======================================

Product: LinkedIn Autonomous Engagement Agent
---------------------------------------------

Version: 1.0
------------

Owner: Ahsan Ali
----------------

Target Environment: Ubuntu Desktop
----------------------------------

Architecture Style: Modular, Stateful, Event-Driven Automation
--------------------------------------------------------------

1\. Introduction
----------------

### 1.1 Purpose

This document defines the **system architecture** of the LinkedIn Autonomous Engagement Agent. It describes:

*   High-level system structure
    
*   Core components and responsibilities
    
*   Data and control flows
    
*   State management
    
*   Failure handling
    
*   External integrations
    

This document is intended for:

*   Backend / automation engineers
    
*   Technical leads
    
*   Reviewers responsible for safety and reliability
    

### 1.2 Scope

The architecture covers:

*   Browser automation via Playwright
    
*   Scheduling and rate limiting
    
*   Human-like interaction orchestration
    
*   CAPTCHA detection and safe shutdown
    
*   External service integrations (ChatGPT, Google Sheets, Email)
    

Out of scope:

*   CAPTCHA solving
    
*   Multi-account orchestration
    
*   Proxy/fingerprint evasion
    
*   UI dashboards
    

2\. Architectural Overview
--------------------------

### 2.1 High-Level Architecture

The system is a **single-agent, stateful automation engine** running continuously on a user-controlled Ubuntu Desktop machine.

It follows a **layered modular architecture**:

*   **Configuration Layer** – Controls behavior
    
*   **Core Control Layer** – Scheduler, rate limits, state
    
*   **Automation Layer** – Playwright-driven LinkedIn actions
    
*   **Integration Layer** – ChatGPT, Google Sheets, Email
    
*   **Observability Layer** – Logging and alerts
    

### 2.2 High-Level Component Diagram (Logical)

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   +---------------------+  |   Configuration     |  |     (config.py)     |  +----------+----------+             |  +----------v----------+  |   Orchestrator      |  |      (main.js)      |  +----------+----------+             |  +----------v-------------------------------+  |            Core Services                 |  |  Scheduler | RateLimiter | StateManager  |  +-----+-------------+----------------------+        |             |  +-----v-----+   +---v------------------+  | Playwright|   | CAPTCHA Detector     |  |  Browser  |   +----------------------+  +-----+-----+        |  +-----v----------------------------------+  |           Automation Actions           |  | Feed | Search | Profile | Connect     |  +-----+----------------------------------+        |  +-----v----------------------------------+  |         External Integrations          |  | ChatGPT | Google Sheets | Email        |  +----------------------------------------+   `

3\. Architectural Style & Rationale
-----------------------------------

### 3.1 Style

*   **Stateful automation agent**
    
*   **Event-driven stop conditions**
    
*   **Config-driven behavior**
    
*   **Fail-fast on risk**
    

### 3.2 Rationale

LinkedIn automation requires:

*   Long-lived session trust
    
*   Predictable behavior
    
*   Conservative error handling
    

Stateless or distributed approaches were explicitly rejected.

4\. Component Breakdown
-----------------------

4.1 Configuration Layer
-----------------------

### Component

config/config.py

### Responsibility

*   Centralized control of all system behavior
    
*   Feature toggles
    
*   Safety limits
    
*   Timing constraints
    

### Characteristics

*   Loaded at startup
    
*   Read-only at runtime
    
*   Single source of truth
    

4.2 Orchestrator Layer
----------------------

### Component

main.js

### Responsibility

*   System bootstrapping
    
*   Module coordination
    
*   Main execution loop
    
*   Graceful shutdown
    

### Key Functions

*   Load config & state
    
*   Start browser
    
*   Enforce scheduler
    
*   Call action modules
    
*   Handle stop signals
    

This component **contains no business logic**.

4.3 Core Services Layer
-----------------------

### 4.3.1 Scheduler

**Purpose**

*   Enforces daily active hours
    
*   Controls idle vs active behavior
    

**Inputs**

*   System clock
    
*   Configured time windows
    

**Outputs**

*   Permission to execute actions
    
*   Sleep commands
    

### 4.3.2 Rate Limiter

**Purpose**

*   Prevents excessive actions
    
*   Enforces daily caps
    

**Tracked Counters**

*   Likes
    
*   Profile visits
    
*   Connection requests
    

**Persistence**

*   Stored in local state
    

### 4.3.3 State Manager

**Purpose**

*   Persistent memory
    
*   Crash recovery
    
*   Daily reset tracking
    

**Stored Data**

*   Counters
    
*   Progress indices
    
*   System status
    
*   Last action timestamp
    

4.4 Browser Automation Layer
----------------------------

### Component

core/browser.js

### Technology

*   Playwright (Chromium)
    
*   Persistent browser context
    

### Responsibility

*   Launch and manage browser
    
*   Provide page context
    
*   Ensure session continuity
    

### Constraints

*   Visible browser only
    
*   Single context
    
*   No cookie manipulation
    

4.5 Automation Actions Layer
----------------------------

Each action module performs **one type of user behavior**.

### 4.5.1 Feed Actions

**Responsibilities**

*   Scroll feed
    
*   Like posts
    
*   Simulate reading behavior
    

**Constraints**

*   Non-deterministic
    
*   Rate-limited
    
*   Delay-enforced
    

### 4.5.2 People Search

**Responsibilities**

*   Execute keyword-based searches
    
*   Apply filters (People, Location)
    

**Input**

*   searchpeople.txt
    

### 4.5.3 Profile Actions

**Responsibilities**

*   Visit profile pages
    
*   Scroll sections
    
*   Extract visible data
    

### 4.5.4 Connection Actions

**Responsibilities**

*   Initiate connection request
    
*   Insert generated note
    
*   Send invitation
    

4.6 CAPTCHA Detection Layer
---------------------------

### Component

core/captchaDetector.js

### Responsibility

*   Detect LinkedIn security challenges
    
*   Immediately halt automation
    
*   Trigger alerts (if enabled)
    

### Detection Signals

*   /checkpoint/ URLs
    
*   CAPTCHA iframes
    
*   Security verification text
    
*   Page interaction lock
    

### Behavior

*   Fail-fast
    
*   No retries
    
*   No bypass attempts
    

4.7 External Integration Layer
------------------------------

### 4.7.1 ChatGPT Integration

**Purpose**

*   Generate personalized connection notes
    

**Characteristics**

*   Optional
    
*   Non-blocking
    
*   Failure-safe (skip note)
    

### 4.7.2 Google Sheets Integration

**Purpose**

*   External audit log
    
*   Long-term record storage
    

**Design**

*   Write locally first
    
*   Batch synchronization
    
*   Retry on failure
    

### 4.7.3 Email Notification System

**Purpose**

*   Alert operator on critical failures
    

**Triggers**

*   CAPTCHA detection
    
*   Fatal crashes
    
*   Restart loops
    

**Controlled By**

*   Config flags
    

4.8 Observability Layer
-----------------------

### Logging

*   Terminal logs
    
*   File logs
    
*   Timestamped
    
*   Leveled (INFO/WARN/ERROR/FATAL)
    

### Alerts

*   Email-based
    
*   Only for critical events
    
*   Never for routine behavior
    

5\. Data Flow Architecture
--------------------------

### 5.1 Primary Data Flows

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   User Config → Orchestrator  State → RateLimiter → Actions  Actions → State Manager  Actions → Google Sheets (async)  Profile Data → ChatGPT → Note  Errors → CAPTCHA Detector → Shutdown   `

6\. Control Flow
----------------

### 6.1 Normal Operation

1.  Startup
    
2.  Check scheduler
    
3.  Perform feed actions
    
4.  Execute people search
    
5.  Visit profiles
    
6.  Send connections
    
7.  Persist state
    
8.  Take break
    
9.  Loop
    

### 6.2 CAPTCHA Flow

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   Action →  CAPTCHA Detected →  State Saved →  Browser Closed →  Status = BLOCKED →  (Optional Email) →  System Idle   `

7\. State Management Architecture
---------------------------------

### States

*   INIT
    
*   RUNNING
    
*   IDLE
    
*   SLEEPING
    
*   RATE\_LIMIT\_REACHED
    
*   BLOCKED\_BY\_CAPTCHA
    
*   ERROR\_FATAL
    

### State Transitions

*   Strictly controlled
    
*   No automatic recovery from CAPTCHA
    

8\. Failure Handling Strategy
-----------------------------

FailureResponseCAPTCHAImmediate haltRate limitIdleCrashPM2 restartSheets failureLocal cacheChatGPT failureSkip note

9\. Security Architecture
-------------------------

### Key Principles

*   No credential storage
    
*   No API abuse
    
*   No stealth techniques
    
*   Manual authentication required
    

### Threat Model

*   Account restriction
    
*   Data leakage
    
*   Uncontrolled automation
    

Mitigated via:

*   Conservative behavior
    
*   Fail-fast design
    
*   Operator control
    

10\. Deployment Architecture
----------------------------

### Runtime

*   Ubuntu Desktop
    
*   Single-node
    
*   PM2 managed
    

### Startup

*   Manual or systemd
    
*   User session required
    

11\. Architectural Constraints
------------------------------

*   Single account only
    
*   Single browser context
    
*   Human-like speed only
    
*   Operator must intervene on CAPTCHA
    

12\. Architecture Decision Records (ADR Summary)
------------------------------------------------

DecisionReasonPlaywrightStability & controlPersistent browserTrust continuityNo LinkedIn APINot permittedFail-fast CAPTCHAAccount safetyConfig-drivenOperational safety

13\. Conclusion
---------------

This architecture prioritizes:

*   **Safety**
    
*   **Longevity**
    
*   **Transparency**
    
*   **Human realism**
    

It is designed to be **maintainable**, **auditable**, and **safe for long-term operation**, not aggressive growth.

If you want next, I can:

*   Produce a **State Machine Diagram (Mermaid / UML)**
    
*   Create **Architecture diagrams**
    
*   Write **ADR documents**
    
*   Generate **runbook & ops docs**
    

Just tell me which one to generate next.