# L&G Cleaning Services — Research Report (Gemini original, 2026-11-13)

## 1. Executive Summary
The Business: L&G Cleaning Services is a highly rated, family-owned cleaning company established in 2011, serving the Aurora and greater Denver, Colorado area. The company maintains an excellent reputation for quality and communication.
The Issue: The owner, Luis Guzman, manually reviews, prices, and confirms every single quote and appointment request. This creates a significant bottleneck, acting as a strict ceiling on the company's growth capacity and consuming the owner’s valuable time.
The Proposed Product: A custom automated intake, quoting, and scheduling FastAPI microservice. This solution will instantly compute firm quotes using the company’s already-published pricing rules, check real crew availability, and issue automatic SMS/email confirmations for standard cleanings, routing only complex edge cases to the owner for manual approval.

## 2. The Business
 * Name & Background: L&G Cleaning Services, a family-owned business established in 2011. Bonded and insured with a bilingual team (English & Spanish).
 * Leadership: Owned and operated by Luis Guzman.
 * Contact Details: Phone: (303) 944-4318 | Email: Lguzman@lngcleaning.com | Website: https://www.lngcleaning.com/
 * Operating Hours: Monday–Saturday.
 * Service Area: Based in Aurora, CO, serving Denver, Aurora, Centennial, Parker, Castle Pines, Castle Rock, Englewood, Elizabeth, Greenwood Village, Littleton, and Cherry Hills Village.
 * Services Provided: Recurring house and apartment cleaning, deep cleaning, move-in/move-out cleaning, post-construction cleaning, commercial/office/janitorial, and medical/dental office cleaning.
 * Reputation: 4.8 stars across 60 Google reviews. The business is also listed on Angi and HomeAdvisor. The reviews displayed on the site are uniformly positive, specifically highlighting quality, reliability, punctuality, "great communication and honest pricing," and being "easy to schedule." [CLANCY AUDIT: the full set of 60 reviews was not read individually — "displayed on the site" is the verified scope.]
 * Published Pricing & Policies:
   * Home & Apartment: $120–$260
   * Office/Commercial: $180–$450
   * Deep Clean: $220–$450
   * Move In/Out: $260–$550
   * Post-Construction: $300–$700
   * Discounts: 20% weekly, 15% bi-weekly, 10% monthly, 10% senior (65+).
   * Fees & Terms: Rush fee is a $100 minimum ($200 for a weekend rush). There is no deposit required, no cancellation fee, and customers pay only when the job is done.

## 3. The Issue: The Owner Bottleneck
Despite having the necessary structured data to automate bookings, every single scheduling decision funnels manually through one person. The website's own copy repeatedly reinforces this bottleneck:
 * Homepage hero: "Ask a question or request a free estimate. Luis confirms pricing and appointments."
 * "How It Works" step 2: "Request a day and arrival window, Mon–Sat. Luis confirms availability and your appointment."
 * Quote form ending: "This is a quote request, not a confirmed appointment."
 * AI Assistant (Maggie): "Share the details of the cleaning you need. The Advisor organizes the request for Luis to review and confirm your final quote."
 * Service-specific interventions:
   * Deep cleaning: "Luis reviews your priorities"
   * Move-in/out: "Luis can confirm what is included"
   * Free return cleaning: "Luis confirms scheduling"
   * Damage reports: "Luis reviews the situation"
 * Modifications: Cancellations and rescheduling require a manual call or email with no self-serve option. Last-minute/same-day bookings state: "Call (303) 944-4318 to check availability".
 * Site-wide footer: "Monday–Saturday · Appointments confirmed by Luis."
In mechanics, the AI and intake forms merely collect data; a submitted request yields nothing until Luis personally replies.

