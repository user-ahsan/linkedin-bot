**Developer Guide**
===================

LinkedIn Autonomous Engagement Agent
------------------------------------

1\. Purpose of This Guide
-------------------------

This document explains:

*   How the system is structured
    
*   How developers should implement each module
    
*   How Playwright should be used safely and robustly
    
*   How state, scheduling, rate limits, and alerts interact
    
*   How to debug, extend, and maintain the system
    

This is **not marketing documentation** — it is for **builders**.

2\. Core Engineering Principles
-------------------------------

Before touching code, every developer must understand these principles:

1.  **Human realism > speed**
    
2.  **Statefulness > stateless scripts**
    
3.  **Stop on risk, never push through**
    
4.  **Selectors must be resilient**
    
5.  **Everything must be observable**
    
6.  **Config controls behavior, not code edits**
    

3\. Technology Stack
--------------------

### Required

*   Ubuntu Desktop 22.04+
    
*   Node.js (LTS)
    
*   Playwright (Chromium)
    
*   PM2
    
*   Google Sheets API
    
*   SMTP (for email alerts)
    
*   ChatGPT API (note generation)
    

### Explicitly NOT Used

*   Headless browsers
    
*   Private LinkedIn APIs
    
*   DOM class-name scraping
    
*   CAPTCHA solvers
    
*   Fingerprint spoofing
    

