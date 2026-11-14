# All World Automotive: Research Report (Gemini original, 2026-11-13)

## 1. Executive Summary
The Business: All World Automotive is an independent auto repair shop based in Aurora, Colorado. Established in 2017 and owned by Ali, the shop provides a wide range of general repair services and has built a base of long-time customers who praise the quality of work and fair pricing.
The Issue: The shop suffers from an intake and communication bottleneck. OpenBay and the phone line take in bookings without a capacity limit, causing the shop to accept more cars than it can handle. Once cars are in the shop, there is a documented pattern of zero status communication and missed deadlines.
The Proposed Product: A capacity-aware booking and status-communication FastAPI microservice. This solution will funnel OpenBay and phone bookings into a single intake queue, cap new bookings based on real daily bay and technician capacity, and dispatch SMS status updates and delay notices to customers, supported by a new operational SOP.

## 2. The Business
 * Name & Background: All World Automotive, an independent auto repair shop servicing foreign and domestic vehicles. Established in 2017.
 * Leadership: The owner is named Ali. Operational management is unclear; reviews indicate a person named Alex ran the shop during Ali's absence, while a later review mentions a "new manager" named Vivun.
 * Location & Contact: 17084 E. Quincy Ave, Aurora, CO 80015. Phone numbers listed are (303) 690-4128 and (720) 744-3992.
 * Operating Hours: Tuesday–Saturday 8:00 AM–4:00 PM; closed Sunday and Monday.
 * Services: General repair, including oil & filter, brakes, tires, alignment, engine, transmission diagnosis, A/C, electrical, and hybrid battery. The shop is ASE and D.O.T. certified. Amenities include early drop-off, a shuttle service, free wifi, and on-site waiting.
 * Digital Presence: The business has no website of its own. The online booking presence is an OpenBay marketplace listing (featuring "Schedule Appointment" and "Request a Free Service Estimate" buttons) alongside manual phone calls. Note: A domain named allworldautomotiverepair.com exists, but it is a generic template shop selling parts online with no Aurora address, no owner name, and no connection to this business.
 * Reputation: The shop holds a 3.6-star rating across 50 reviews on Birdeye. The Birdeye profile states: "This profile has not been claimed by the business owner or representative." The Manta profile is unclaimed and unverified. No responses from the shop were found on the sources checked. [CLANCY AUDIT: the original said "Nobody from the shop is responding to online reviews". Softened to the verified scope. The unclaimed profiles were checked; responses on other platforms were not verified.]

## 3. The Issue: Overbooked, Then Silent
The core issue is that the shop takes in more cars than it can handle, and then goes silent.
The mechanics driving this are intake-related: OpenBay and the phone line accept bookings without checking the real bay or technician capacity for the day. Once a car is in the shop, there is no system for status communication and no callbacks are made when a job slips. This creates a gap between the OpenBay listing's promise of "quick and reliable" service where "we will always make sure that you completely understand what will be done to your vehicle" and the actual customer reality.
This pattern is documented in multiple independent reviews:
 * "The shop is run correctly when the owner is around but unfortunately he hasn't been around for awhile and it's been left to a guy named Alex who clearly over books and under staffs and constantly take too long on everything… dropped my vehicle off for a quick check up at 8:45am… he called me at 6PM claiming he didn't have time to get to it"
 * "These guys over book and under staff"
 * "told that he would have the truck back in two hours, we ended up waiting five hours just to be told the truck never got an oil change and that they needed it for longer"
 * "4 hours for an oil change is unreal… I heard the mechanic Alex give the same response to multiple customers of 'there were 4 cars ahead of them' when I know there weren't"
 * "There is a pattern of no communication… No one ever called me back… I was without my car for almost 5 days"
 * "This place has had my car for over a month. The owner dodges calls about why my vehicle is taking so long to fix."
 * "Kept my car for 2 months. Scratched brand new custom paint job… One excuse after another."

