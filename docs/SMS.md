📘 Software Modeling Specification (SMS)
========================================

1\. Document Purpose
--------------------

This Software Modeling Specification (SMS) defines the **logical, behavioral, and interaction models** of the LinkedIn Automation System.It provides a **clear mental model** of how the system behaves, transitions, and interacts with external services.

This document is intended for:

*   Backend automation engineers
    
*   QA engineers
    
*   System architects
    
*   DevOps engineers
    

2\. System Overview
-------------------

### System Name

**LinkedIn Human-like Automation Bot**

### Platform

*   Ubuntu Desktop (headful browser)
    
*   Python-based automation
    
*   Playwright Chromium
    
*   Google Sheets
    
*   LLM (for message generation)
    
*   Email notification system
    

### High-Level Objective

To continuously and safely automate LinkedIn feed engagement and connection workflows while:

*   Mimicking human behavior
    
*   Respecting rate limits
    
*   Persisting structured interaction data
    
*   Providing observability and control
    

3\. System Context Model
------------------------

### External Actors

ActorRoleUser (You)Configures system, monitors alertsLinkedIn Web AppAutomation targetGoogle Sheets APIData persistenceEmail SMTP ServerAlert notificationsLLM APIPersonalized note generationOS SchedulerDaily execution

### Context Diagram (Textual)

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   User   ├── config.py   ├── email alerts   └── logs  Automation System   ├── Playwright Engine   ├── State Machine   ├── Rate Limiter   ├── CAPTCHA Detector   ├── Scheduler   ├── Logger  External Systems   ├── LinkedIn Web UI   ├── Google Sheets   ├── Email SMTP   └── LLM API   `

4\. Functional Decomposition Model
----------------------------------

### Core Subsystems

1.  **Automation Orchestrator**
    
2.  **Playwright Interaction Engine**
    
3.  **Human Behavior Engine**
    
4.  **Rate Limiting Engine**
    
5.  **CAPTCHA Detection Engine**
    
6.  **Data Persistence Engine**
    
7.  **Notification Engine**
    
8.  **Scheduler Engine**
    
9.  **Configuration Engine**
    
10.  **Logging & Observability Engine**
    

5\. Behavioral Model (State Machine)
------------------------------------

### Global System States

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   [INIT]    ↓  [CONFIG_LOADED]    ↓  [BROWSER_READY]    ↓  [RUNNING]    ├── FEED_ENGAGEMENT    ├── NETWORK_SEARCH    ├── PROFILE_EXTRACTION    ├── NOTE_GENERATION    ├── CONNECTION_SENT    ↓  [SLEEPING]    ↓  [RUNNING]   `

### Exception States

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   [RUNNING]    ↓  [CAPTCHA_DETECTED]    ↓  [STOPPED_SAFELY]   ← email optional via config   `

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   [RUNNING]    ↓  [ERROR_FATAL]    ↓  [STOPPED]          ← email always   `

6\. Use Case Models
-------------------

### UC-01: Feed Engagement

**Primary Flow**

1.  Scroll feed randomly
    
2.  Detect post cards
    
3.  Like eligible posts
    
4.  Occasionally open comment box (optional)
    
5.  Log interaction
    

**Constraints**

*   Daily like limit
    
*   Random delays
    
*   Scroll jitter
    

### UC-02: Search & Filter People

**Primary Flow**

1.  Read searchpeople.txt
    
2.  Search LinkedIn
    
3.  Switch to People tab
    
4.  Apply location filter (Pakistan)
    
5.  Scroll results
    

### UC-03: Profile Data Extraction

**Primary Flow**

1.  Open profile
    
2.  Extract:
    
    *   Name
        
    *   Headline
        
    *   About
        
    *   Skills
        
    *   Profile URL
        
3.  Save temporarily
    
4.  Write to Google Sheet (Profile Requests Sent)
    

### UC-04: LLM Note Generation

**Primary Flow**

1.  Send profile + your profile summary to LLM
    
2.  Receive personalized note
    
3.  Validate length and tone
    
4.  Store note locally
    

### UC-05: Send Connection Request

**Primary Flow**

1.  Click Connect
    
2.  Click “Add a note”
    
3.  Paste generated note
    
4.  Send request
    
5.  Update counters
    
6.  Persist data
    

7\. Interaction Model (Playwright Targeting)
--------------------------------------------

### Selector Strategy Model

**Priority Order**

1.  data-control-name
    
2.  aria-label
    
3.  role-based selectors
    
4.  text-based selectors (fallback)
    
5.  XPath (last resort)
    

### Example Interaction Flow

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   Page Loaded   ↓  Wait for network idle   ↓  Find button[data-control-name="connect"]   ↓  Hover   ↓  Click   ↓  Wait popup   ↓  Fill textarea   ↓  Send   `

8\. Data Model
--------------

### Google Sheets Structure

#### Sheet 1: interactions

Columntimestampaction\_typetargetstatussession\_id

#### Sheet 2: profile\_requests\_sent

Columntimestampprofile\_nameheadlineaboutskillsprofile\_urlgenerated\_notestatus

9\. Configuration Model
-----------------------

### Configuration File: config.py

Controls:

*   Email alerts (on/off)
    
*   CAPTCHA email toggle
    
*   Rate limits
    
*   Delays
    
*   Max daily actions
    
*   Headful / headless mode
    
*   Scheduler timing
    

### Config Dependency Model

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   All Modules     ↑  config.py   `

10\. Notification Model
-----------------------

### Email Notification Rules

EventEmailFatal error✅CAPTCHA detected✅ (config toggle)Rate limit reached❌Normal stop❌Restart loop✅

11\. Logging & Observability Model
----------------------------------

### Terminal Logging Levels

*   \[BOOT\]
    
*   \[NAV\]
    
*   \[ACTION\]
    
*   \[WAIT\]
    
*   \[DATA\]
    
*   \[STATE\]
    
*   \[ERROR\]
    
*   \[CAPTCHA\]
    

Each action emits a log node with:

*   Timestamp
    
*   Module
    
*   Action
    
*   Outcome
    

12\. Scheduling Model
---------------------

### Daily Scheduler

*   OS-level (cron / systemd)
    
*   Randomized start window
    
*   Auto sleep cycles
    
*   Persistent counters reset daily
    

13\. Security & Risk Model
--------------------------

### Risk Controls

*   Human-like delays
    
*   Randomized navigation
    
*   Hard stop on CAPTCHA
    
*   No CAPTCHA bypass
    
*   No aggressive retries
    
*   Session persistence
    

14\. Non-Functional Requirements (Mapped)
-----------------------------------------

CategoryRequirementReliabilityGraceful stop on blockScalabilitySingle-account safeMaintainabilityModular architectureObservabilityFull terminal + logsConfigurabilityCentral configSafetyCAPTCHA-aware

15\. Handover Readiness Checklist
---------------------------------

This SMS supports:

*   Architecture review
    
*   QA test case creation
    
*   Dev onboarding
    
*   Security review
    
*   Future scaling discussions