## 4. Why It Matters
 * Single Point of Failure: Luis is the sole bottleneck for pricing, availability, confirmation, changes, and rescheduling. Every request waits on his manual reply, including evenings and weekends when he is actively working on jobs.
 * Strict Growth Ceiling: This manual intervention caps how many bookings the business can physically intake and limits how fast a customer receives an answer.
 * Wasted Automation Potential: The inputs required to fully automate these decisions are already being collected in a structured format. The current quote form successfully captures service type, bedrooms, bathrooms, square footage, frequency, add-ons (fridge/oven, interior windows, laundry & ironing), preferred dates, and specific arrival windows (8–10am, 10am–12pm, 12–2pm, 2–4pm). Furthermore, the pricing logic and discount rules are entirely standardized and published. The data is fully prepared for automation; only the final decision remains manual.
 * Important Distinction: This is strictly an owner-time and growth-ceiling problem, not a reputation or customer service problem. Existing reviews explicitly praise the business as "easy to schedule."

## 5. The Product Idea: Automated Intake, Quoting & Scheduling Service
To uncap the business's growth and reclaim the owner's time, we propose a custom middleware solution that transitions standard bookings to a zero-touch flow, keeping Luis in the loop only for complex edge cases.
 * End-to-End Customer Flow: The customer submits the existing structured form. Instead of resting in an inbox, the service instantly computes a firm quote using the published pricing ranges and discount rules. It then checks real-time crew availability, secures the calendar block, and automatically sends SMS and email confirmations and reminders to the client.
 * Luis Override: Standard recurring and one-off house cleans are fully automated. Complex edge cases (deep cleans, move-ins/move-outs, and post-construction) are automatically routed to a manual approval queue for Luis to review before confirmation.
 * Technical Shape:
   * Core: A lightweight FastAPI service acting as the central nervous system.
   * Quote Engine: A rules-based computational engine that translates the site's published ranges and discount matrices into exact quotes.
   * Availability Module: An integration that checks the business's existing schedule to map available 2-hour arrival windows against crew capacity. [CLANCY AUDIT: this assumes a digital schedule exists — what tool Luis uses today is unknown (see §7). If bookings are tracked on paper or by memory, v1 includes standing up a shared calendar first, before the integration.]
   * Communications: Automated SMS and email dispatch for instant confirmations and pre-appointment reminders.
   * Operational Handoff: Delivery includes a complete Standard Operating Procedure (SOP) documenting how to manage the new flow.

## 6. Scope for a First Version (v1)
In Scope for v1:
 * The FastAPI middleware service linking the intake form to the quote engine.
 * The rules-based pricing calculator for standard and recurring home/apartment cleans.
 * Basic calendar/availability check integration.
 * Automated SMS and email confirmations/reminders for approved bookings.
 * Standard Operating Procedure (SOP) documentation.
Explicitly Out of Scope for v1:
 * Automated approvals for complex services (deep cleans, move-in/out, post-construction, commercial). These will be routed to the Luis Override step.
 * A custom-built CRM or calendar application (the service will integrate with the schedule tooling Luis currently uses).
Delivery Outline (35/40/25 Milestone Shape):
 * Milestone 1 (35%): Kickoff & Rules Lock: Finalizing the exact mathematical logic for the pricing engine and confirming the calendar integration constraints.
 * Milestone 2 (40%): Working Demo: Delivery of a functional end-to-end pipeline (intake form → automated quote → calendar block → test email/SMS notifications).
 * Milestone 3 (25%): Final Delivery: Production deployment of the FastAPI service and handover of the documented SOP.

## 7. Risks, Limits & Unknowns
Before initiating Milestone 1, the following operational unknowns must be confirmed with Luis:
 * What specific tool (if any) is currently being used to track crew schedules and bookings today (e.g., Google Calendar, a specific CRM, a spreadsheet, or paper)?
 * How long does a manual quote reply typically take today?
 * What is the current weekly volume of inbound requests?
 * Does the existing AI "Advisor" (Maggie) currently deliver its intake summaries via email, or do they live in a proprietary dashboard?

## 8. Sources
 * https://www.lngcleaning.com/
 * https://www.lngcleaning.com/aurora/
 * https://www.lngcleaning.com/denver/
 * https://www.lngcleaning.com/commercial-cleaning/
 * https://www.lngcleaning.com/office-cleaning/
 * https://www.lngcleaning.com/medical-office-cleaning/