## 4. Why It Matters
 * Operations, Not Workmanship: The shop's actual repair work gets plenty of praise. Many reviews call out Ali, highlight good workmanship from long-time customers, and praise the pricing ("best prices around"). This is an operations and communication problem, not a workmanship problem.
 * Public Reputation: At 3.6 stars with an unclaimed profile, these bad experiences serve as the shop's unmanaged public face. Every overbooked day creates the next bad review, and because the profile is unclaimed, nobody is stepping in to mitigate the damage online.
 * Operational Gridlock: Cars sitting in the shop for weeks or months tie up valuable bays, stalling daily throughput and revenue.
 * No Owned Booking Channel: Everything relies on a third-party marketplace listing and phone calls. Because the shop does not own its booking channel, there is no structural way to cap intake or text customers at scale, forcing the staff to call customers one by one, which they are failing to do.

## 5. The Product Idea: Capacity-Aware Booking + Status-Communication Service
To resolve the intake bottleneck and the lack of status communication, we propose a custom FastAPI middleware service.
 * What It Does: The service funnels all bookings from OpenBay and phone calls into a single, unified intake queue. It then caps new daily bookings by checking them against the real bay and technician capacity limits for that specific day.
 * End-to-End Flow: When a customer drops off a car, they are enrolled in the automated system. The service dispatches automatic SMS status texts at each key stage of the repair (received → diagnosed → in progress → ready). If a job slips past its expected completion time, the service sends a delay notice.
 * Manual Override: The owner or manager retains the ability to override the capacity limits for emergencies or the most profitable walk-ins.
 * Technical Shape:
   * A FastAPI backend service managing the central intake queue.
   * A capacity-checking rules engine mapping incoming requests against hard bay/technician limits.
   * An SMS integration for automated stage updates and delay notices.
 * SOP Integration: The delivery will include a simple Standard Operating Procedure (SOP) documenting how the front desk should manage intake and trigger callbacks under the new flow.

## 6. Scope for a First Version
In Scope for v1:
 * The FastAPI middleware service connecting the OpenBay/phone intake queue to the capacity rules engine.
 * The capacity-checking logic based on total bays and daily technician availability.
 * The automated SMS status update pipeline (received, diagnosed, in progress, ready) and delay notifications.
 * The SOP documentation for intake and status changes.
Out of Scope for v1:
 * A custom consumer-facing website (bookings will remain through OpenBay and the phone).
 * Automated review response management.
Delivery Outline (35/40/25 Milestone Shape):
 * Milestone 1 (35%): Kickoff & Capacity-Rules Lock: Confirming exact shop metrics and finalizing the mathematical logic for the capacity engine.
 * Milestone 2 (40%): Working Demo: Delivery of a functional end-to-end pipeline (intake queue → capacity block → test SMS notifications).
 * Milestone 3 (25%): Final Delivery: Production deployment of the FastAPI service and handover of the documented SOP.

## 7. Risks, Limits & Unknowns
Before initiating Milestone 1, the following operational unknowns must be confirmed with Ali:
 * Intake Logistics: How do bookings reach the shop today (e.g., OpenBay email notifications, an OpenBay dashboard, a physical phone log, or paper)?
 * Capacity Baseline: How many cars does the shop take in per day versus the actual number of bays and technicians available?
 * Status Tracking: Does anyone track individual job status today, and if so, where does that data live?
 * Recency of the Issue: The dates of the negative reviews could not be verified on the source page. Are these operational breakdowns a recent development, or do they reflect an older state of the business?
 * Management Status: Is Ali still absent from the shop, or has the situation stabilized under the "new manager" Vivun?

## 8. Sources
 * https://app.openbay.com/s/all-world-automotive-aurora-co
 * https://usa-services.worldorgs.com/catalog/aurora/auto-repair/all-world-automotive
 * https://reviews.birdeye.com/all-world-automotive-156042638139338
 * https://www.manta.com/c/mhbj59b/all-world-automotive
 * https://allworldautomotiverepair.com/