4\. Project Structure (Developer View)
--------------------------------------

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   linkedin-bot/  │  ├── config/  │   └── config.py  │  ├── core/  │   ├── browser.js  │   ├── scheduler.js  │   ├── rateLimiter.js  │   ├── stateManager.js  │   ├── captchaDetector.js  │   ├── logger.js  │   └── notifier.js  │  ├── actions/  │   ├── feedActions.js  │   ├── searchPeople.js  │   ├── profileActions.js  │   ├── connectActions.js  │   └── noteGenerator.js  │  ├── storage/  │   ├── localState.json  │   ├── sheetsClient.js  │   └── batchSync.js  │  ├── inputs/  │   └── searchpeople.txt  │  └── main.js   `

Each folder has **one responsibility**.

5\. Bootstrapping the Application
---------------------------------

### Startup Flow

1.  Load configuration
    
2.  Load persisted state
    
3.  Validate system time & scheduler
    
4.  Launch Playwright with persistent profile
    
5.  Confirm LinkedIn login
    
6.  Enter main automation loop
    

### Important Rule

If LinkedIn is **not logged in**, the bot must **stop immediately**.

6\. Playwright Browser Management
---------------------------------

### Key Rules

*   Always use launchPersistentContext
    
*   Never clear cookies
    
*   Never open incognito contexts
    
*   Visible browser only
    
*   One tab maximum (unless explicitly needed)
    

### Why

LinkedIn heavily fingerprints session consistency.Persistent context = trust continuity.

7\. Selector Strategy (CRITICAL)
--------------------------------

### Selector Priority Order

1.  **ARIA labels**
    
2.  **Visible text**
    
3.  **Roles**
    
4.  **DOM hierarchy**
    
5.  **Index-based fallback (last resort)**
    

### Example Strategy (Conceptual)

Instead of:

*   .artdeco-button--primary
    

Use:

*   Button with text **“Connect”**
    
*   Button with aria-label containing **“Like”**
    
*   Button inside an article context
    

### Golden Rule

If a selector breaks after a LinkedIn UI update, it should be fixable **in one place**, not everywhere.

8\. Feed Interaction Module (Developer Notes)
---------------------------------------------

### Behavior Model

*   Scroll small distances
    
*   Pause randomly
    
*   Occasionally scroll upward
    
*   Like only after “reading”
    
*   Never like two posts back-to-back
    

### Developer Warning

Do **not** iterate posts mechanically.Treat the feed as **unpredictable content**, not a list.

9\. People Search Automation
----------------------------

### Developer Flow

1.  Navigate to **My Network**
    
2.  Input keyword from searchpeople.txt
    
3.  Click **People**
    
4.  Open **Location filter**
    
5.  Select **Pakistan**
    
6.  Close filter
    
7.  Scroll results
    

### Important

*   Filters must be applied **visibly**
    
*   Never manipulate URLs directly
    
*   Wait for results to stabilize before scrolling
    

10\. Profile Visit & Extraction
-------------------------------

### Required Actions Before Extraction

*   Scroll profile slowly
    
*   Open About section
    
*   Allow skills section to render
    
*   Pause before reading content
    

### Extract Only:

*   Name
    
*   Headline
    
*   About text
    
*   Skills (visible only)
    
*   Profile URL
    

### Never:

*   Scrape hidden elements
    
*   Expand beyond visible UI
    
*   Trigger “See more” aggressively
    

11\. ChatGPT Note Generation
----------------------------

### Developer Responsibilities

*   Sanitize extracted text
    
*   Enforce character limit
    
*   Enforce neutral tone
    
*   Handle API failures gracefully
    

### Failure Policy

If ChatGPT fails:

*   Log warning
    
*   Proceed with “Send without note”
    

12\. Connection Request Flow
----------------------------

### Supported Flows

*   **Connect → Add note → Send**
    
*   **Connect → Send without note**
    

### Guardrails

*   Never resend to same profile
    
*   Never retry failed requests
    
*   Stop when daily limit is reached
    

13\. Scheduler & Rate Limiter
-----------------------------

### Scheduler

*   Hard gatekeeper
    
*   No action allowed outside window
    
*   Overrides all modules
    

### Rate Limiter

*   Counts persist in localState.json
    
*   Reset daily
    
*   Enforced before every action
    

14\. CAPTCHA Detection (Safety-Critical)
----------------------------------------

### Detection Signals

*   URL includes /checkpoint/
    
*   CAPTCHA iframe detected
    
*   Security verification text
    
*   Page interaction freezes
    

### On Detection

1.  Log error
    
2.  Persist state
    
3.  Close browser
    
4.  Change status to BLOCKED\_BY\_CAPTCHA
    
5.  Trigger email alert **if enabled**
    

### Developer Rule

Never attempt recovery automatically.

15\. Email Notification System
------------------------------

### Controlled via Config

*   Global enable switch
    
*   CAPTCHA-specific toggle
    

### Used For

*   CAPTCHA detection
    
*   Fatal crashes
    
*   Repeated restarts
    
*   Data sync failures
    

### Not Used For

*   Rate limits
    
*   Normal idling
    
*   Expected pauses
    

16\. Google Sheets Integration
------------------------------

### Developer Guidance

*   Write locally first
    
*   Batch uploads every 4–5 hours
    
*   Retry failures
    
*   Never block automation loop on Sheets
    

### Sheets Are:

*   External memory
    
*   Audit trail
    
*   Not real-time dependencies
    

17\. Logging & Debugging
------------------------

### Logging Requirements

*   Every action logged
    
*   Include timestamp & module
    
*   Use log levels consistently
    

### Debugging Philosophy

If something goes wrong:

*   Logs should explain **what**, **where**, and **why**
    
*   Developer should not need to attach a debugger
    

18\. State Management
---------------------

### Stored State Includes

*   Counters
    
*   Last keyword index
    
*   Last profile index
    
*   CAPTCHA status
    
*   Last successful action
    

### Why

State enables:

*   Safe restarts
    
*   Crash recovery
    
*   Long-running reliability
    

19\. Process Management (PM2)
-----------------------------

### Expectations

*   Auto-restart on crash
    
*   No restart loops
    
*   Clean shutdowns
    
*   Logs preserved across restarts
    

20\. Developer Do / Don’t Summary
---------------------------------

### DO

*   Think like a cautious human
    
*   Log everything
    
*   Stop on risk
    
*   Respect limits
    
*   Use config flags
    

### DON’T

*   Speed things up
    
*   Hardcode selectors
    
*   Retry blocked actions
    
*   Hide failures
    
*   Assume UI stability
    

21\. Final Developer Note
-------------------------

This system is **closer to an autonomous agent** than a script.

If you treat it like a bot, it will fail.If you treat it like a **slow, forgetful human**, it will survive.

If you want next, I can:

*   Create a **state machine diagram**
    
*   Provide **Playwright selector patterns**
    
*   Write **pseudocode for main loop**
    
*   Design **testing & dry-run modes**
    

Just say the word.