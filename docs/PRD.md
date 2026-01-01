**Product Requirements Document (PRD)**
=======================================

**Product Name:** LinkedIn Autonomous Engagement Agent
------------------------------------------------------

**Version:** 1.0
----------------

**Owner:** Ahsan Ali
--------------------

**Platform:** Ubuntu Desktop
----------------------------

**Status:** Definition Complete
-------------------------------

1\. Executive Summary
---------------------

The **LinkedIn Autonomous Engagement Agent** is a long-running, human-behavior-driven automation system designed to operate on a real Ubuntu Desktop environment. It simulates organic LinkedIn usage—scrolling, liking posts, searching people, visiting profiles, and sending connection requests with personalized notes—while maintaining strict safety controls, rate limits, state persistence, and observability.

The product is **not designed to aggressively automate LinkedIn**, but to behave as a cautious, distracted human user over long periods, minimizing detection risk while maximizing consistent engagement.

2\. Goals & Non-Goals
---------------------

### 2.1 Goals

*   Maintain **24/7 availability** with scheduled active hours
    
*   Simulate **realistic human interaction patterns**
    
*   Automate **people discovery and connection requests**
    
*   Generate **personalized connection notes** via ChatGPT
    
*   Persist all interactions in **Google Sheets**
    
*   Provide **full terminal observability**
    
*   Allow **configuration-driven behavior control**
    
*   Detect CAPTCHA / restrictions and **safely halt**
    
*   Optionally notify operator via **email alerts**
    

### 2.2 Non-Goals

*   ❌ Bypassing CAPTCHA or LinkedIn security
    
*   ❌ Mass outreach or spam behavior
    
*   ❌ Using private or reverse-engineered LinkedIn APIs
    
*   ❌ Headless or fingerprint-evasive browsing
    
*   ❌ Multiple account management
    

3\. Target Users
----------------

*   Individual developers
    
*   Founders
    
*   Job seekers
    
*   Solo operators running one LinkedIn account
    
*   Users comfortable with Ubuntu & terminal environments
    

4\. Operating Environment
-------------------------

### 4.1 OS

*   Ubuntu Desktop 22.04 / 24.04
    

### 4.2 Runtime

*   Node.js
    
*   Playwright (Chromium)
    
*   PM2 (process manager)
    

### 4.3 Browser Mode

*   **Visible browser (non-headless)**
    
*   Persistent user profile
    
*   Manual login required once
    

