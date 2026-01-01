PHASE 1 — Environment & Foundations
-----------------------------------

### Objective

Create a **stable Ubuntu automation environment**.

### Tasks

*   Install system dependencies:
    
    *   Python 3.10+
        
    *   Playwright + Chromium
        
    *   Fonts, video codecs
        
*   Setup Python virtual environment
    
*   Install core libraries:
    
    *   playwright
        
    *   google-api-python-client
        
    *   gspread
        
    *   requests
        
    *   dotenv
        
*   Create folder structure
    

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   /bot   ├── core/   ├── playwright/   ├── sheets/   ├── llm/   ├── notifier/   ├── scheduler/   ├── utils/   ├── config.py   └── main.py   `

### Deliverables

*   Environment setup doc
    
*   Working Playwright browser launch
    
*   Config file stub
    

### Exit Criteria

✔ Browser opens LinkedIn manually✔ Script runs without error

PHASE 2 — Configuration & Control Layer
---------------------------------------

### Objective

Centralize **all behavior control**.

### Tasks

*   Implement config.py
    
*   Add toggles:
    
    *   Email alerts on/off
        
    *   CAPTCHA email on/off
        
    *   Max daily actions
        
    *   Rate limits
        
*   Add runtime flags
    
*   Validate config on startup
    

### Deliverables

*   Config schema
    
*   Validation logic
    
*   Sample config file
    

### Exit Criteria

✔ Changing config alters behavior✔ No hard-coded values elsewhere

PHASE 3 — Logging, States & Observability
-----------------------------------------

### Objective

Make every action **visible and traceable**.

### Tasks

*   Implement terminal log system
    
*   Define log levels:
    
    *   BOOT, NAV, ACTION, DATA, STATE, ERROR
        
*   Implement global state manager:
    
    *   RUNNING
        
    *   SLEEPING
        
    *   CAPTCHA\_DETECTED
        
    *   STOPPED
        
*   Persist state to disk
    

### Deliverables

*   Log formatter
    
*   State persistence file
    
*   Action counters
    

### Exit Criteria

✔ Every click logs output✔ System resumes safely after crash

PHASE 4 — Playwright Core Engine
--------------------------------

### Objective

Build **robust browser control**.

### Tasks

*   Implement browser context
    
*   Persistent session (cookies)
    
*   Human mouse movement
    
*   Scroll behavior engine
    
*   Safe click wrapper:
    
    *   Wait
        
    *   Hover
        
    *   Click
        
    *   Confirm result
        

### Deliverables

*   browser\_manager.py
    
*   human\_actions.py
    

### Exit Criteria

✔ No brittle selectors✔ Natural scrolling behavior

PHASE 5 — Feed Engagement Automation
------------------------------------

### Objective

Simulate **real LinkedIn feed usage**.

### Tasks

*   Scroll feed randomly
    
*   Detect post cards
    
*   Like posts probabilistically
    
*   Optional comment click (no submit)
    
*   Track engagement count
    

### Deliverables

*   Feed interaction module
    
*   Interaction logs
    
*   Google Sheet integration (Sheet 1)
    

### Exit Criteria

✔ Likes look human✔ No rapid consecutive actions

PHASE 6 — Search & Network Automation
-------------------------------------

### Objective

Automate **people discovery safely**.

### Tasks

*   Read searchpeople.txt
    
*   Perform search
    
*   Switch to People tab
    
*   Apply location filter (Pakistan)
    
*   Scroll results with delays
    

### Deliverables

*   Network search module
    
*   Filter validation logic
    

### Exit Criteria

✔ Filters applied correctly✔ No infinite scrolling loops

PHASE 7 — Profile Extraction Engine
-----------------------------------

### Objective

Extract **structured profile data**.

### Tasks

*   Open profile safely
    
*   Extract:
    
    *   Name
        
    *   Headline
        
    *   About
        
    *   Skills
        
    *   URL
        
*   Handle missing sections
    
*   Cache locally
    

### Deliverables

*   Profile parser
    
*   Validation rules
    
*   Local persistence
    

### Exit Criteria

✔ No crashes on partial profiles✔ Clean structured output

PHASE 8 — LLM Integration (Note Generation)
-------------------------------------------

### Objective

Generate **context-aware connection notes**.

### Tasks

*   Build LLM prompt template
    
*   Inject:
    
    *   Profile data
        
    *   Your profile
        
*   Enforce:
    
    *   Max character count
        
    *   Professional tone
        
*   Store response
    

### Deliverables

*   Prompt template
    
*   LLM adapter
    
*   Fallback handling
    

### Exit Criteria

✔ Notes look human✔ No repeated messages

PHASE 9 — Connection Request Automation
---------------------------------------

### Objective

Send **safe, personalized connection requests**.

### Tasks

*   Detect Connect button
    
*   Handle:
    
    *   “Follow” vs “Connect”
        
    *   “Add note” popup
        
*   Paste generated note
    
*   Send request
    
*   Update Sheet 2
    

### Deliverables

*   Connect workflow module
    
*   Success/failure tracking
    

### Exit Criteria

✔ No duplicate requests✔ Data persisted correctly

PHASE 10 — CAPTCHA & Safety Controls
------------------------------------

### Objective

Protect the account.

### Tasks

*   Detect CAPTCHA patterns
    
*   Immediate stop
    
*   Save state
    
*   Trigger email **only if enabled**
    
*   Lock automation
    

### Deliverables

*   CAPTCHA detector
    
*   Safe shutdown handler
    

### Exit Criteria

✔ Zero retry after CAPTCHA✔ No account lock escalation

PHASE 11 — Scheduler & Rate Limiting
------------------------------------

### Objective

Make the bot **long-running and safe**.

### Tasks

*   Daily scheduler (cron/systemd)
    
*   Randomized start time
    
*   Hourly sleep cycles
    
*   Reset counters daily
    

### Deliverables

*   Scheduler config
    
*   Rate limit engine
    

### Exit Criteria

✔ Runs for weeks without manual input✔ Respects limits

PHASE 12 — Notifications & Alerts
---------------------------------

### Objective

Inform **only when necessary**.

### Tasks

*   Email on:
    
    *   Fatal crash
        
    *   CAPTCHA (config-controlled)
        
*   No spam
    
*   Clear subject + logs
    

### Deliverables

*   Email templates
    
*   Alert routing logic
    

### Exit Criteria

✔ Useful alerts only✔ No alert fatigue

PHASE 13 — QA, Hardening & Handover
-----------------------------------

### Objective

Prepare for **team ownership**.

### Tasks

*   Dry-run testing
    
*   Selector break testing
    
*   LinkedIn UI change simulation
    
*   Documentation finalization
    

### Deliverables

*   Test cases
    
*   Known risk list
    
*   Onboarding guide
    

### Exit Criteria

✔ Team can run without you✔ System stable