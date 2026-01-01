**Developer-ready blueprint** of the entire system with:

*   **File-by-file responsibility**
    
*   **List of imports per file**
    
*   **Public functions per file**
    
*   **Pseudocode (not full code, but implementable)**
    
*   **Clear data flow between modules**
    

1️⃣ config/config.py
====================

### Responsibility

Single source of truth for **all behavior switches, limits, timings, alerts**.

### Imports

*   none (pure config)
    

### Exposed Objects

*   CONFIG
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   CONFIG = {    ENABLE_AUTOMATION: true,    ENABLE_EMAIL_ALERTS: true,    EMAIL_ON_CAPTCHA: true,    BROWSER: {      HEADLESS: false,      USER_DATA_DIR: "./browser_profile"    },    SCHEDULER: {      START_HOUR: 9,      END_HOUR: 18    },    LIMITS: {      LIKES_PER_DAY: 45,      PROFILE_VISITS_PER_DAY: 35,      CONNECTIONS_PER_DAY: 12    },    DELAYS: {      ACTION_MIN: 2.5,      ACTION_MAX: 6.5,      SHORT_BREAK_MIN: 120,      SHORT_BREAK_MAX: 600,      LONG_BREAK_MIN: 1200,      LONG_BREAK_MAX: 2700    },    EMAIL: {      TO: "your@email.com",      SMTP_SERVER: "smtp.gmail.com",      PORT: 587    }  }   `

2️⃣ core/logger.js
==================

### Responsibility

Centralized **terminal + file logging**.

### Imports

*   fs
    
*   path
    
*   chalk (or similar)
    

### Public Functions

*   logInfo(msg)
    
*   logWarn(msg)
    
*   logError(msg)
    
*   logFatal(msg)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML``   function log(level, message):    timestamp = now()    formatted = `[${timestamp}] ${level} | ${message}`    print_to_terminal(formatted, color_by_level)    append_to_log_file(formatted)  export logInfo, logWarn, logError, logFatal   ``

3️⃣ core/stateManager.js
========================

### Responsibility

Persistent memory across restarts.

### Imports

*   fs
    
*   path
    

### Public Functions

*   loadState()
    
*   saveState(state)
    
*   resetDailyCounters(state)
    
*   markBlocked(state, reason)
    

### State Shape

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   {    "date": "YYYY-MM-DD",    "likes": 0,    "profileVisits": 0,    "connections": 0,    "lastKeywordIndex": 0,    "lastProfileIndex": 0,    "status": "RUNNING | BLOCKED_BY_CAPTCHA"  }   `

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function loadState():    if file exists:      return parse(file)    else:      return default_state()  function saveState(state):    write_json_to_disk(state)  function resetDailyCounters(state):    if state.date != today:      reset counters      update date   `

4️⃣ core/browser.js
===================

### Responsibility

Launch & manage Playwright browser context.

### Imports

*   playwright
    
*   config
    
*   logger
    

### Public Functions

*   launchBrowser()
    
*   closeBrowser()
    
*   getPage()
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function launchBrowser():    context = chromium.launchPersistentContext(USER_DATA_DIR, {      headless: false    })    page = context.newPage()    return { context, page }  function closeBrowser(context):    context.close()   `

5️⃣ core/scheduler.js
=====================

### Responsibility

Enforce **time windows & breaks**.

### Imports

*   config
    
*   logger
    

### Public Functions

*   isWithinActiveHours()
    
*   waitForNextAllowedWindow()
    
*   takeRandomBreak()
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function isWithinActiveHours():    now = current hour    return START <= now <= END  function takeRandomBreak():    duration = random(short or long)    sleep(duration)   `

6️⃣ core/rateLimiter.js
=======================

### Responsibility

Prevent unsafe volumes.

### Imports

*   config
    
*   stateManager
    
*   logger
    

### Public Functions

*   canLike(state)
    
*   canVisitProfile(state)
    
*   canSendConnection(state)
    
*   increment(action, state)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function canSendConnection(state):    return state.connections < LIMIT  function increment(action, state):    state[action] += 1    saveState(state)   `

