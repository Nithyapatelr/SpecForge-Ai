"""
generate_synthetic_data.py
--------------------------
Generates a large corpus of synthetic requirement documents across 25 domains,
writes them as .txt files to data/sample_requirements/, and ingests them into
the SpecForge database using the existing pipeline.

Usage:
    C:\\Python314\\python.exe scripts\\generate_synthetic_data.py
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─────────────────────────────────────────────────────────────────────────────
# SYNTHETIC REQUIREMENT DOCUMENTS
# Each entry: (slug, title, list_of_requirements)
# Mix of RIT categories per document:
#   BR = Behavioral Rule, ST = State Transition, AP = Actor Permission,
#   DC = Data Contract, IC = Integration Constraint, AC = Acceptance Condition
#   VAGUE = intentionally ambiguous (for ambiguity detection testing)
# ─────────────────────────────────────────────────────────────────────────────

DOCUMENTS = [

    # ── 1. E-Commerce Platform ────────────────────────────────────────────────
    ("ecommerce-01", "E-Commerce Platform — Order Management Requirements", [
        "1. The system shall allow registered customers to browse products by category, brand, price range, and customer rating.",
        "2. When a customer places an order, the system shall deduct the ordered quantity from inventory within 5 seconds and send an order confirmation email.",
        "3. An order transitions from 'Pending' to 'Processing' once payment is confirmed; from 'Processing' to 'Shipped' once a tracking number is assigned; and from 'Shipped' to 'Delivered' once the carrier marks it as delivered.",
        "4. Only users with the 'Warehouse Manager' role shall be permitted to update inventory stock levels directly.",
        "5. The product SKU field must be a string of exactly 12 alphanumeric characters and must be unique across the product catalog.",
        "6. The system shall integrate with Stripe Payment Gateway; if Stripe is unavailable, it shall attempt PayPal as a fallback before failing the transaction.",
        "7. The product listing page shall load within 1.5 seconds for 95% of requests under 500 concurrent users.",
        "8. The system should make shopping easy and enjoyable for customers.",
        "9. A customer may return a product within 30 days of delivery; the system shall automatically issue a refund to the original payment method within 3 business days of receiving the returned item.",
        "10. Only a 'Store Admin' may create, update, or deactivate product listings; 'Sales Staff' may view product details but not modify them.",
        "11. Each order record must contain: order_id (UUID), customer_id (UUID), order_date (ISO 8601 datetime), line_items (array), total_amount (decimal, 2 decimal places), and status (enum: Pending|Processing|Shipped|Delivered|Cancelled|Refunded).",
        "12. The system shall apply discount codes at checkout; a discount code must reduce the cart total by the specified percentage or fixed amount but shall never reduce the total below zero.",
        "13. If a customer's payment fails, the system shall retain the cart contents for 15 minutes and prompt the customer to retry or use a different payment method.",
        "14. The checkout page must complete the full payment flow in under 3 seconds at 200 concurrent users.",
        "15. The system shall send abandoned cart reminder emails 1 hour and 24 hours after a customer adds items to the cart without completing checkout.",
        "16. Product reviews must be submitted by customers who have purchased the product; the system shall reject review submissions from non-purchasers.",
        "17. The system shall provide good customer support features.",
        "18. The search functionality shall return relevant results and support typo tolerance for queries with up to 2 character errors.",
        "19. All customer payment card data must be tokenized before storage; the system must never store raw card numbers.",
        "20. The system shall generate a daily sales report in CSV format and deposit it in the configured S3 bucket by 02:00 UTC each day.",
    ]),

    # ── 2. Banking / Fintech ──────────────────────────────────────────────────
    ("banking-01", "Retail Banking Platform — Account and Transaction Requirements", [
        "1. The system shall allow customers to open a savings or checking account online by submitting identity documents, address proof, and completing KYC verification.",
        "2. When a transaction is initiated, the system shall validate available balance, apply any applicable transaction limits, and post the debit or credit within 2 seconds.",
        "3. An account transitions from 'Pending KYC' to 'Active' once identity verification is approved; from 'Active' to 'Frozen' if suspicious activity is flagged; and from 'Frozen' to 'Closed' upon customer request after review.",
        "4. Only users with the 'Compliance Officer' role shall have permission to unfreeze a flagged account.",
        "5. Each transaction record must contain: transaction_id (UUID), account_id (UUID), transaction_type (enum: Debit|Credit|Transfer|Fee), amount (decimal, 2 decimal places), currency (ISO 4217 3-letter code), timestamp (ISO 8601), and status (enum: Pending|Completed|Reversed|Failed).",
        "6. The system shall integrate with the national SWIFT network for international wire transfers; if SWIFT is unavailable, the transaction must be queued and retried within 30 minutes.",
        "7. The mobile banking login must complete within 1 second for 99% of requests.",
        "8. The system should be secure and trustworthy for customers.",
        "9. Customers must be authenticated using multi-factor authentication (MFA) before performing any transaction exceeding $500.",
        "10. Only a 'Branch Manager' may approve loan applications above $50,000; amounts below this threshold may be auto-approved by the credit scoring engine.",
        "11. The system shall send real-time push notifications and SMS alerts for every debit transaction exceeding $100.",
        "12. If a debit transaction would cause the account balance to fall below zero, the system shall decline the transaction unless the account has an approved overdraft limit.",
        "13. The credit scoring engine must evaluate loan eligibility using the applicant's credit bureau score, debt-to-income ratio, and employment history.",
        "14. All inter-bank transfers must be completed within the regulatory limit of T+1 business days.",
        "15. The system shall archive transaction records older than 7 years to cold storage and make them accessible to compliance officers on demand within 48 hours.",
        "16. The system shall detect and flag transactions matching known fraud patterns using rule-based and ML-based detection in real time.",
        "17. Account statements must be available for download in PDF and CSV format for up to 5 years of history.",
        "18. The system should be fast and handle many users at once.",
        "19. The system shall comply with PCI-DSS Level 1 requirements for all card data processing and storage.",
        "20. Passwords must be hashed using bcrypt with a minimum work factor of 12 before storage; plain-text passwords must never be stored.",
        "21. The system shall enforce daily transfer limits per account tier: Basic ($5,000), Premium ($25,000), Private Banking (unlimited with manual approval above $100,000).",
        "22. Loan repayment schedules must be generated using the amortization formula and stored as a structured JSON array in the loan record.",
    ]),

    # ── 3. HR Management System ───────────────────────────────────────────────
    ("hr-01", "Human Resources Management System — Employee Lifecycle Requirements", [
        "1. The system shall allow HR administrators to create, update, and deactivate employee profiles including personal information, job title, department, and compensation details.",
        "2. When a new employee is onboarded, the system shall automatically provision accounts for email, Slack, and the project management tool within 4 hours of the start date being confirmed.",
        "3. An employee record transitions from 'Offer Extended' to 'Active' on the confirmed start date; from 'Active' to 'On Leave' when an approved leave request is active; and from 'Active' to 'Terminated' upon separation processing.",
        "4. Only the 'HR Director' or 'C-Suite' roles may view salary details for employees outside their direct reporting line.",
        "5. Each employee record must contain: employee_id (UUID), full_name (string, max 200 characters), date_of_birth (ISO 8601 date), national_id (string, encrypted), department_id (FK), job_title (string), hire_date (ISO 8601 date), and employment_type (enum: Full-Time|Part-Time|Contract|Intern).",
        "6. The system shall integrate with the payroll provider API (ADP) to push approved payroll runs 3 business days before each pay date.",
        "7. Leave balance calculations must complete within 500 milliseconds for any employee query.",
        "8. Managers should be able to easily track their team's performance.",
        "9. A leave request transitions from 'Submitted' to 'Approved' or 'Rejected' within 48 business hours; if no action is taken, the system shall escalate to the HR administrator.",
        "10. Only a direct manager or HR administrator may approve or reject leave requests; the requesting employee may not approve their own leave.",
        "11. The performance review cycle must be initiated quarterly; the system shall notify managers and employees 2 weeks before review deadlines.",
        "12. The payroll system must calculate gross pay, statutory deductions (tax, social security), and net pay correctly for all employment types.",
        "13. The system shall generate a headcount report by department, employment type, and tenure band on the first business day of each month.",
        "14. Employee self-service password reset must enforce the organizational password policy: minimum 12 characters, at least 1 uppercase, 1 lowercase, 1 digit, 1 special character.",
        "15. The system shall archive records of terminated employees for 7 years in compliance with labor law and restrict access to HR Director role only.",
        "16. Training completion certificates shall be automatically emailed to the employee upon completion of a mandatory training module.",
        "17. The system should be user-friendly for non-technical HR staff.",
        "18. All employee personal data must be stored in an encrypted database column using AES-256; decryption keys must not be stored in the same system.",
        "19. The system shall track and report overtime hours; any overtime exceeding 10 hours per week must trigger an alert to the employee's manager.",
        "20. Recruitment pipelines must track candidates from 'Applied' through 'Screened', 'Interviewed', 'Offered', and 'Hired' or 'Rejected' states.",
        "21. Only a recruiter or HR administrator may advance a candidate to the 'Offered' stage.",
        "22. The system shall produce an annual diversity and inclusion report summarizing workforce demographics by gender, age band, and ethnicity.",
        "23. Job postings must be published to LinkedIn, Indeed, and the company careers page simultaneously via API integration.",
        "24. The system should handle all HR needs effectively.",
    ]),

    # ── 4. Ride-Sharing Application ───────────────────────────────────────────
    ("rideshare-01", "Ride-Sharing Application — Booking and Driver Requirements", [
        "1. The system shall allow registered riders to request a ride by providing pickup and drop-off locations; the system must show estimated fare and ETA before confirmation.",
        "2. When a ride is requested, the system shall broadcast the request to available drivers within a 3 km radius and assign the first driver who accepts within 30 seconds.",
        "3. A ride transitions from 'Requested' to 'Accepted' when a driver accepts; to 'In Progress' when the driver marks arrival and starts the trip; to 'Completed' when the driver ends the trip; and to 'Cancelled' if either party cancels before trip start.",
        "4. Only users with the 'Fleet Manager' role may view real-time GPS locations of all active drivers.",
        "5. Each ride record must contain: ride_id (UUID), rider_id (UUID), driver_id (UUID), pickup_coordinates (lat/lon decimal), dropoff_coordinates (lat/lon decimal), requested_at (ISO 8601), fare_amount (decimal, 2 decimal places), and status.",
        "6. The system shall integrate with Google Maps API for route calculation and ETA; if unavailable, it shall fall back to OpenStreetMap Routing API.",
        "7. Driver matching must complete within 5 seconds for 95% of ride requests.",
        "8. The app should feel smooth and responsive for drivers and riders.",
        "9. Surge pricing shall activate automatically when demand exceeds supply by more than 1.5x in a given zone; the system must display the surge multiplier prominently to the rider before booking confirmation.",
        "10. Only a verified driver with a valid license, insurance, and background check clearance may receive ride assignments.",
        "11. The system shall calculate driver earnings by applying the platform commission rate (15%) to the base fare and crediting the net amount to the driver's wallet daily at midnight.",
        "12. If a driver does not accept or decline a ride within 20 seconds, the system shall automatically pass the request to the next available driver.",
        "13. The fare must be calculated using: base_fare + (per_km_rate * distance) + (per_minute_rate * duration) + applicable_surge_multiplier.",
        "14. Ride cancellation by a rider after driver arrival shall incur a cancellation fee of $2.00 charged to the rider.",
        "15. The system shall provide in-app SOS functionality; activating SOS must immediately share the rider's real-time location with emergency contacts and the platform safety team.",
        "16. Drivers must maintain a minimum rating of 4.0 out of 5.0; drivers falling below this threshold must be notified and may be deactivated after 30 days without improvement.",
        "17. The system should make commuting better for everyone.",
        "18. The payment split feature shall allow riders to divide the fare equally among up to 4 riders; each participant must confirm their share via in-app notification within 5 minutes.",
        "19. All location data must be encrypted in transit using TLS 1.3; stored location history must be retained for 90 days only.",
        "20. The system shall generate a weekly earnings summary report for each driver, delivered via email every Monday at 08:00 local time.",
        "21. Promo codes must be validated at booking confirmation; invalid or expired codes must return a descriptive error message within 1 second.",
        "22. The system shall enforce a maximum of 12 driving hours per day per driver and alert the driver and fleet manager when 10 hours are reached.",
    ]),

    # ── 5. University Enrollment System ──────────────────────────────────────
    ("university-01", "University Student Enrollment System — Registration Requirements", [
        "1. The system shall allow prospective students to submit undergraduate and postgraduate applications online with academic transcripts, personal statements, and reference letters.",
        "2. When a student's application is received, the system shall send an acknowledgment email with a unique application reference number within 10 minutes.",
        "3. An application transitions from 'Submitted' to 'Under Review' when an admissions officer opens it; to 'Conditional Offer' or 'Rejected' after evaluation; to 'Accepted' when the student confirms acceptance; and to 'Enrolled' on the course start date.",
        "4. Only 'Admissions Officers' and 'Academic Deans' may change an application status to 'Accepted' or 'Rejected'.",
        "5. Each student record must contain: student_id (UUID), national_id (encrypted string), full_name (string), date_of_birth (ISO 8601 date), program_id (FK), enrollment_status (enum), and academic_year (integer).",
        "6. The system shall integrate with the national student loan authority API to automatically verify financial aid eligibility upon enrollment confirmation.",
        "7. The course registration portal must handle 5,000 concurrent users during peak enrollment periods without degrading response time beyond 3 seconds.",
        "8. The system should help students choose courses that are good for their career.",
        "9. A student may register for a maximum of 6 courses per semester; the system shall reject any registration exceeding this limit.",
        "10. Only a student who has paid the semester fee or has an approved payment deferral may register for courses.",
        "11. Prerequisites must be enforced automatically; the system shall reject course registration if the student has not completed all listed prerequisites.",
        "12. The academic transcript must be generated in PDF format and digitally signed; it must be available for download within 60 seconds of the request.",
        "13. Grades submitted by faculty must be locked 5 business days after the grade submission deadline; locked grades may only be modified by the Registrar.",
        "14. The system shall send enrollment deadline reminder notifications to all students who have not yet registered, 14 days, 7 days, and 1 day before the deadline.",
        "15. All student financial records must be retained for 10 years in compliance with government auditing requirements.",
        "16. The timetable scheduling engine must detect and prevent course time conflicts for a student's registered courses.",
        "17. The system should be easy to use for students with no technical background.",
        "18. Faculty must be able to upload course materials (PDF, PPTX, MP4) up to 500 MB per file to the course LMS.",
        "19. The system shall calculate and publish semester GPA and cumulative GPA for each student within 24 hours of all grade submissions being finalized.",
        "20. Student data must be processed in compliance with FERPA regulations; access to records must be logged with accessor identity and timestamp.",
        "21. The scholarship matching engine shall evaluate all enrolled students against available scholarship criteria and auto-apply where all conditions are met.",
        "22. The system shall generate an accreditation report summarizing enrollment statistics, course completion rates, and faculty-to-student ratios annually.",
    ]),

    # ── 6. Inventory Management System ───────────────────────────────────────
    ("inventory-01", "Warehouse Inventory Management System — Stock Control Requirements", [
        "1. The system shall allow warehouse staff to receive goods by scanning barcodes or QR codes and recording quantity, supplier, batch number, and expiry date.",
        "2. When stock for any product falls below its defined reorder point, the system shall automatically generate a purchase order and notify the procurement team within 15 minutes.",
        "3. A stock item transitions from 'In Transit' to 'Received' upon goods receipt confirmation; to 'Quarantined' if quality inspection fails; and to 'Available' upon inspection clearance.",
        "4. Only users with the 'Warehouse Manager' or 'Inventory Auditor' role may perform stock adjustments outside of standard receive/dispatch operations.",
        "5. Each inventory transaction record must contain: transaction_id (UUID), product_id (UUID), transaction_type (enum: Receive|Dispatch|Adjustment|Return), quantity (integer), unit_of_measure (string), timestamp (ISO 8601), and performed_by (UUID).",
        "6. The system shall integrate with the ERP system via REST API to synchronize stock levels every 15 minutes; discrepancies greater than 5% must trigger an alert.",
        "7. Barcode scanning operations must register within 500 milliseconds to support fast-paced warehouse workflows.",
        "8. The system should make it easy to manage stock effectively.",
        "9. FIFO (First-In, First-Out) dispatch logic must be enforced for all perishable goods; the system shall automatically select the oldest batch for dispatch.",
        "10. Only items that have passed quality inspection may be marked as 'Available' and dispatched to fulfillment.",
        "11. Each product record must include: product_id (UUID), SKU (string, unique, max 20 characters), product_name (string), category (string), reorder_point (integer), reorder_quantity (integer), and storage_zone (string).",
        "12. The system shall generate a daily inventory valuation report using FIFO costing and deliver it to the finance team by 06:00 each morning.",
        "13. Cycle counts must be scheduled by the system for each storage zone on a rotating basis; discrepancies found during cycle counts must be recorded and investigated within 48 hours.",
        "14. The system shall enforce storage zone capacity limits; any attempt to receive goods into a zone at 100% capacity must be rejected with a descriptive error.",
        "15. Expired goods must be automatically flagged and moved to 'Quarantined' status 3 days before expiry; disposal must be approved by the Warehouse Manager.",
        "16. The system shall maintain a full audit trail of all stock movements with actor identity, timestamp, and before/after quantity.",
        "17. The system should optimize space utilization in the warehouse.",
        "18. Return merchandise authorizations (RMAs) must capture: reason code, condition of returned goods, and originating order reference.",
        "19. The system shall support multi-location warehousing; stock queries must be filterable by warehouse, zone, aisle, and shelf.",
        "20. Annual physical inventory counts must produce a variance report comparing system quantities to physical counts; all variances must be reconciled before the financial year close.",
    ]),

    # ── 7. Smart Home IoT Platform ────────────────────────────────────────────
    ("smarthome-01", "Smart Home IoT Platform — Device Management Requirements", [
        "1. The system shall allow homeowners to pair smart devices (lights, locks, thermostats, cameras) by scanning a QR code or entering a device pairing code in the mobile app.",
        "2. When a door lock device reports a 'forced entry' event, the system shall immediately send push notifications to all household members and the designated emergency contact.",
        "3. A device transitions from 'Unpaired' to 'Paired' after successful pairing; to 'Offline' if no heartbeat is received for 5 minutes; and to 'Error' if the device reports a hardware fault.",
        "4. Only the 'Home Owner' account may add, remove, or rename devices; 'Guest' accounts may only control devices they have been explicitly granted access to.",
        "5. Each device record must contain: device_id (UUID), device_type (enum), mac_address (string, unique), firmware_version (string), paired_at (ISO 8601), and status (enum: Paired|Offline|Error|Unpaired).",
        "6. The system shall integrate with Amazon Alexa and Google Home via their respective Smart Home APIs to enable voice control of all paired devices.",
        "7. Device command execution (e.g., turn on light) must complete end-to-end within 1 second for 99% of commands.",
        "8. The system should make homes smarter and more energy efficient.",
        "9. Automation rules shall be evaluated in priority order; if two rules conflict, the higher-priority rule shall take precedence and a conflict notification shall be sent to the homeowner.",
        "10. Only devices with firmware version 3.0.0 or above may be enrolled in the platform; older firmware devices must be prompted to update before pairing.",
        "11. Each automation rule must include: rule_id (UUID), trigger_condition (JSON), action (JSON), priority (integer 1-100), and is_active (boolean).",
        "12. The system shall store 30 days of device event history; events older than 30 days shall be purged unless the user has a Premium subscription (1-year retention).",
        "13. Energy consumption data from smart plugs and thermostats must be aggregated hourly and displayed as daily, weekly, and monthly charts.",
        "14. Camera livestream must begin within 3 seconds of the homeowner tapping the camera tile in the app.",
        "15. All video streams must be encrypted end-to-end; raw video must never pass through the platform's servers unencrypted.",
        "16. The system shall perform automatic firmware over-the-air (OTA) updates during a maintenance window (02:00–04:00 local time) after homeowner approval.",
        "17. The system should give good notifications.",
        "18. Guest access permissions must expire automatically at a configured date and time; expired guest accounts must have all device control permissions revoked.",
        "19. The platform must support geofencing; when the homeowner's phone leaves the defined home area, the system shall automatically arm the security devices and lock all doors.",
        "20. The system shall send a weekly energy report every Sunday summarizing energy saved compared to the previous week.",
        "21. Multiple homes may be managed under a single account; device namespaces must be isolated per property.",
    ]),

    # ── 8. Insurance Claims Processing ───────────────────────────────────────
    ("insurance-01", "Insurance Claims Processing System — Claim Lifecycle Requirements", [
        "1. The system shall allow policyholders to submit insurance claims online by uploading supporting documents, photographs, and a written incident description.",
        "2. When a claim is submitted, the system shall assign a unique claim number and send an acknowledgment to the policyholder within 5 minutes.",
        "3. A claim transitions from 'Submitted' to 'Under Investigation' when an adjuster is assigned; to 'Approved' or 'Rejected' after investigation; to 'Paid' once the approved settlement amount is disbursed; and to 'Closed' after payment confirmation.",
        "4. Only licensed adjusters with the 'Claims Adjuster' role may change claim status from 'Under Investigation' to 'Approved' or 'Rejected'.",
        "5. Each claim record must contain: claim_id (UUID), policy_id (FK), claimant_id (FK), incident_date (ISO 8601 date), claim_type (enum), submitted_at (ISO 8601 datetime), claimed_amount (decimal, 2 decimal places), and status (enum).",
        "6. The system shall integrate with the insurance fraud detection API; all claims above $10,000 must be automatically submitted for fraud scoring before adjuster assignment.",
        "7. Claim acknowledgment must be sent within 5 minutes for 99.5% of submissions.",
        "8. The claims system should be fair and easy to use for policyholders.",
        "9. Claims exceeding $50,000 must be reviewed and co-approved by a Senior Adjuster and the Claims Manager before status changes to 'Approved'.",
        "10. Only adjusters assigned to a specific claim may view, update, or add notes to that claim; unassigned adjusters may only view anonymized claim summaries.",
        "11. Supporting documents uploaded with a claim must be virus-scanned within 60 seconds; documents failing the scan must be quarantined and the claimant notified.",
        "12. The system shall calculate and apply depreciation to claim settlements for property damage claims using the configured depreciation schedule.",
        "13. Settlement payments must be initiated via ACH bank transfer; the payment must reach the claimant's account within 3 business days of approval.",
        "14. The system shall generate a monthly claims analytics report by claim type, average settlement amount, fraud rate, and average processing time.",
        "15. All claim documents must be retained for 10 years in compliance with insurance regulatory requirements.",
        "16. The system shall enforce policy coverage limits; any approved settlement exceeding the policy coverage limit must be flagged for manual review.",
        "17. The system should process claims faster than competitors.",
        "18. Claim denial letters must be auto-generated using the configured letter template and include the specific denial reason code and applicable policy clause.",
        "19. Claimants must be notified by email and SMS at every status transition; notification must be sent within 2 minutes of the status change.",
        "20. The adjuster workload dashboard must display each adjuster's open claims, average days to resolution, and approval/rejection rate.",
        "21. Claims submitted more than 90 days after the incident date must be flagged for late submission review and cannot be fast-tracked.",
        "22. The system shall support subrogation tracking; when the insurer recovers costs from a third party, the recovery amount must be recorded and linked to the originating claim.",
    ]),

    # ── 9. Food Delivery Platform ─────────────────────────────────────────────
    ("fooddelivery-01", "Food Delivery Platform — Order and Delivery Requirements", [
        "1. The system shall allow customers to browse restaurants by cuisine type, rating, delivery time estimate, and minimum order amount.",
        "2. When a customer places a food order, the system shall notify the restaurant within 10 seconds and wait for the restaurant to confirm before showing the customer a confirmed ETA.",
        "3. An order transitions from 'Placed' to 'Confirmed' when the restaurant accepts; to 'Preparing' when preparation starts; to 'Ready for Pickup' when the restaurant marks it ready; to 'Out for Delivery' when a rider picks up; and to 'Delivered' when the rider marks delivery complete.",
        "4. Only users with the 'Restaurant Manager' role may update the restaurant's menu, operating hours, and delivery radius settings.",
        "5. Each order record must contain: order_id (UUID), customer_id (UUID), restaurant_id (UUID), rider_id (UUID, nullable), items (JSON array), subtotal (decimal), delivery_fee (decimal), total (decimal), placed_at (ISO 8601), and status (enum).",
        "6. The system shall integrate with Google Maps API for real-time rider location tracking and ETA updates every 30 seconds.",
        "7. Order confirmation must be delivered to the customer within 15 seconds of placement for 98% of orders.",
        "8. Deliveries should arrive as fast as possible.",
        "9. The platform shall enforce a maximum delivery radius of 10 km per restaurant; orders from customers outside this radius must be rejected with a descriptive message.",
        "10. Only riders who have completed background checks and received food handling certification may be assigned delivery orders.",
        "11. Restaurants must specify preparation time per menu item; the system shall calculate estimated total preparation time at order placement.",
        "12. Customers may cancel an order without penalty within 2 minutes of placement; cancellation after restaurant confirmation shall incur a $1.50 cancellation fee.",
        "13. The delivery fee must be calculated as: base_fee + (per_km_rate * distance_beyond_2km); orders above $30 qualify for free delivery.",
        "14. Customer ratings submitted for a completed delivery must be stored and factored into the restaurant's and rider's rolling 30-day average rating.",
        "15. Promo codes must not be stackable; applying a second promo code must replace the first and notify the customer.",
        "16. If no rider accepts a delivery within 10 minutes of the restaurant marking the order 'Ready for Pickup', the system must alert the dispatch team.",
        "17. The system should have a nice interface for customers.",
        "18. Allergy information must be displayed prominently on each menu item; customers must be able to filter menu items by allergen.",
        "19. All customer payment data must be processed through a PCI-DSS compliant payment gateway; the platform must not store raw card data.",
        "20. The system shall generate a weekly payout report for restaurants summarizing total orders, gross revenue, platform commission, and net payout.",
        "21. Restaurant onboarding must verify the restaurant's food safety license and business registration before activating the account.",
        "22. The system shall support scheduled orders up to 7 days in advance; scheduled orders must be activated 30 minutes before the requested delivery time.",
        "23. Peak hour surge delivery fees (1.25x multiplier) must be disclosed to the customer at checkout and require explicit customer acknowledgment.",
    ]),

    # ── 10. Flight Booking System ─────────────────────────────────────────────
    ("flight-01", "Flight Booking System — Reservation and Ticketing Requirements", [
        "1. The system shall allow customers to search for available flights by specifying origin, destination, departure date, return date (optional), number of passengers, and cabin class.",
        "2. When a booking is confirmed, the system shall issue an e-ticket with a unique PNR within 30 seconds and send it to the customer's registered email.",
        "3. A booking transitions from 'Hold' to 'Confirmed' upon payment; to 'Checked In' when the passenger completes online check-in; to 'Boarded' upon gate scan; and to 'Cancelled' if the booking is cancelled before departure.",
        "4. Only 'Airline Staff' and 'Travel Agency' roles may access bulk booking management and apply corporate fare rates.",
        "5. Each booking record must contain: pnr (string, 6 alphanumeric), booking_id (UUID), flight_id (FK), passenger details (array), cabin_class (enum: Economy|Business|First), seat_numbers (array), total_fare (decimal), taxes (decimal), and status (enum).",
        "6. The system shall integrate with the GDS (Global Distribution System) Amadeus API for real-time seat availability and fare retrieval.",
        "7. Flight search results must be returned within 3 seconds for any origin-destination pair.",
        "8. The booking flow should be simple and quick for travelers.",
        "9. Seat selection must lock the selected seat for 10 minutes while the customer completes payment; if payment is not completed, the lock must be released and the seat made available again.",
        "10. Only passengers who have completed check-in may access the boarding pass; boarding pass QR codes must expire 30 minutes after the scheduled departure.",
        "11. Baggage allowance rules must be enforced per cabin class and fare type; additional baggage fees must be calculated and added to the total before payment.",
        "12. Flight cancellation by the airline must trigger automatic rebooking offers or full refund options to all affected passengers within 2 hours.",
        "13. The system shall calculate the cheapest available fare combination for multi-city itineraries across all available airlines in the GDS.",
        "14. Online check-in must open 48 hours before scheduled departure and close 1 hour before departure.",
        "15. All customer passport and ID data must be encrypted at rest using AES-256 and transmitted only over TLS 1.3.",
        "16. The system shall enforce IATA name change rules; name corrections of up to 3 characters may be processed by airline staff; full name changes are not permitted on non-refundable tickets.",
        "17. The system should give good deals and discounts to loyal customers.",
        "18. Loyalty points must be credited to the customer's frequent flyer account within 48 hours of flight completion, based on the fare type and distance flown.",
        "19. The system shall generate and submit passenger manifest data to the relevant government authority as required by APIS regulations, 60 minutes before departure.",
        "20. Refund processing for eligible cancellations must be initiated within 24 hours and completed within 7 business days.",
        "21. The system shall support group bookings of 10 or more passengers with negotiated group fares; group booking requests must be reviewed by an airline staff member.",
    ]),

    # ── 11. Legal Case Management System ─────────────────────────────────────
    ("legal-01", "Legal Case Management System — Matter and Document Requirements", [
        "1. The system shall allow attorneys to create legal matters by entering client information, matter type, jurisdiction, opposing counsel details, and relevant court deadlines.",
        "2. When a new matter is created, the system shall generate a unique matter number and notify the assigned paralegal and billing coordinator within 30 minutes.",
        "3. A matter transitions from 'Open' to 'In Litigation' when a court filing is recorded; to 'Settled' when a settlement agreement is uploaded and approved by the partner; to 'Closed' upon final billing reconciliation.",
        "4. Only attorneys with the 'Supervising Partner' role may close a matter; paralegals and associates may update matter details but not change status to 'Closed'.",
        "5. Each matter record must contain: matter_id (UUID), client_id (FK), matter_number (string, unique), matter_type (enum), jurisdiction (string), opened_date (ISO 8601 date), assigned_attorney_id (FK), billable_hours (decimal), and status (enum).",
        "6. The system shall integrate with the court e-filing portal API to submit legal documents directly; submission receipts must be stored against the matter record.",
        "7. Document uploads must complete within 5 seconds for files up to 50 MB.",
        "8. The system should make legal work more organized and efficient.",
        "9. Conflict-of-interest checks must be run automatically when a new client is onboarded; if a conflict is detected, the matter must be flagged and the Supervising Partner notified before the matter can proceed.",
        "10. Only the attorney and paralegal assigned to a matter may view its confidential documents; firm administrators may view metadata only.",
        "11. Each time entry must include: time_entry_id (UUID), matter_id (FK), attorney_id (FK), activity_code (string), description (string, max 1000 characters), hours (decimal, 2 decimal places), billing_rate (decimal), and billable (boolean).",
        "12. The system shall automatically calculate billable fees as: hours * billing_rate for each time entry; invoices must be generated monthly and approved by the billing partner before sending.",
        "13. Court deadline reminders must be sent 30 days, 14 days, 7 days, and 1 day before each deadline to all attorneys and paralegals on the matter.",
        "14. The system shall enforce document version control; every document edit must create a new version; previous versions must be accessible and labeled with editor identity and timestamp.",
        "15. All matter and client records must be retained for 7 years after matter closure in compliance with bar association rules.",
        "16. The system shall generate a utilization report showing billable vs. non-billable hours by attorney for the billing partner every Monday.",
        "17. The system should be helpful for lawyers and their clients.",
        "18. Client intake forms must capture conflict-check fields including client name, opposing party names, and related entity names.",
        "19. The system shall enforce trust accounting rules: client funds in trust accounts must never be commingled with firm operating funds; all trust transactions must be double-entry recorded.",
        "20. Expense entries must capture: expense type, amount, currency, vendor, date, and whether the expense is client-billable.",
        "21. Only a Supervising Partner may write off time entries or reduce an invoice amount by more than 10%.",
    ]),

    # ── 12. Online Learning Platform ──────────────────────────────────────────
    ("elearning-01", "Online Learning Platform — Course and Progress Requirements", [
        "1. The system shall allow instructors to create courses by uploading video lessons, quizzes, assignments, and supplementary materials organized into sections and modules.",
        "2. When a student enrolls in a paid course, the system shall process payment, grant immediate access to course content, and send an enrollment confirmation email.",
        "3. A course transitions from 'Draft' to 'Published' when the instructor submits it for review and an admin approves it; to 'Archived' when the instructor retires it.",
        "4. Only users with the 'Content Admin' role may approve or reject course submissions; instructors may not approve their own courses.",
        "5. Each course record must contain: course_id (UUID), instructor_id (FK), title (string, max 255), description (text), price (decimal), difficulty_level (enum: Beginner|Intermediate|Advanced), language (ISO 639-1), and status (enum).",
        "6. The system shall integrate with Vimeo API for secure video hosting; video playback URLs must be signed and expire after 4 hours.",
        "7. Video lessons must begin playback within 3 seconds of the student clicking play for 95% of requests.",
        "8. Students should be able to learn at their own pace easily.",
        "9. Quiz attempts must be limited to 3 per student per quiz; after 3 failed attempts, the student must wait 24 hours before retrying.",
        "10. Only students who have completed all prerequisite modules may unlock advanced modules; the system must enforce this sequentially.",
        "11. Each quiz submission record must contain: submission_id (UUID), student_id (FK), quiz_id (FK), answers (JSON), score (decimal), passed (boolean), submitted_at (ISO 8601), and attempt_number (integer).",
        "12. Course completion certificates must be auto-generated and emailed to students who achieve a passing score (70% or above) on all course assessments.",
        "13. The system shall track and display video watch progress per lesson; a lesson is marked as 'Completed' only when 90% of the video has been watched.",
        "14. Instructors shall receive 70% of each course sale as royalties; the platform retains 30% commission; payouts must be processed monthly.",
        "15. Course reviews may only be submitted by students who have completed at least 50% of the course content.",
        "16. The system shall recommend courses to students based on their enrolled categories, completion history, and skill level using a collaborative filtering model.",
        "17. The platform should motivate students to keep learning.",
        "18. Student discussion forum posts must be moderated; posts flagged by 3 or more peers must be reviewed by a moderator within 24 hours.",
        "19. The system shall support subtitles in at least 10 languages for all video lessons; subtitle files must be in SRT format.",
        "20. All financial transactions must be logged with instructor_id, course_id, amount, platform_fee, instructor_payout, and transaction_date.",
        "21. Refund requests submitted within 30 days of purchase and with less than 30% of course content consumed must be automatically approved.",
        "22. The system shall send a weekly progress report to enrolled students summarizing lessons completed, quiz scores, and time spent learning.",
        "23. Instructor analytics dashboards must display total enrollments, revenue, average rating, and completion rate per course.",
    ]),

    # ── 13. Telemedicine Platform ─────────────────────────────────────────────
    ("telemedicine-01", "Telemedicine Platform — Virtual Consultation Requirements", [
        "1. The system shall allow patients to book virtual consultations with licensed physicians by selecting specialty, preferred time slot, and consultation type (video, audio, or chat).",
        "2. When a consultation is booked, the system shall send the patient and physician a calendar invite with a unique secure video link 24 hours and 1 hour before the scheduled time.",
        "3. A consultation transitions from 'Scheduled' to 'In Progress' when the physician opens the video room; to 'Completed' when the physician closes the session and submits clinical notes; to 'No Show' if the patient does not join within 10 minutes of the scheduled start.",
        "4. Only licensed physicians with verified credentials may conduct consultations; credential verification must be renewed annually.",
        "5. Each consultation record must contain: consultation_id (UUID), patient_id (FK), physician_id (FK), scheduled_at (ISO 8601), duration_minutes (integer), consultation_type (enum), diagnosis_code (ICD-10), prescription_id (UUID, nullable), and status (enum).",
        "6. The system shall integrate with WebRTC for video and audio streaming; if WebRTC quality degrades below acceptable threshold, the system must notify both parties and offer to switch to audio-only.",
        "7. Video call connection must be established within 5 seconds of both parties joining the room.",
        "8. The system should give patients access to good healthcare.",
        "9. Physicians must complete and lock their consultation notes within 24 hours of session completion; late note completion must be flagged to the medical director.",
        "10. Only the treating physician and the patient's designated care team may view consultation notes; unauthorized access attempts must be logged and flagged.",
        "11. Electronic prescriptions issued during a consultation must be digitally signed by the physician and transmitted to the patient's chosen pharmacy via the e-prescribing network within 5 minutes.",
        "12. The system shall enforce state-specific telehealth prescribing regulations; physicians may not prescribe controlled substances via telemedicine in states where it is prohibited.",
        "13. Patient wait time in the virtual waiting room must not exceed 15 minutes; if exceeded, the patient must be offered a reschedule or a same-day alternate physician.",
        "14. All consultation video recordings (if consented) must be encrypted at rest and at transit; recordings must be retained for 7 years per HIPAA requirements.",
        "15. The system shall generate and deliver itemized billing statements to patients within 24 hours of consultation completion.",
        "16. Insurance eligibility verification must be completed automatically before the consultation starts using the patient's insurance details and the payer verification API.",
        "17. The system should improve access to healthcare in rural areas.",
        "18. The physician availability calendar must reflect real-time slot availability; double-booking must be prevented by the system.",
        "19. Patient consent for the consultation, recording, and data sharing must be obtained and recorded digitally before the session begins.",
        "20. The system shall send prescription pickup reminders to the patient 2 hours after the prescription is transmitted to the pharmacy.",
        "21. Platform uptime must be 99.9% during peak hours (08:00–22:00 local time); scheduled maintenance must be performed between 02:00–04:00.",
    ]),

    # ── 14. Social Media Platform ─────────────────────────────────────────────
    ("socialmedia-01", "Social Media Platform — Content and Community Requirements", [
        "1. The system shall allow registered users to create posts containing text (max 5,000 characters), images (max 10 per post, each up to 10 MB), and videos (max 500 MB per video).",
        "2. When a user publishes a post, the system shall distribute it to all followers' feeds within 30 seconds for accounts with fewer than 10,000 followers.",
        "3. A post transitions from 'Draft' to 'Published' when the user submits it; to 'Flagged' if automated moderation detects a policy violation; to 'Removed' if a moderator confirms the violation.",
        "4. Only users with the 'Content Moderator' role may change a post's status to 'Removed'; automated systems may change status to 'Flagged' only.",
        "5. Each user account record must contain: user_id (UUID), username (string, unique, max 30 characters), email (string, unique), hashed_password (string), date_of_birth (ISO 8601 date), account_status (enum), and created_at (ISO 8601).",
        "6. The system shall integrate with Microsoft Azure Content Moderator API to scan all images and videos for prohibited content within 60 seconds of upload.",
        "7. The news feed must load within 1.5 seconds for 95% of users.",
        "8. The platform should encourage meaningful social interactions.",
        "9. Users under 13 years of age must not be permitted to create accounts; date of birth must be verified at registration.",
        "10. Only account owners and designated administrators may delete posts; deleted posts must be retained in a soft-delete state for 30 days before permanent deletion.",
        "11. Each direct message must contain: message_id (UUID), sender_id (FK), recipient_id (FK), content (encrypted text), sent_at (ISO 8601), read_at (ISO 8601, nullable), and is_deleted (boolean).",
        "12. The recommendation algorithm shall surface content based on the user's interaction history, follow graph, and trending topics within their interest graph.",
        "13. Users must be able to block other users; blocked users must not be able to view the blocker's profile, posts, or send direct messages.",
        "14. Two-factor authentication must be enforced for all accounts with more than 100,000 followers.",
        "15. All direct messages must be encrypted end-to-end; the platform must not have access to message plaintext.",
        "16. The system shall apply rate limiting to all API endpoints: authenticated users may make up to 1,000 requests per hour; unauthenticated requests are limited to 100 per hour.",
        "17. The platform should have good tools for content creators.",
        "18. Hashtags must be indexed in real time; trending hashtags must be recalculated every 15 minutes based on post volume in the past hour.",
        "19. User-generated audio and video content must be scanned for copyright violations using the configured audio fingerprinting service before publication.",
        "20. The system shall provide advertisers with campaign analytics including impressions, click-through rate, engagement rate, and conversion tracking.",
        "21. Account deletion requests must be processed within 30 days; all personal data must be purged in compliance with GDPR Article 17.",
        "22. Stories (ephemeral posts) must automatically expire and be deleted 24 hours after publication.",
    ]),

    # ── 15. Cybersecurity Monitoring System ──────────────────────────────────
    ("cybersec-01", "Cybersecurity Monitoring System — Threat Detection Requirements", [
        "1. The system shall collect and aggregate security event logs from firewalls, IDS/IPS, endpoint agents, and cloud services in real time.",
        "2. When a critical severity alert is triggered, the system shall notify the on-call SOC analyst via PagerDuty within 60 seconds and create an incident ticket in Jira automatically.",
        "3. An alert transitions from 'New' to 'Acknowledged' when a SOC analyst assigns it; to 'In Investigation' when analysis begins; to 'Resolved' when the threat is contained; and to 'False Positive' if determined to be non-threatening.",
        "4. Only 'Senior SOC Analysts' and 'Incident Commanders' may escalate an alert to Critical severity; Tier 1 analysts may update status but not escalate.",
        "5. Each security event record must contain: event_id (UUID), source_system (string), event_type (string), severity (enum: Low|Medium|High|Critical), raw_log (text), detected_at (ISO 8601), and alert_id (FK, nullable).",
        "6. The system shall integrate with threat intelligence feeds (VirusTotal, MISP) to enrich alerts with IOC (Indicator of Compromise) data within 30 seconds of alert creation.",
        "7. Log ingestion pipeline must handle at least 100,000 events per second without dropping events.",
        "8. The system should make the organization more secure.",
        "9. Threat correlation rules shall be evaluated in real time; a rule triggering more than 100 false positives per day shall be automatically disabled and flagged for review.",
        "10. Only Incident Commanders may authorize isolation of a compromised host from the network; all other roles may recommend isolation but not execute it.",
        "11. Each incident record must contain: incident_id (UUID), severity (enum), affected_systems (array of strings), attack_vector (MITRE ATT&CK TTP code), discovered_at (ISO 8601), and remediation_steps (text).",
        "12. The SIEM shall retain hot storage (queryable) logs for 90 days and cold storage archives for 7 years in compliance with SOC 2 Type II requirements.",
        "13. Anomaly detection models must be retrained weekly using the past 30 days of labeled event data; retraining must not degrade detection accuracy below the established baseline.",
        "14. The system shall generate a weekly threat landscape report summarizing top attack vectors, alert volumes by severity, mean time to detect (MTTD), and mean time to respond (MTTR).",
        "15. All analyst actions on alerts and incidents must be audit-logged with actor identity, timestamp, and change details; logs must be immutable.",
        "16. The system shall support playbook automation; when a known attack pattern is detected, the configured automated response playbook must execute within 5 minutes.",
        "17. The system should have good dashboards for security teams.",
        "18. Vulnerability scan results from integrated scanners must be correlated with active assets and prioritized using CVSS scores.",
        "19. The system shall enforce role-based access control; analysts may only access logs and alerts for assets within their assigned scope.",
        "20. Incident post-mortem reports must be completed within 5 business days of incident resolution and reviewed by the CISO.",
    ]),

    # ── 16. Logistics and Shipping Platform ───────────────────────────────────
    ("logistics-01", "Logistics and Shipping Platform — Shipment Tracking Requirements", [
        "1. The system shall allow shippers to create shipment records by entering sender and receiver addresses, package dimensions, weight, declared value, and service type.",
        "2. When a shipment label is generated, the system shall assign a unique tracking number and transmit the shipment manifest to the assigned carrier within 2 minutes.",
        "3. A shipment transitions from 'Label Created' to 'Picked Up' upon carrier scan; to 'In Transit' at each intermediate scan point; to 'Out for Delivery' at the destination facility; and to 'Delivered' upon recipient signature or delivery confirmation scan.",
        "4. Only 'Fleet Coordinators' and 'Dispatch Managers' may reassign a shipment to a different carrier after the label is created.",
        "5. Each shipment record must contain: tracking_number (string, unique, 18 characters), shipper_id (FK), receiver_address (JSON), package_weight_kg (decimal), dimensions_cm (JSON with L/W/H), declared_value (decimal), service_type (enum: Standard|Express|Overnight), and status (enum).",
        "6. The system shall integrate with FedEx, UPS, and DHL APIs to retrieve real-time carrier tracking events and synchronize status every 15 minutes.",
        "7. Shipment tracking status must be updated within 10 minutes of a carrier scan event.",
        "8. The system should make shipping easy for businesses.",
        "9. Dimensional weight must be calculated as (L * W * H) / 5000 and billed at the higher of actual weight or dimensional weight.",
        "10. Only verified business accounts may access bulk shipment creation (more than 50 shipments per batch); individual accounts are limited to 10 per batch.",
        "11. Each customs declaration record for international shipments must include: HS code, country of origin, description of goods, quantity, and declared value in USD.",
        "12. The system shall automatically generate customs documents (Commercial Invoice, Packing List) for international shipments and attach them to the shipment record.",
        "13. Delivery exception alerts (e.g., address not found, recipient unavailable) must be sent to the shipper within 30 minutes of the exception being logged by the carrier.",
        "14. The system shall enforce carrier-specific size and weight limits; shipments exceeding limits must be flagged and require manual carrier confirmation.",
        "15. Proof of delivery (POD) records (recipient signature image, timestamp, GPS coordinates) must be stored and accessible to the shipper within 2 hours of delivery.",
        "16. The system shall generate a monthly shipment volume and cost report by service type, carrier, and destination region.",
        "17. The system should help reduce shipping costs.",
        "18. Insurance claims for lost or damaged shipments must be submitted through the platform within 60 days of the estimated delivery date.",
        "19. The system shall support return shipment generation; return labels must be pre-paid and generated within 5 minutes of a return request.",
        "20. All address data must be validated against the national postal address database before shipment creation; invalid addresses must return a descriptive error.",
        "21. The system shall track carrier on-time delivery performance per route and generate a quarterly carrier scorecard for procurement review.",
    ]),

    # ── 17. Government Tax Portal ─────────────────────────────────────────────
    ("taxporal-01", "Government Tax Filing Portal — Submission and Assessment Requirements", [
        "1. The system shall allow registered taxpayers to file annual income tax returns online by entering income sources, deductions, exemptions, and uploading supporting documents.",
        "2. When a tax return is submitted, the system shall validate completeness and consistency of the data and send an acknowledgment with a submission reference number within 10 minutes.",
        "3. A tax return transitions from 'Submitted' to 'Under Processing' when assigned to an assessor; to 'Assessment Issued' when the tax liability is computed; to 'Objection Filed' if the taxpayer disputes the assessment; and to 'Finalized' upon agreement or adjudication.",
        "4. Only 'Tax Assessors' may issue formal tax assessments; 'Tax Officers' may process routine returns but must escalate complex cases.",
        "5. Each tax return record must contain: return_id (UUID), taxpayer_id (FK), tax_year (integer), filing_date (ISO 8601 date), total_income (decimal), total_deductions (decimal), taxable_income (decimal), tax_liability (decimal), and status (enum).",
        "6. The system shall integrate with the national financial institution reporting API to pre-populate interest and dividend income fields using bank-reported data.",
        "7. Tax calculation engine must compute liability for any return within 5 seconds.",
        "8. The system should make tax filing easier for ordinary citizens.",
        "9. Taxpayers who miss the filing deadline must be automatically assessed a late filing penalty calculated at 5% of unpaid tax per month, up to a maximum of 25%.",
        "10. Only a 'Senior Tax Assessor' may approve waivers for late filing penalties; standard assessors may not grant waivers.",
        "11. Each assessment record must contain: assessment_id (UUID), return_id (FK), assessor_id (FK), assessed_tax (decimal), penalty (decimal), interest (decimal), total_due (decimal), and issued_at (ISO 8601).",
        "12. The system shall calculate interest on overdue tax at the statutory rate (currently 1% per month) compounding monthly from the original due date.",
        "13. Tax refunds due to taxpayers must be processed and credited to the registered bank account within 30 business days of assessment finalization.",
        "14. The system shall enforce audit selection rules; returns with deductions exceeding 30% of gross income must be flagged for mandatory audit.",
        "15. All taxpayer records and return data must be retained for 10 years in compliance with the Revenue Code.",
        "16. Objections to assessments must be submitted within 30 days of the assessment date; the system must enforce this deadline and reject late objections.",
        "17. The system should help the government collect the right amount of taxes.",
        "18. The system shall generate an annual tax collection report by income bracket, industry sector, and geographic region for the Finance Ministry.",
        "19. All access to taxpayer financial records must be logged with assessor identity, timestamp, and purpose; unauthorized access must trigger an immediate alert.",
        "20. The system shall send payment due reminders 30 days, 14 days, and 3 days before the tax payment deadline.",
        "21. The e-payment gateway must accept bank transfers, credit/debit cards, and government payment vouchers; payments must be reconciled against the taxpayer account within 1 business day.",
    ]),

    # ── 18. Restaurant POS System ─────────────────────────────────────────────
    ("restaurant-pos-01", "Restaurant Point-of-Sale System — Order and Billing Requirements", [
        "1. The system shall allow servers to create table orders by selecting menu items, specifying quantities, and adding modifiers (e.g., 'no onions', 'extra sauce').",
        "2. When an order is submitted by a server, the system shall print kitchen tickets on the appropriate kitchen display system (KDS) or kitchen printer within 5 seconds.",
        "3. An order transitions from 'Open' to 'Sent to Kitchen' when submitted; to 'Ready' when the kitchen marks it complete; to 'Served' when the server confirms delivery to the table; and to 'Paid' upon settlement.",
        "4. Only users with the 'Manager' role may void items or apply discounts exceeding 20% to an order.",
        "5. Each order record must contain: order_id (UUID), table_number (integer), server_id (FK), items (JSON array with item_id, quantity, modifiers, unit_price), subtotal (decimal), tax (decimal), total (decimal), and status (enum).",
        "6. The system shall integrate with the inventory management system via API to decrement ingredient stock quantities in real time as orders are placed.",
        "7. Kitchen order ticket printing must complete within 3 seconds of order submission.",
        "8. The POS system should make service faster for customers.",
        "9. Split billing must support splitting the total equally among up to 8 guests or splitting by individual item selection; each split must be settled independently.",
        "10. Only the 'Cashier' and 'Manager' roles may process payments; servers may take orders but may not access the payment screen.",
        "11. Each payment record must contain: payment_id (UUID), order_id (FK), payment_method (enum: Cash|Card|Voucher|Mobile), amount_paid (decimal), change_given (decimal, applicable for cash), and processed_at (ISO 8601).",
        "12. The system shall calculate tax based on the configured tax profile per menu category; mixed-tax orders must be itemized per tax rate on the receipt.",
        "13. Happy hour pricing must be enforced automatically between configured times; the system must revert to standard pricing outside happy hour without manual intervention.",
        "14. The end-of-day (EOD) report must reconcile total orders, total revenue by payment method, voids, discounts, and tips; it must be available within 5 minutes of day close.",
        "15. The system shall operate in offline mode for up to 4 hours if the internet connection is lost; all offline transactions must sync to the central system when connectivity is restored.",
        "16. Menu items marked as 'Out of Stock' must be visually indicated on the POS screen and must not be orderable.",
        "17. The system should help the restaurant make more profit.",
        "18. Loyalty points must be credited to the customer's account at the rate of 1 point per $1 spent after payment is processed.",
        "19. The system shall support reservations; reserved tables must be blocked on the floor map for the reservation period plus 15 minutes.",
        "20. All financial transactions must be logged with server_id, manager_id (if override applied), timestamp, and amount for audit purposes.",
    ]),

    # ── 19. Healthcare Patient Portal ─────────────────────────────────────────
    ("healthportal-01", "Healthcare Patient Portal — Health Records and Communication Requirements", [
        "1. The system shall allow patients to view their medical history, lab results, medication lists, and immunization records through a secure online portal.",
        "2. When a lab result is published by the laboratory, the system shall notify the ordering physician within 5 minutes and make the result visible to the patient after the physician reviews it.",
        "3. A lab result transitions from 'Pending' to 'Available to Physician' when published; to 'Released to Patient' when the physician marks it reviewed; to 'Critcal Value Alerted' if the result is flagged as critical by the lab.",
        "4. Only the treating physician and care team members assigned to the patient may access full medical records; patients may access their own records but not modify them.",
        "5. Each lab result record must contain: result_id (UUID), patient_id (FK), ordering_physician_id (FK), test_code (LOINC), result_value (string), reference_range (string), unit (string), collected_at (ISO 8601), and status (enum).",
        "6. The system shall integrate with the HL7 FHIR API of connected hospital systems to retrieve and synchronize patient records.",
        "7. Patient portal page load time must not exceed 2 seconds for 95% of authenticated users.",
        "8. The portal should help patients understand their health better.",
        "9. Critical lab values must trigger an immediate phone call to the ordering physician via the automated calling system in addition to in-system notification.",
        "10. Only patients who have provided electronic consent for record sharing may have their records shared with external providers via the patient portal.",
        "11. Each secure message between patient and physician must contain: message_id (UUID), sender_id (FK), recipient_id (FK), subject (string), body (encrypted text), sent_at (ISO 8601), and is_read (boolean).",
        "12. The system shall enforce a maximum response time commitment for physician replies to patient messages: routine messages within 2 business days; urgent messages within 4 hours.",
        "13. Prescription refill requests submitted via the portal must be routed to the prescribing physician for approval; approved refills must be transmitted to the pharmacy within 30 minutes.",
        "14. The system shall allow patients to schedule follow-up appointments directly through the portal; scheduling must check real-time physician availability.",
        "15. All PHI (Protected Health Information) must be handled in compliance with HIPAA; all data access events must be audit-logged.",
        "16. Patient consent forms must be versioned; when a new version is published, all patients must re-acknowledge consent before accessing the portal.",
        "17. The system should make healthcare more convenient.",
        "18. The system shall send automated appointment reminders 48 hours and 2 hours before each appointment via the patient's preferred communication channel (SMS, email, or push notification).",
        "19. The portal must support accessibility standards (WCAG 2.1 AA) to ensure usability for patients with disabilities.",
        "20. Health summary exports must be available in FHIR JSON and PDF formats; exports must be generated within 60 seconds.",
        "21. The system shall generate monthly population health reports for enrolled physician practices, summarizing patient adherence rates, chronic condition management metrics, and preventive care completion.",
    ]),

    # ── 20. Supply Chain Management System ────────────────────────────────────
    ("supplychain-01", "Supply Chain Management System — Procurement and Supplier Requirements", [
        "1. The system shall allow procurement officers to create purchase orders by selecting items from the approved vendor catalog, specifying quantities, delivery dates, and shipping addresses.",
        "2. When a purchase order is approved, the system shall transmit it to the supplier via EDI or email within 15 minutes and record the expected delivery date.",
        "3. A purchase order transitions from 'Draft' to 'Pending Approval' when submitted; to 'Approved' when authorized; to 'Sent to Supplier' once transmitted; to 'Partially Received' when some items arrive; and to 'Fully Received' when all items are received.",
        "4. Only the 'Procurement Manager' or 'CFO' may approve purchase orders exceeding $100,000.",
        "5. Each purchase order record must contain: po_id (UUID), supplier_id (FK), line_items (JSON array), total_value (decimal), currency (ISO 4217), requested_delivery_date (ISO 8601 date), approved_by (FK, nullable), and status (enum).",
        "6. The system shall integrate with supplier EDI systems using the EDIFACT X12 850 standard for purchase order transmission.",
        "7. Purchase order approval workflows must route to the correct approver within 5 minutes of submission.",
        "8. The system should help the company save money on procurement.",
        "9. Three-way matching must be enforced before invoice payment: the invoice must match the purchase order and the goods receipt within a 5% tolerance.",
        "10. Only approved vendors on the vendor master list may receive purchase orders; new vendors must complete a qualification process before being added to the master list.",
        "11. Each supplier record must contain: supplier_id (UUID), company_name (string), contact_email (string), payment_terms (string), currency (ISO 4217), tax_id (string), and compliance_status (enum: Qualified|Probation|Disqualified).",
        "12. The system shall track supplier delivery performance: on-time delivery rate, order accuracy rate, and defect rate; suppliers with on-time delivery below 85% must be flagged for review.",
        "13. Inventory replenishment orders must be triggered automatically when stock falls below the safety stock level defined per SKU.",
        "14. The system shall calculate total cost of ownership (TCO) for each supplier per category, including unit price, freight, duties, and quality costs.",
        "15. Goods receipt notes must be created within 24 hours of physical goods arrival; late GRNs must be flagged to the warehouse manager.",
        "16. All procurement documents must be retained for 7 years in compliance with corporate audit requirements.",
        "17. The system should improve supplier relationships.",
        "18. The system shall generate a monthly spend analysis report by supplier, category, and cost center for the finance team.",
        "19. Contract expiry alerts must be sent to the procurement team 90 days, 60 days, and 30 days before each supplier contract expiration date.",
        "20. The system shall enforce budget controls; purchase orders that would exceed the approved budget for a cost center must be flagged and require CFO approval.",
        "21. Supplier invoices must be processed and approved within 15 business days; invoices outstanding beyond this must trigger an escalation alert.",
    ]),

    # ── 21. Real Estate Property Management ──────────────────────────────────
    ("realestate-01", "Real Estate Property Management System — Lease and Tenant Requirements", [
        "1. The system shall allow property managers to list rental units by entering property address, unit number, floor area, rent amount, available date, and amenities.",
        "2. When a tenant application is received, the system shall send an acknowledgment within 30 minutes and initiate background check and credit screening automatically.",
        "3. A lease transitions from 'Draft' to 'Active' upon tenant signature and receipt of security deposit; to 'Expiring' 60 days before end date; to 'Expired' on end date if not renewed; and to 'Terminated' upon early termination.",
        "4. Only the 'Property Manager' role may set or change rent amounts; 'Leasing Agents' may create listings but may not modify financial terms.",
        "5. Each lease record must contain: lease_id (UUID), unit_id (FK), tenant_id (FK), start_date (ISO 8601 date), end_date (ISO 8601 date), monthly_rent (decimal), security_deposit (decimal), and status (enum).",
        "6. The system shall integrate with Equifax and TransUnion credit bureaus for automated tenant credit screening.",
        "7. Rent payment reminders must be sent 5 days before the due date via email and SMS.",
        "8. The system should make property management easier and less stressful.",
        "9. Late rent payments must automatically generate a late fee of 5% of monthly rent after 5 calendar days of non-payment.",
        "10. Only tenants with an active lease may submit maintenance requests through the portal; prospective tenants may not access the maintenance module.",
        "11. Each maintenance request must contain: request_id (UUID), unit_id (FK), tenant_id (FK), description (text), priority (enum: Emergency|High|Medium|Low), submitted_at (ISO 8601), and status (enum).",
        "12. Emergency maintenance requests must be dispatched to an on-call maintenance technician within 15 minutes of submission.",
        "13. The system shall calculate and process monthly rent charges, late fees, and utility reimbursements automatically on the 1st of each month.",
        "14. Security deposit refund processing must be initiated within 21 days of lease termination in compliance with local tenancy law.",
        "15. All lease documents must be digitally signed using a certified e-signature provider; wet signatures are not accepted.",
        "16. The system shall generate an owner statement monthly for each property, detailing rent collected, maintenance expenses, management fees, and net owner distribution.",
        "17. The system should help landlords maximize rental income.",
        "18. Prospective tenants must pass credit score (minimum 650), background check (no felony convictions), and income verification (gross income 3x monthly rent) to be approved.",
        "19. Maintenance vendor invoices must be three-way matched against the work order and purchase order before payment approval.",
        "20. The system shall enforce lease renewal workflows: the tenant must be offered renewal terms 90 days before lease expiry; non-response after 30 days must trigger escalation.",
        "21. Utility submetering data must be integrated from smart meters; tenant utility bills must be calculated and issued within 3 business days of meter read.",
    ]),

    # ── 22. Healthcare Drug Inventory Management ──────────────────────────────
    ("pharma-01", "Pharmaceutical Drug Inventory Management — Controlled Substance Requirements", [
        "1. The system shall allow licensed pharmacists to receive, dispense, and return controlled and non-controlled medications with full chain-of-custody recording.",
        "2. When a controlled substance is dispensed, the system shall record the patient name, prescribing physician DEA number, prescription number, quantity dispensed, and dispensing pharmacist ID within the transaction.",
        "3. Controlled substance inventory transitions from 'Ordered' to 'In Transit' upon shipping confirmation; to 'Received' upon physical receipt and count verification; to 'Available' after quality check; to 'Dispensed' per individual dispense transaction.",
        "4. Only pharmacists with a valid DEA registration may receive, count, or dispense Schedule II controlled substances.",
        "5. Each dispense transaction record must contain: transaction_id (UUID), rx_number (string), patient_id (FK), prescriber_dea (string), drug_ndc (string, 11 digits), quantity (integer), dispense_date (ISO 8601), pharmacist_id (FK), and lot_number (string).",
        "6. The system shall integrate with the state Prescription Drug Monitoring Program (PDMP) API to query and submit dispense records for controlled substances in real time.",
        "7. PDMP submission must complete within 60 seconds of dispense transaction creation.",
        "8. The system should help pharmacies manage their drug inventory efficiently.",
        "9. Schedule II controlled substances must be counted by two pharmacists; both must confirm the count in the system before the inventory record is accepted.",
        "10. Only a Pharmacist-in-Charge may authorize write-offs for damaged, expired, or stolen controlled substances; write-off records must include DEA Form 41 data.",
        "11. Each controlled substance inventory record must contain: inventory_id (UUID), drug_ndc (string), lot_number (string), expiry_date (ISO 8601 date), quantity_on_hand (integer), storage_location (string), and last_count_date (ISO 8601).",
        "12. The system shall enforce quantity limits for controlled substance dispensing per prescription; quantities exceeding the prescription limit must be rejected.",
        "13. Automated alerts must be sent when any controlled substance's stock falls below the configured minimum level or when stock exceeds the maximum permitted quantity.",
        "14. All controlled substance transactions must be reconcilable to within a zero-variance tolerance; any discrepancy must trigger an immediate investigation workflow.",
        "15. The system must generate DEA ARCOS-format reports for Schedule I and II drugs monthly and transmit them to the DEA reporting endpoint.",
        "16. Expired medications must be segregated automatically by the system 30 days before expiry; disposal must be documented and submitted to the DEA within 30 days of disposal.",
        "17. The system should handle all types of medications properly.",
        "18. Drug-drug interaction checking must be performed at dispense time using the configured clinical decision support engine; critical interactions must block dispense and require pharmacist override with documented reason.",
        "19. The system shall support perpetual inventory tracking; every receipt, dispense, return, and adjustment must update the perpetual balance in real time.",
        "20. Annual physical inventory counts for controlled substances must be conducted within 2 years of the previous count as required by DEA regulations; the system shall schedule and track this.",
        "21. Patient counseling records must document that the pharmacist provided drug usage instructions and potential side effects; this must be captured per dispense transaction.",
    ]),

    # ── 23. Cloud Infrastructure Management Platform ──────────────────────────
    ("cloudinfra-01", "Cloud Infrastructure Management Platform — Provisioning and Governance Requirements", [
        "1. The system shall allow platform engineers to provision cloud resources (VMs, databases, object storage, VPCs) across AWS, GCP, and Azure through a unified self-service portal.",
        "2. When a resource provisioning request is submitted, the system shall validate the request against the organizational policy engine and provision the resource within 10 minutes if approved.",
        "3. A provisioning request transitions from 'Submitted' to 'Policy Check' upon submission; to 'Approved' if policy checks pass; to 'Rejected' if any policy violation is detected; to 'Provisioning' once approved; and to 'Active' when the resource is ready.",
        "4. Only 'Platform Architects' may create or modify the organizational cloud policies; 'Engineers' may submit provisioning requests but may not override policy controls.",
        "5. Each resource record must contain: resource_id (UUID), cloud_provider (enum: AWS|GCP|Azure), resource_type (string), region (string), owner_team (string), cost_center (string), provisioned_at (ISO 8601), and status (enum).",
        "6. The system shall integrate with the cloud providers' billing APIs to pull daily cost data per resource and aggregate it by team and cost center.",
        "7. Resource provisioning must be idempotent; re-submitting an identical request must not create duplicate resources.",
        "8. The platform should help engineering teams be more productive.",
        "9. Resources left idle for more than 30 days must be automatically flagged; the owning team must justify continued use or the resource must be terminated.",
        "10. Only resources tagged with mandatory tags (environment, team, cost_center, project) may be provisioned; untagged resources must be rejected by the policy engine.",
        "11. Each cost anomaly alert must include: alert_id (UUID), resource_id (FK), expected_daily_cost (decimal), actual_daily_cost (decimal), deviation_percent (decimal), and detected_at (ISO 8601).",
        "12. The system shall enforce cloud spending budgets per team and per project; provisioning requests that would exceed the quarterly budget must require CFO approval.",
        "13. All secrets and API keys must be stored in the integrated secrets manager (HashiCorp Vault); secrets must never be stored in resource configurations or code repositories.",
        "14. Disaster recovery requirements must be enforced at provisioning: production resources must be provisioned in at least 2 availability zones; single-AZ provisioning for production is blocked.",
        "15. The system shall generate a weekly cost optimization report identifying over-provisioned instances, unused resources, and savings recommendations.",
        "16. All API calls to cloud provider APIs must be logged in the audit trail with caller identity, resource ID, action, and timestamp.",
        "17. The system should reduce cloud costs for the organization.",
        "18. Resource decommissioning must follow a defined workflow: request, approval, backup, decommission, and confirmation; each step must be recorded.",
        "19. The system shall support infrastructure-as-code (IaC) templates in Terraform and Pulumi; all provisioned resources must have an associated IaC configuration stored in version control.",
        "20. Security groups and firewall rules must be validated against the security baseline before provisioning; rules permitting unrestricted public access (0.0.0.0/0) to sensitive ports must be blocked.",
    ]),

    # ── 24. Event Management Platform ────────────────────────────────────────
    ("eventmgmt-01", "Event Management Platform — Registration and Ticketing Requirements", [
        "1. The system shall allow event organizers to create events by entering event name, description, venue, date, time, ticket types, and pricing.",
        "2. When an attendee registers for a paid event, the system shall process payment, generate a unique QR code ticket, and send a confirmation email within 2 minutes.",
        "3. A ticket transitions from 'Reserved' to 'Purchased' upon payment confirmation; to 'Checked In' when scanned at the event gate; to 'Cancelled' if the attendee cancels; and to 'Refunded' upon successful refund.",
        "4. Only users with the 'Event Organizer' role may create, edit, cancel, or transfer event ownership; 'Staff' roles may manage check-in operations only.",
        "5. Each ticket record must contain: ticket_id (UUID), event_id (FK), attendee_id (FK), ticket_type (string), qr_code (string, unique), purchase_price (decimal), purchased_at (ISO 8601), and status (enum).",
        "6. The system shall integrate with Stripe and PayPal for payment processing; the organizer may configure their preferred gateway per event.",
        "7. QR code scanning at event check-in must validate and update status within 1 second.",
        "8. Event registration should be quick and easy for attendees.",
        "9. Waitlist functionality must activate automatically when an event reaches 100% ticket capacity; waitlisted attendees must be offered available tickets within 15 minutes of a cancellation.",
        "10. Only organizers with a verified bank account may receive payouts; payout must be processed within 5 business days of event completion.",
        "11. Each event record must contain: event_id (UUID), organizer_id (FK), name (string, max 255), venue_address (JSON), start_datetime (ISO 8601), end_datetime (ISO 8601), capacity (integer), and status (enum: Draft|Published|Cancelled|Completed).",
        "12. Event cancellation by the organizer must trigger automatic full refunds to all ticket holders within 5 business days.",
        "13. The system shall enforce ticket transfer rules: tickets may be transferred to another attendee up to 24 hours before the event; the transferee must register on the platform.",
        "14. Discount codes must be validated at checkout; the maximum discount per ticket must not exceed 50% of the face value.",
        "15. All event financial data must be retained for 7 years for tax and audit compliance.",
        "16. The system shall generate a post-event analytics report: total registrations, check-in rate, revenue by ticket type, and attendee satisfaction survey summary.",
        "17. The system should help organizers create successful events.",
        "18. Attendee data (name, email, dietary preferences) must be exportable by organizers in CSV format per event; the export must complete within 30 seconds.",
        "19. The system shall support recurring events; organizers may define a recurrence pattern and the system shall auto-create event instances for the next 12 months.",
        "20. On-site badge printing must be triggered automatically upon successful QR code scan at designated badge printing stations.",
        "21. The platform must provide a live attendee count dashboard visible to event staff, updating in real time as check-ins occur.",
    ]),

    # ── 25. Project Management Tool ───────────────────────────────────────────
    ("projectmgmt-01", "Project Management Tool — Task and Workflow Requirements", [
        "1. The system shall allow project managers to create projects by specifying project name, description, start date, target end date, budget, and assigning team members.",
        "2. When a task is assigned to a team member, the system shall send a notification via email and in-app within 60 seconds of assignment.",
        "3. A task transitions from 'Backlog' to 'In Progress' when a team member begins work; to 'In Review' when submitted for review; to 'Done' when the reviewer approves; and to 'Blocked' when an impediment is logged.",
        "4. Only 'Project Managers' and 'Product Owners' may move tasks to 'Done'; team members may only move tasks to 'In Review'.",
        "5. Each task record must contain: task_id (UUID), project_id (FK), title (string, max 255), description (text), assignee_id (FK, nullable), priority (enum: Critical|High|Medium|Low), story_points (integer), due_date (ISO 8601 date), and status (enum).",
        "6. The system shall integrate with GitHub and GitLab APIs to link commits and pull requests to tasks; merged PRs must automatically transition the linked task to 'In Review'.",
        "7. The Kanban board must load within 2 seconds for boards with up to 500 tasks.",
        "8. The tool should help teams collaborate more effectively.",
        "9. Sprint planning must enforce velocity limits: the total story points planned per sprint must not exceed 110% of the team's average velocity over the last 3 sprints.",
        "10. Only team members assigned to the project may view project data; guests may view a read-only project summary if explicitly granted access by the project manager.",
        "11. Each sprint record must contain: sprint_id (UUID), project_id (FK), name (string), start_date (ISO 8601 date), end_date (ISO 8601 date), goal (text), planned_points (integer), and completed_points (integer).",
        "12. Burndown charts must be calculated nightly and be accessible in the project analytics dashboard.",
        "13. The system shall send daily standup reminders to all active team members at a configured time and collect async status updates through a structured form.",
        "14. Blocked tasks must generate an escalation notification to the project manager if the impediment is not resolved within 2 business days.",
        "15. All project data must be exportable in JIRA-compatible JSON format for migration purposes.",
        "16. The system shall calculate project health metrics: schedule variance (SV), cost performance index (CPI), and completion percentage, updated daily.",
        "17. The tool should make project reporting less time-consuming.",
        "18. Time tracking entries must capture: entry_id (UUID), task_id (FK), team_member_id (FK), hours (decimal, 2 decimal places), date (ISO 8601 date), and description (text).",
        "19. The system shall enforce working hour limits: no team member may log more than 12 hours per day in the time tracking system; entries exceeding this must be flagged.",
        "20. Resource allocation reports must show each team member's planned vs. actual hours per sprint, available capacity, and allocation percentage.",
        "21. The system shall support dependency mapping between tasks; circular dependencies must be detected and rejected by the system.",
        "22. Retrospective action items must be tracked as tasks in the following sprint; completion rate of retrospective actions must be reported in the sprint review dashboard.",
    ]),
]


# ─────────────────────────────────────────────────────────────────────────────
# WRITE .txt FILES
# ─────────────────────────────────────────────────────────────────────────────

import pathlib

OUTPUT_DIR = pathlib.Path(__file__).parent.parent / "data" / "sample_requirements"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_txt_files():
    for slug, title, reqs in DOCUMENTS:
        out_path = OUTPUT_DIR / f"{slug}.txt"
        lines = [title, "", "Functional Requirements", ""]
        lines.extend(reqs)
        lines.append("")
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  Written: {out_path.name}  ({len(reqs)} requirements)")
    print(f"\n[OK] {len(DOCUMENTS)} files written to {OUTPUT_DIR}\n")


# ─────────────────────────────────────────────────────────────────────────────
# INGEST ALL FILES INTO DATABASE
# ─────────────────────────────────────────────────────────────────────────────

def ingest_all():
    """Ingest every .txt file in the output directory into the SpecForge DB."""
    from specforge.ingestion.service import ingest_document
    from specforge.preprocessing.service import preprocess_requirement
    from specforge.classification.service import classify_and_store
    from specforge.ambiguity.service import detect_and_store
    from specforge.db.session import get_session
    from specforge.db.models import Requirement
    from sqlalchemy import select

    total_units = 0
    total_docs = 0
    errors = []

    for slug, title, reqs in DOCUMENTS:
        txt_path = OUTPUT_DIR / f"{slug}.txt"
        print(f"Ingesting [{slug}] ...")
        try:
            # Check if already ingested
            with get_session() as session:
                existing = session.execute(
                    select(Requirement).where(Requirement.source_doc_id == slug).limit(1)
                ).scalars().first()

            if existing is not None:
                print(f"  [SKIP] Already ingested: {slug}")
                total_docs += 1
                continue

            # Step 1: ingest raw document -> 1 Requirement row (raw_text = whole file)
            raw_req = ingest_document(file_path=str(txt_path), source_doc_id=slug)
            print(f"  [1/3] Raw document ingested (id={raw_req.requirement_id})")

            # Step 2: preprocess -> split into atomic units
            unit_reqs = preprocess_requirement(requirement_id=raw_req.requirement_id)
            n = len(unit_reqs)
            print(f"  [2/3] Segmented into {n} atomic units.")

            # Step 3: classify and detect ambiguity for each unit
            ok = 0
            for unit in unit_reqs:
                try:
                    classify_and_store(requirement_id=unit.requirement_id)
                    detect_and_store(requirement_id=unit.requirement_id)
                    ok += 1
                except Exception as e:
                    errors.append(f"{slug} unit#{unit.requirement_id[:8]}: {e}")

            total_units += ok
            total_docs += 1
            print(f"  [3/3] Classified and scored {ok}/{n} units. [OK]\n")

        except Exception as e:
            errors.append(f"{slug}: {e}")
            print(f"  [ERROR] {slug}: {e}\n")

    print(f"\n{'='*60}")
    print(f"Ingestion complete.")
    print(f"  Documents processed : {total_docs}")
    print(f"  Atomic units stored : {total_units}")
    if errors:
        print(f"  Errors ({len(errors)}):")
        for err in errors:
            print(f"    - {err}")
    print(f"{'='*60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SpecForge AI — Synthetic Data Generator")
    print("=" * 60)

    print("\n[Step 1] Writing .txt requirement files...")
    write_txt_files()

    print("[Step 2] Ingesting into database...")
    ingest_all()

    print("[Done] Synthetic data generation complete.")