5\. High-Level Architecture
---------------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   ┌────────────┐  │   Config   │◄──────────────┐  └─────┬──────┘               │        │                      │  ┌─────▼──────┐     ┌─────────▼─────────┐  │  Scheduler │     │  Rate Limiter     │  └─────┬──────┘     └─────────┬─────────┘        │                      │  ┌─────▼──────────────────────▼──────┐  │         Automation Engine           │  │  (Playwright Orchestrator)          │  └─────┬───────────┬───────────┬─────┘        │           │           │   Feed Actions  Search People  Profile Actions        │           │           │  ┌─────▼──────┐ ┌──▼────────┐ ┌▼─────────────┐  │ CAPTCHA    │ │ ChatGPT   │ │ Google Sheets │  │ Detector   │ │ Note Gen  │ │ Sync          │  └─────┬──────┘ └───────────┘ └─────┬─────────┘        │                              │  ┌─────▼────────┐              ┌─────▼──────┐  │ Email Alerts │              │ Local State │  └──────────────┘              └────────────┘   `

6\. Core Functional Requirements
--------------------------------

6.1 Scheduler
-------------

### Description

Controls when the automation is allowed to perform actions.

### Requirements

*   Configurable daily active window (e.g. 09:00–18:00)
    
*   Hard stop outside active hours
    
*   Randomized short breaks (2–10 min)
    
*   Randomized long breaks (20–45 min)
    
*   Night-time sleep enforced
    

### Acceptance Criteria

*   No LinkedIn actions outside allowed hours
    
*   Scheduler overrides all modules
    

6.2 Rate Limiter
----------------

### Description

Ensures safe daily activity limits.

### Limits (configurable)

ActionMax / DayLikes40–50Profile Visits30–40Connections10–15

### Behavior

*   Persistent across restarts
    
*   Reset daily
    
*   If limit reached → action disabled for the day
    

6.3 Feed Interaction Module
---------------------------

### Actions

*   Scroll feed
    
*   Pause randomly
    
*   Scroll up occasionally
    
*   Like posts
    
*   Open posts
    
*   Click “Show more” text
    
*   Optionally open comments
    

### Constraints

*   Likes must be spread out
    
*   Never like consecutive posts rapidly
    
*   Idle time required between actions
    

6.4 People Search & Filtering
-----------------------------

### Input

*   searchpeople.txt
    
*   Comma-separated search terms
    

### Flow

1.  Go to **My Network**
    
2.  Enter search keyword
    
3.  Click **People**
    
4.  Open **Location filter**
    
5.  Select **Pakistan**
    
6.  Close dropdown
    
7.  Scroll results list
    

6.5 Profile Visit & Data Extraction
-----------------------------------

### Extracted Fields

*   Full Name
    
*   Headline
    
*   About section
    
*   Skills (visible)
    
*   Profile URL
    

### Constraints

*   Must scroll profile naturally
    
*   Must open sections before extracting
    
*   Data stored locally first
    

6.6 ChatGPT Connection Note Generator
-------------------------------------

### Input

*   Extracted profile data
    
*   Operator’s own profile summary (static)
    

### Output

*   Short professional LinkedIn invite note
    
*   ≤300 characters
    
*   No emojis
    
*   No sales tone
    

### Failure Handling

*   If ChatGPT fails → send invite without note
    

6.7 Connection Request Module
-----------------------------

### Flow

1.  Click **Connect**
    
2.  If popup appears:
    
    *   Click **Add a note**
        
    *   Paste generated note
        
3.  Else:
    
    *   Click **Send without a note**
        
4.  Log result
    

### Constraints

*   Never resend to same profile
    
*   Never exceed daily limit
    

6.8 CAPTCHA & Restriction Detection
-----------------------------------

### Detection Signals

*   /checkpoint/ in URL
    
*   CAPTCHA iframe detected
    
*   “Verify you’re human” text
    
*   Security challenge messages
    

### Behavior

1.  Immediately stop automation
    
2.  Save local state
    
3.  Mark status as BLOCKED\_BY\_CAPTCHA
    
4.  Close browser
    
5.  If enabled → send email alert
    

### Non-Goals

*   No CAPTCHA bypass
    
*   No retries
    

6.9 Email Notification System
-----------------------------

### Config-Driven

*   Master enable/disable switch
    
*   CAPTCHA-specific toggle
    

### Email Triggers

*   CAPTCHA detection
    
*   Fatal crash
    
*   Continuous restart loop
    
*   Google Sheets sync failure
    

### Email Content

*   Reason
    
*   Timestamp
    
*   Last action
    
*   Manual intervention required
    

6.10 Google Sheets Integration
------------------------------

### Sheet 1: interactions

| timestamp | action | target | status |

### Sheet 2: profile\_requests\_sent

| name | headline | about | skills | url | note | time |

### Behavior

*   Write locally first
    
*   Batch sync every 4–5 hours
    
*   Retry on failure
    

6.11 Local State Persistence
----------------------------

Stored in local\_state.json

Includes:

*   Counters
    
*   Last keyword
    
*   Last profile index
    
*   Blocked status
    
*   Daily reset timestamp
    

6.12 Logging & Observability
----------------------------

### Terminal Logs

*   Every action logged
    
*   Color-coded levels
    
*   Timestamped
    
*   Human-readable
    

### Log Levels

*   INFO
    
*   WARN
    
*   ERROR
    
*   FATAL
    

7\. Configuration System
------------------------

All behavior controlled via config.py:

*   Scheduler
    
*   Limits
    
*   Email alerts
    
*   Delays
    
*   Feature toggles
    

Single-point control for safety.

8\. Failure & Recovery Strategy
-------------------------------

ScenarioActionCAPTCHAStop + optional emailRate limit hitIdleCrashPM2 restartSheets downLocal cacheChatGPT downNo note

9\. Security & Safety Considerations
------------------------------------

*   No credential storage
    
*   No API abuse
    
*   No fingerprint spoofing
    
*   Manual login required
    
*   Human-paced actions only
    

10\. Success Metrics
--------------------

*   Days without CAPTCHA
    
*   Connection acceptance rate
    
*   Zero manual intervention days
    
*   Consistent daily operation
    
*   No LinkedIn account warnings
    

11\. Future Enhancements (Out of Scope)
---------------------------------------

*   Multi-account support
    
*   Proxy rotation
    
*   UI dashboard
    
*   Mobile emulation
    
*   Smart audience scoring
    

12\. Final Notes
----------------

This product is designed as a **long-term autonomous assistant**, not a growth hack.

**Stability, safety, and realism override speed.**

If you want next:

*   **State machine diagram**
    
*   **Exact Playwright selectors**
    
*   **PM2 + Ubuntu autostart setup**
    
*   **Security hardening checklist**
    

Just tell me.