7️⃣ core/captchaDetector.js
===========================

### Responsibility

Detect LinkedIn security blocks.

### Imports

*   config
    
*   logger
    
*   notifier
    
*   stateManager
    

### Public Functions

*   checkForCaptcha(page, state)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function checkForCaptcha(page, state):    if url contains "checkpoint" OR       page contains "Verify you're a human":         markBlocked(state)         if EMAIL_ON_CAPTCHA:           sendEmail()         throw STOP_AUTOMATION   `

8️⃣ core/notifier.js
====================

### Responsibility

Email alerts.

### Imports

*   nodemailer
    
*   config
    
*   logger
    

### Public Functions

*   sendAlert(subject, body)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function sendAlert(subject, body):    if EMAIL_ALERTS_DISABLED:      return    send email via SMTP   `

9️⃣ actions/feedActions.js
==========================

### Responsibility

Human-like feed interaction.

### Imports

*   logger
    
*   scheduler
    
*   rateLimiter
    
*   captchaDetector
    

### Public Functions

*   scrollFeed(page, state)
    
*   likePostIfSafe(page, state)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function scrollFeed():    scroll small amount    pause randomly    sometimes scroll up  function likePostIfSafe():    if canLike:      find Like button by aria-label      hover → delay → click      increment likes   `

🔟 actions/searchPeople.js
==========================

### Responsibility

Search & filter people.

### Imports

*   fs
    
*   logger
    
*   captchaDetector
    

### Public Functions

*   loadSearchTerms()
    
*   searchPeople(page, keyword)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function loadSearchTerms():    read file    split by comma  function searchPeople(page, keyword):    go to My Network    enter keyword    click People tab    open Location filter    select Pakistan   `

1️⃣1️⃣ actions/profileActions.js
================================

### Responsibility

Visit profiles & extract data.

### Imports

*   logger
    
*   captchaDetector
    

### Public Functions

*   visitProfile(page, url)
    
*   extractProfileData(page)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function visitProfile(url):    navigate    scroll slowly    pause  function extractProfileData():    read name, headline, about, skills    return structured object   `

1️⃣2️⃣ actions/noteGenerator.js
===============================

### Responsibility

ChatGPT integration.

### Imports

*   openai
    
*   logger
    

### Public Functions

*   generateNote(profileData)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function generateNote(profile):    send prompt to ChatGPT    return note   `

1️⃣3️⃣ actions/connectActions.js
================================

### Responsibility

Send connection requests.

### Imports

*   logger
    
*   rateLimiter
    
*   captchaDetector
    

### Public Functions

*   sendConnection(page, note, state)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function sendConnection():    if !canSendConnection:      return    click Connect    if Add note exists:      paste note    click Send    increment connections   `

1️⃣4️⃣ storage/sheetsClient.js
==============================

### Responsibility

Google Sheets writing.

### Imports

*   googleapis
    
*   logger
    

### Public Functions

*   appendInteraction(row)
    
*   appendProfile(profile)
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   function appendInteraction(row):    append to interactions sheet  function appendProfile(profile):    append to profile_requests_sent   `

1️⃣5️⃣ storage/batchSync.js
===========================

### Responsibility

Deferred syncing.

### Imports

*   sheetsClient
    
*   logger
    

### Public Functions

*   syncLocalCache()
    

1️⃣6️⃣ main.js (Orchestrator)
=============================

### Responsibility

Glue everything together.

### Imports

*   all core + actions + storage modules
    

### Pseudocode

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   load config  load state  launch browser  while automation enabled:    if not within active hours:      sleep    reset daily counters if needed    scroll feed    like occasionally    for each search term:      search people      for each profile:        visit profile        extract data        generate note        send connection        log + save    take random break   `

🔚 FINAL NOTE
-------------

If you follow **this exact structure**, you will get:

*   Debuggable automation
    
*   Safe stop behavior
    
*   Minimal selector breakage
    
*   Long-running stability
    

If you want next, I can:

*   Turn this pseudocode into **real Playwright code**
    
*   Design **unit test strategy**
    
*   Add **dry-run / simulation mode**
    

Just tell me.