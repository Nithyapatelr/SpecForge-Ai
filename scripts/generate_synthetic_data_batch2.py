"""
generate_synthetic_data_batch2.py
---------------------------------
Batch 2: Generates 10 additional synthetic requirement documents across
new domains, writes them as .txt files, and ingests them into the DB.

Usage:
    C:\\Python314\\python.exe scripts\\generate_synthetic_data_batch2.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOCUMENTS = [

    # ── 1. Online Gaming Platform ────────────────────────────────────────────
    ("gaming-01", "Online Gaming Platform — Multiplayer & Matchmaking Requirements", [
        "1. The system shall allow players to create an account using email, Google, or Discord OAuth, storing a unique gamer tag of 3-20 alphanumeric characters.",
        "2. When a player queues for a ranked match, the matchmaking engine shall pair players within 200 MMR points and start the lobby within 30 seconds for 95% of requests.",
        "3. A match transitions from 'Lobby' to 'In Progress' when all players confirm readiness; from 'In Progress' to 'Completed' when a win condition is met; and from 'In Progress' to 'Abandoned' if fewer than 2 players remain for over 60 seconds.",
        "4. Only users with the 'Game Moderator' role shall be permitted to issue temporary bans, mute players, or review reported chat logs.",
        "5. Each match record must contain: match_id (UUID), game_mode (enum: Ranked|Casual|Tournament), player_ids (array of UUIDs), map_name (string), start_time (ISO 8601), end_time (ISO 8601), winner_team_id (UUID, nullable), and final_scores (JSON object).",
        "6. The system shall integrate with Steam and Epic Games Store APIs for cross-platform friend list synchronization; if either API is unavailable, the system shall display cached friend data up to 24 hours old.",
        "7. The game client shall render frames at a minimum of 60 FPS on medium-quality settings for hardware meeting the published minimum specifications.",
        "8. The system should provide a fun and engaging gaming experience for all players.",
        "9. When a player disconnects during a ranked match, the system shall hold their slot for 120 seconds; if the player does not reconnect within this window, a loss is recorded for the disconnected player and the match continues.",
        "10. Only a 'Tournament Admin' may create, modify, or cancel tournament brackets; 'Players' may register and view bracket progress but not alter it.",
        "11. The leaderboard must update within 10 seconds of a ranked match completing and reflect global, regional, and friend-only views.",
        "12. The in-game voice chat latency must not exceed 80ms one-way for players in the same geographic region.",
        "13. Anti-cheat scans shall run in a sandboxed kernel-level driver and report violations to the server within 5 seconds; confirmed violations result in automatic session termination.",
        "14. The in-game store shall apply promotional discounts only during the configured promotion window; discounts must never reduce the final price below the configured floor price.",
        "15. The system should handle a lot of players at once without problems.",
        "16. Player inventory items must be stored as a typed JSON array with fields: item_id (UUID), item_type (enum: Skin|Weapon|Emote|Currency), acquired_date (ISO 8601), and tradeable (boolean).",
        "17. If a player reports another player for abusive chat, the system shall log the last 50 chat messages in that match session and flag the report for moderator review within 24 hours.",
        "18. The system shall generate weekly engagement analytics reports containing DAU, MAU, session length distribution, and retention cohort data, deposited in the analytics S3 bucket by Monday 04:00 UTC.",
        "19. All player passwords must be stored using Argon2id hashing with a minimum memory cost of 64MB; plaintext passwords must never be persisted.",
        "20. The system shall support hot-patching of game balance parameters (damage values, cooldowns, spawn rates) without requiring a full client update or server restart.",
        "21. Replay files shall be stored for 30 days and be downloadable by any match participant; after 30 days, replays are archived to cold storage.",
    ]),

    # ── 2. FinTech Payment Gateway ───────────────────────────────────────────
    ("fintech-01", "FinTech Payment Gateway — Transaction Processing Requirements", [
        "1. The system shall process payment authorization requests within 500ms end-to-end for 99th percentile latency under 2000 TPS sustained load.",
        "2. When a merchant submits a payment request, the system shall validate the merchant API key, verify the card BIN against the issuer registry, and route the transaction to the appropriate acquirer.",
        "3. A payment transitions from 'Authorized' to 'Captured' when the merchant issues a capture call; from 'Authorized' to 'Voided' if the merchant cancels before capture; and from 'Captured' to 'Refunded' upon a valid refund request.",
        "4. Only users with the 'Payment Operations' role shall be permitted to manually override a declined transaction and force-approve it with a documented reason code.",
        "5. Each payment record must contain: payment_id (UUID), merchant_id (UUID), amount (decimal, 2 decimal places), currency (ISO 4217), card_token (string), authorization_code (string), processor_response_code (string), timestamp (ISO 8601), and status (enum: Authorized|Captured|Voided|Refunded|Declined|Error).",
        "6. The system shall integrate with Visa, Mastercard, and Amex processing networks; if the primary processor is unavailable, transactions shall be routed to the configured backup processor within 2 seconds.",
        "7. The system should be reliable and never lose transaction data.",
        "8. The fraud scoring engine shall evaluate each transaction against velocity checks (>5 transactions in 60 seconds from the same card), geographic anomaly detection, and device fingerprint analysis, returning a risk score between 0.0 and 1.0.",
        "9. Only a 'Compliance Manager' may access raw cardholder data; all other roles shall see masked card numbers (first 6 and last 4 digits only).",
        "10. The system shall support idempotency keys on all payment endpoints; duplicate requests with the same idempotency key within 24 hours must return the original response without creating a new transaction.",
        "11. Settlement files shall be generated daily in ISO 8583 format and transmitted to the acquiring bank via SFTP by 23:00 UTC.",
        "12. If a chargeback is received, the system shall automatically transition the payment to 'Disputed', notify the merchant via webhook, and create a case file with a 30-day response deadline.",
        "13. The system shall maintain 99.999% uptime for the payment authorization endpoint, measured on a rolling 30-day window.",
        "14. All API communication must use TLS 1.3; connections attempting TLS 1.1 or lower shall be rejected.",
        "15. The reconciliation engine shall cross-reference processor settlement reports against internal transaction records daily and flag discrepancies exceeding $0.01.",
        "16. The system should handle international payments smoothly.",
        "17. Webhook delivery to merchant endpoints shall retry with exponential backoff (1s, 2s, 4s, 8s, 16s) for up to 5 attempts; after exhaustion, the event shall be marked as 'delivery_failed' and surfaced in the merchant dashboard.",
        "18. Rate limiting shall be enforced per merchant API key: 100 requests/second for standard tier, 500 requests/second for enterprise tier; excess requests shall receive HTTP 429 with a Retry-After header.",
        "19. All PAN data must be tokenized at the edge before reaching the core processing layer; the tokenization service must comply with PCI-DSS Level 1 requirements.",
        "20. The system shall generate monthly merchant statements in PDF format containing transaction summary, fee breakdown, chargebacks, and net settlement amounts.",
        "21. Multi-currency transactions must use exchange rates sourced from the European Central Bank feed, refreshed every 15 minutes, with a configurable markup percentage per merchant.",
        "22. The system shall support 3D Secure 2.0 authentication flows for all card-present and card-not-present transactions in compliance with PSD2 SCA requirements.",
    ]),

    # ── 3. Smart Agriculture / AgriTech ──────────────────────────────────────
    ("agritech-01", "Smart Agriculture Platform — Crop Monitoring & IoT Requirements", [
        "1. The system shall ingest telemetry data from soil moisture sensors, weather stations, and drone imagery at intervals of 5 minutes, 15 minutes, and daily, respectively.",
        "2. When soil moisture drops below the configured threshold for a specific crop zone, the system shall automatically trigger the irrigation controller and send an alert to the farm manager's mobile app within 30 seconds.",
        "3. A crop cycle transitions from 'Planted' to 'Growing' once germination is sensor-confirmed; from 'Growing' to 'Harvest Ready' when the NDVI index exceeds 0.75 for 5 consecutive days; and from 'Harvest Ready' to 'Harvested' upon manual confirmation.",
        "4. Only users with the 'Agronomist' role shall be permitted to modify crop treatment plans, including pesticide schedules and fertilizer application rates.",
        "5. Each sensor reading must contain: reading_id (UUID), sensor_id (string), sensor_type (enum: SoilMoisture|Temperature|Humidity|WindSpeed|Rainfall|LightIntensity), value (decimal), unit (string), timestamp (ISO 8601), and gps_coordinates (latitude, longitude as decimal degrees).",
        "6. The system shall integrate with the USDA Crop Forecast API for regional yield predictions; if the API is unavailable, the system shall use the last cached forecast data up to 7 days old.",
        "7. The system should help farmers increase crop yields.",
        "8. Drone flight plans must be uploaded as GeoJSON polygons; the system shall validate that the flight area does not exceed the farm boundary and reject plans that overlap with no-fly zones.",
        "9. The pest detection module shall analyze drone imagery using a convolutional neural network and flag affected zones with bounding boxes and confidence scores above 0.80.",
        "10. Only a 'Farm Owner' may approve purchase orders for seeds, fertilizers, and equipment exceeding $5,000; 'Farm Workers' may submit requests but not approve them.",
        "11. The dashboard shall display real-time sensor data with a maximum lag of 60 seconds from sensor reading to dashboard update.",
        "12. Weather forecast data shall be pulled from OpenWeatherMap API every 3 hours and cached locally for offline access during connectivity outages.",
        "13. The system shall generate monthly yield reports comparing actual vs predicted harvest quantities per crop zone, exported as CSV and PDF.",
        "14. All sensor communication must use MQTT over TLS; unencrypted MQTT connections shall be rejected by the broker.",
        "15. If a sensor fails to report for 3 consecutive intervals, the system shall mark it as 'Offline', notify the maintenance team, and interpolate missing data from adjacent sensors.",
        "16. The system should be easy for farmers to use even if they are not tech-savvy.",
        "17. Irrigation schedules must account for forecasted rainfall: if rainfall exceeding 10mm is predicted within 24 hours, scheduled irrigation shall be deferred automatically.",
        "18. Soil health indices (pH, nitrogen, phosphorus, potassium) shall be calculated weekly from lab-uploaded test results and displayed as trend charts with historical comparison.",
        "19. The system shall maintain a geo-fenced asset registry tracking all equipment (tractors, drones, sensors) with real-time GPS location updated every 60 seconds.",
        "20. The mobile app shall function in offline mode for up to 72 hours, syncing queued actions and cached data upon reconnection.",
        "21. Harvest logistics shall integrate with third-party transport scheduling APIs to auto-book pickup trucks based on estimated harvest volume and nearest available fleet.",
    ]),

    # ── 4. Autonomous Vehicle System ─────────────────────────────────────────
    ("automotive-01", "Autonomous Vehicle Platform — Perception & Navigation Requirements", [
        "1. The perception module shall fuse data from LiDAR, radar, and 8 surround-view cameras at a minimum of 20 Hz to produce a unified 3D environment model.",
        "2. When an obstacle is detected within 3 meters of the planned trajectory and closing at > 2 m/s, the system shall initiate emergency braking within 100ms of detection.",
        "3. The vehicle's driving mode transitions from 'Manual' to 'Autonomous' when all sensor health checks pass, the HD map is loaded, and the driver confirms handoff; from 'Autonomous' to 'Manual' upon driver override; and from 'Autonomous' to 'Minimal Risk Condition' if a critical sensor fails.",
        "4. Only users with the 'Fleet Safety Engineer' role shall be permitted to modify the driving policy parameters, including speed limits, following distances, and lane-change aggressiveness thresholds.",
        "5. Each driving event record must contain: event_id (UUID), vehicle_id (string), event_type (enum: LaneChange|EmergencyBrake|Overtake|PedestrianYield|TrafficViolation|Disengage), timestamp (ISO 8601), gps_location (lat/lng), speed_kph (decimal), and sensor_snapshot_url (string).",
        "6. The system shall integrate with HERE HD Live Map for real-time road topology updates; if HERE is unavailable, the system shall fall back to the onboard cached map, which must be no older than 72 hours.",
        "7. The car should drive safely in all conditions.",
        "8. The object classification model shall achieve a minimum of 99.5% precision and 99.0% recall on the KITTI benchmark dataset for pedestrians, cyclists, and vehicles.",
        "9. Only a 'Remote Operations Center Supervisor' may authorize the vehicle to proceed through a construction zone that the planner has flagged as uncertain.",
        "10. The path planner shall generate a collision-free trajectory within 50ms of receiving an updated environment model, considering vehicle kinematics constraints (max steering angle, max lateral acceleration).",
        "11. Vehicle-to-cloud telemetry (V2C) shall stream at 1 Hz during normal operation and 10 Hz during safety-critical events, using MQTT over TLS 1.3.",
        "12. The system shall log all disengagement events with a 30-second pre/post video recording, sensor data, and planner state, stored for a minimum of 3 years per regulatory requirements.",
        "13. Over-the-air (OTA) software updates must be cryptographically signed with Ed25519 keys; the vehicle shall reject any unsigned or incorrectly signed update package.",
        "14. If the localization confidence drops below 95% for more than 5 seconds, the system shall reduce speed to 20 kph and initiate a safe pullover maneuver.",
        "15. The system should handle lots of traffic without issues.",
        "16. The simulation test suite shall cover 10,000+ scenario variations including rain, fog, night, and construction zones, achieving 100% pass rate before any OTA release.",
        "17. Battery-electric vehicle variants shall calculate remaining range using real-time energy consumption, terrain gradient, HVAC load, and historical driving patterns, with an accuracy of +/- 5%.",
        "18. Traffic sign recognition shall correctly identify and parse regulatory signs (speed limits, stop, yield, no entry) with 99.8% accuracy under varying lighting and occlusion conditions.",
        "19. The fleet management dashboard shall display real-time vehicle status, route progress, and safety metrics for up to 500 vehicles simultaneously with a refresh rate of 5 seconds.",
        "20. All inter-module communication within the vehicle software stack shall use DDS (Data Distribution Service) with QoS profiles guaranteeing message delivery within 10ms for safety-critical topics.",
        "21. Passenger ride comfort shall be maintained with lateral acceleration below 2.5 m/s2 and longitudinal acceleration below 3.0 m/s2 during normal autonomous driving.",
        "22. The system shall comply with ISO 26262 ASIL-D requirements for all safety-critical software components, including redundant computation paths and fail-operational architecture.",
    ]),

    # ── 5. Energy Grid Management ────────────────────────────────────────────
    ("energy-01", "Energy Grid Management — Smart Grid & Renewable Integration Requirements", [
        "1. The system shall ingest real-time power flow data from 10,000+ smart meters at 15-second intervals via the IEC 61850 protocol.",
        "2. When grid frequency deviates beyond +/- 0.5 Hz from the nominal 50 Hz, the system shall activate automatic load shedding within 200ms, prioritizing non-critical zones.",
        "3. A power outage transitions from 'Detected' to 'Dispatched' when a repair crew is assigned; from 'Dispatched' to 'Under Repair' upon crew arrival confirmation; and from 'Under Repair' to 'Resolved' once power is restored and verified by smart meter readings.",
        "4. Only users with the 'Grid Controller' role shall be permitted to manually override automatic load balancing decisions or modify generation dispatch schedules.",
        "5. Each meter reading must contain: reading_id (UUID), meter_id (string), consumption_kwh (decimal, 3 decimal places), voltage_v (decimal), current_a (decimal), power_factor (decimal), timestamp (ISO 8601), and quality_flag (enum: Valid|Estimated|Missing).",
        "6. The system shall integrate with the national weather service API for solar irradiance and wind speed forecasts to predict renewable generation capacity 24 hours ahead with error margins below 10%.",
        "7. The system should support clean energy and reduce carbon emissions.",
        "8. The demand response module shall send curtailment signals to enrolled industrial consumers via OpenADR 2.0b protocol, achieving 90% signal delivery within 60 seconds.",
        "9. Only an 'Energy Market Analyst' may submit bids to the wholesale energy exchange; the system shall validate that bid quantities do not exceed available generation capacity plus contracted reserves.",
        "10. The SCADA dashboard shall display real-time grid topology, power flows, and alarm status with a maximum data latency of 3 seconds from field device to screen.",
        "11. If a transformer load exceeds 85% of rated capacity for more than 10 consecutive minutes, the system shall trigger an overload warning and recommend load redistribution to the grid controller.",
        "12. All communication between substations and the control center must use IEC 62351 security standards, including mutual TLS authentication and message integrity verification.",
        "13. The billing engine shall calculate time-of-use tariffs with peak, off-peak, and super-off-peak rates, generating monthly invoices in PDF format with itemized consumption breakdown.",
        "14. The renewable integration module shall curtail solar/wind generation only as a last resort; priority shall be given to battery storage absorption and demand response before curtailment.",
        "15. The system should handle power demand efficiently.",
        "16. Fault location identification shall use impedance-based algorithms on distribution feeders, pinpointing fault location within 100 meters accuracy in 95% of cases.",
        "17. The energy storage management module shall optimize battery charge/discharge cycles to maximize arbitrage revenue while maintaining state-of-charge between 20% and 80% to preserve battery health.",
        "18. The system shall archive all SCADA event logs for a minimum of 10 years in compliance with NERC CIP standards, with indexed search capability across the full archive.",
        "19. Distributed energy resource (DER) registration shall validate inverter IEEE 1547 compliance certificates before allowing grid interconnection.",
        "20. The system shall generate daily generation mix reports showing the percentage contribution of coal, natural gas, nuclear, solar, wind, and hydro sources.",
        "21. Microgrid islanding detection shall identify unintentional islanding within 2 seconds using rate-of-change-of-frequency (ROCOF) and vector shift methods.",
        "22. Customer net metering accounts shall track bidirectional energy flow and calculate monthly credits at the approved feed-in tariff rate, rolling over unused credits for up to 12 months.",
    ]),

    # ── 6. Museum & Gallery Management ───────────────────────────────────────
    ("museum-01", "Museum & Gallery Management — Collection & Visitor Experience Requirements", [
        "1. The system shall catalog all collection items with fields: accession_number (string, unique), title (string), artist (string), medium (string), dimensions_cm (JSON object with height, width, depth), acquisition_date (ISO 8601), provenance (text), insurance_value_usd (decimal), and current_location (string).",
        "2. When a visitor purchases a ticket online, the system shall generate a unique QR code, send it via email within 10 seconds, and update the daily visitor capacity counter in real time.",
        "3. A loan request transitions from 'Submitted' to 'Under Review' when assigned to a curator; from 'Under Review' to 'Approved' or 'Rejected' after curatorial and conservation assessment; and from 'Approved' to 'On Loan' when the item physically leaves the premises.",
        "4. Only users with the 'Chief Curator' role shall be permitted to approve outgoing loans to other institutions or modify the permanent gallery layout.",
        "5. The audio guide system shall deliver location-aware content to visitor devices using BLE beacons, triggering the correct narration within 3 seconds of the visitor entering a gallery zone.",
        "6. The system shall integrate with the Getty ULAN and AAT vocabularies for standardized artist names and art classification terms; if the Getty API is unavailable, local cached vocabularies shall be used.",
        "7. The museum experience should be interesting and educational for all visitors.",
        "8. Environmental monitoring sensors shall track temperature (target: 21 +/- 1 C), relative humidity (target: 45 +/- 5%), and UV exposure in each gallery; if readings deviate beyond thresholds for 15 minutes, the system shall alert the conservation team.",
        "9. Only a 'Registrar' may update an item's accession record, insurance valuation, or condition report; 'Gallery Attendants' may view item details but not modify them.",
        "10. The online collection search shall support full-text search across title, artist, medium, and provenance fields with faceted filtering by period, medium, and gallery location, returning results within 2 seconds.",
        "11. The ticketing system shall enforce daily visitor capacity limits per gallery wing and time slot, automatically closing sold-out slots and offering the next available option.",
        "12. Condition reports must be created before and after each loan period, including photographic documentation; the system shall flag any new damage detected by comparing pre- and post-loan images.",
        "13. The system should work well on mobile phones.",
        "14. The digital exhibition builder shall allow curators to create virtual exhibitions with drag-and-drop layout, high-resolution zoomable images, and multimedia content, publishable to the public website.",
        "15. All visitor personal data must be processed in compliance with GDPR; consent must be explicitly obtained before marketing emails, and data deletion requests must be fulfilled within 72 hours.",
        "16. The gift shop POS integration shall sync inventory with the online store in real time, preventing overselling of limited-edition merchandise.",
        "17. The membership management module shall support tiered memberships (Individual, Family, Patron, Benefactor) with automated renewal reminders sent 30 and 7 days before expiration.",
        "18. The system shall generate monthly visitor analytics reports including total visitors, average dwell time per gallery, popular exhibits, and demographic breakdown (when voluntarily provided).",
        "19. Artwork transport tracking shall integrate with FedEx and DHL APIs to provide real-time shipment status for incoming and outgoing loans, alerting the registrar upon delivery exceptions.",
        "20. The conservation lab module shall schedule and track treatment workflows with task dependencies, material usage, and before/after photography, maintaining a complete treatment history per item.",
    ]),

    # ── 7. Fitness & Wellness App ────────────────────────────────────────────
    ("fitness-01", "Fitness & Wellness Application — Workout & Health Tracking Requirements", [
        "1. The system shall allow users to create a profile with fields: user_id (UUID), display_name (string), date_of_birth (ISO 8601 date), height_cm (integer), weight_kg (decimal), fitness_goal (enum: LoseWeight|BuildMuscle|Endurance|Flexibility|GeneralFitness), and activity_level (enum: Sedentary|LightlyActive|Active|VeryActive).",
        "2. When a user completes a workout session, the system shall calculate calories burned using the MET (Metabolic Equivalent of Task) formula adjusted for the user's weight, and update the daily activity summary within 5 seconds.",
        "3. A training plan transitions from 'Draft' to 'Active' when the user starts the first scheduled workout; from 'Active' to 'Completed' when all scheduled workouts are finished; and from 'Active' to 'Paused' if the user misses 3 consecutive scheduled workouts.",
        "4. Only users with the 'Certified Trainer' role shall be permitted to create and publish workout templates visible to all users; regular users may create private custom workouts only.",
        "5. Each workout record must contain: workout_id (UUID), user_id (UUID), workout_type (enum: Strength|Cardio|HIIT|Yoga|Swimming|Cycling|Running|Custom), exercises (array of {name, sets, reps, weight_kg, duration_seconds}), heart_rate_avg_bpm (integer), calories_burned (decimal), start_time (ISO 8601), and duration_minutes (decimal).",
        "6. The system shall integrate with Apple HealthKit and Google Fit APIs for bidirectional sync of step count, heart rate, and sleep data; if sync fails, the system shall queue the sync and retry every 15 minutes for up to 24 hours.",
        "7. The app should help users get fit and stay motivated.",
        "8. The nutrition tracking module shall allow users to log meals by scanning barcodes or searching the USDA FoodData Central database, calculating macronutrient totals (protein, carbs, fat) and caloric intake per meal and per day.",
        "9. Only an 'Admin' may feature workout plans on the Explore page or ban users for inappropriate content; 'Moderators' may review and hide flagged content but not ban users.",
        "10. The social feed shall display workout completions, personal records, and milestone achievements from followed users, loading the first 20 items within 1.5 seconds.",
        "11. Push notifications for workout reminders must be delivered at the user's preferred time in their local timezone, with a delivery accuracy of +/- 1 minute.",
        "12. If a user's resting heart rate (from wearable sync) exceeds their 30-day rolling average by more than 15%, the system shall suggest a recovery day and reduce planned workout intensity.",
        "13. The system should have a nice and clean design.",
        "14. Progress charts shall display weight, body measurements, strength progression, and cardio performance over time periods of 1 week, 1 month, 3 months, 6 months, and 1 year, with exportable PNG and CSV options.",
        "15. The workout timer shall function offline with locally cached workout plans; completed offline workouts shall sync to the server upon reconnection.",
        "16. Streak tracking shall count consecutive days with at least one logged activity; streaks of 7, 30, 60, 90, and 365 days shall unlock achievement badges.",
        "17. The AI workout recommendation engine shall suggest exercises based on the user's fitness goal, available equipment, workout history, and muscle group recovery status (minimum 48 hours between training the same major muscle group).",
        "18. All health data must be encrypted at rest using AES-256 and in transit using TLS 1.3; the system must comply with HIPAA guidelines for health information handling.",
        "19. The community challenge feature shall support time-bound competitions (e.g., most steps in a week, heaviest deadlift) with leaderboards updated in real time and prize distribution tracking.",
        "20. The system shall generate weekly summary emails containing workout count, total calories burned, step count, sleep quality score, and comparison to the previous week.",
        "21. Video exercise demonstrations shall be streamed using adaptive bitrate (HLS) with quality levels from 360p to 1080p based on the user's connection speed.",
    ]),

    # ── 8. Pet Care & Veterinary ─────────────────────────────────────────────
    ("petcare-01", "Pet Care & Veterinary Management — Animal Health & Booking Requirements", [
        "1. The system shall maintain a pet profile with fields: pet_id (UUID), owner_id (UUID), name (string), species (enum: Dog|Cat|Bird|Rabbit|Reptile|Fish|Other), breed (string), date_of_birth (ISO 8601 date), weight_kg (decimal), microchip_id (string, nullable), and vaccination_status (JSON array).",
        "2. When a pet owner books a veterinary appointment online, the system shall check vet availability, confirm the slot within 5 seconds, and send a confirmation SMS and email with appointment details.",
        "3. A vaccination record transitions from 'Due' to 'Administered' when the vet records the injection; from 'Administered' to 'Expired' when the validity period passes; and from 'Expired' to 'Overdue' if not renewed within 30 days of expiration.",
        "4. Only users with the 'Licensed Veterinarian' role shall be permitted to prescribe medications, update diagnosis records, or authorize surgical procedures.",
        "5. Each medical visit record must contain: visit_id (UUID), pet_id (UUID), vet_id (UUID), visit_date (ISO 8601), chief_complaint (text), examination_notes (text), diagnosis_codes (array of ICD-10-Vet codes), prescribed_treatments (array), follow_up_date (ISO 8601, nullable), and invoice_id (UUID).",
        "6. The system shall integrate with PetDesk and Vetspire APIs for appointment synchronization; if the third-party API is unavailable, appointments shall be queued locally and synced upon reconnection within 30 minutes.",
        "7. The system should make pet care convenient for pet owners.",
        "8. The medication reminder module shall send push notifications to pet owners at the prescribed administration times, with snooze and confirmation options; unconfirmed doses shall trigger a follow-up alert after 30 minutes.",
        "9. Only a 'Clinic Manager' may modify pricing for services, adjust staff schedules, or access financial reports; 'Receptionists' may book appointments and process payments but not modify pricing.",
        "10. The prescription system shall validate drug interactions against a veterinary pharmacology database before allowing a vet to finalize a prescription; flagged interactions must be acknowledged by the vet with a documented override reason.",
        "11. Pet owners shall be able to view their pet's complete medical history, including visit notes, lab results, X-ray images, and vaccination records, through a secure owner portal.",
        "12. The appointment scheduling system shall prevent double-booking of veterinarians and examination rooms; if a conflict is detected, the system shall suggest the nearest available alternative slot.",
        "13. The system should handle emergencies properly.",
        "14. Lab result integration shall automatically import blood work, urinalysis, and pathology results from connected laboratory equipment (IDEXX, Abaxis) and attach them to the corresponding visit record.",
        "15. The boarding and grooming module shall track kennel assignments, feeding schedules, medication administration, exercise logs, and behavior notes for each boarded pet, with real-time updates visible to owners.",
        "16. The invoicing system shall generate itemized bills with service codes, medication costs, tax calculations, and payment method tracking; partial payments and payment plans must be supported.",
        "17. All medical records must be retained for a minimum of 7 years per veterinary regulatory requirements; archived records must be retrievable within 24 hours upon request.",
        "18. The pet adoption module shall list available animals with photos, medical history summary, temperament assessment, and adoption requirements; adoption applications shall be workflow-managed with background check integration.",
        "19. The telemedicine module shall support HIPAA-compliant video consultations with screen sharing, photo upload for visual examination, and integrated note-taking, with session recordings stored for 90 days.",
        "20. The system shall generate monthly clinic performance reports including appointment volume, revenue by service category, client retention rate, and average wait time.",
        "21. Emergency triage shall classify incoming cases using a 5-level urgency scale; Level 1 (life-threatening) cases shall bypass the regular queue and trigger immediate vet notification via SMS and intercom.",
    ]),

    # ── 9. Travel Agency Platform ────────────────────────────────────────────
    ("travel-01", "Travel Agency Platform — Booking & Itinerary Management Requirements", [
        "1. The system shall allow customers to search for flights, hotels, and car rentals simultaneously, displaying combined package pricing within 3 seconds for 95% of search queries.",
        "2. When a customer confirms a booking, the system shall reserve inventory with the supplier, process payment, generate a booking confirmation PDF, and send it via email within 30 seconds.",
        "3. A booking transitions from 'Confirmed' to 'Ticketed' once supplier e-tickets are issued; from 'Ticketed' to 'Checked In' when the traveler completes online check-in; and from 'Confirmed' to 'Cancelled' upon customer cancellation, triggering refund processing.",
        "4. Only users with the 'Travel Consultant' role shall be permitted to override system-generated pricing, apply custom discounts exceeding 15%, or issue manual refunds.",
        "5. Each booking record must contain: booking_id (UUID), customer_id (UUID), segments (array of {type: Flight|Hotel|Car|Activity, supplier_id, confirmation_number, dates, pricing}), total_amount (decimal), currency (ISO 4217), payment_status (enum: Pending|Paid|PartialRefund|FullRefund), and created_at (ISO 8601).",
        "6. The system shall integrate with Amadeus GDS for flight inventory, Booking.com API for hotel availability, and Hertz/Avis APIs for car rentals; if a supplier API is unavailable, the system shall display cached results with a 'prices may vary' disclaimer.",
        "7. The system should make travel planning easy and stress-free.",
        "8. The dynamic packaging engine shall bundle flight + hotel combinations, applying negotiated contracted rates and marking up by the configured margin per destination, ensuring the package price is always lower than the sum of standalone bookings.",
        "9. Only a 'Finance Manager' may process refunds exceeding $5,000 or adjust commission rates; 'Travel Consultants' may initiate refund requests but not approve amounts above this threshold.",
        "10. The itinerary builder shall produce a day-by-day travel plan including flight details, hotel check-in/out, activity schedules, and local weather forecasts, rendered as a shareable web page and downloadable PDF.",
        "11. Visa requirement checks shall be performed based on the traveler's nationality and destination country using the Sherpa API, displaying required documents and processing times during the booking flow.",
        "12. If a flight segment is cancelled by the airline, the system shall automatically search for alternative flights within 6 hours of the original departure, present options to the customer, and rebook upon selection.",
        "13. The system should handle group bookings efficiently.",
        "14. The loyalty points module shall accrue points per dollar spent (1 point per $1 for standard, 2 points for premium members), with points redeemable for future bookings at a rate of 100 points = $1.",
        "15. Travel insurance shall be offered during checkout with options for trip cancellation, medical emergency, and baggage loss coverage; policy documents must be generated and delivered instantly upon purchase.",
        "16. The corporate travel module shall enforce company travel policies (preferred airlines, maximum hotel rate per city, advance booking requirements) and flag non-compliant bookings for manager approval.",
        "17. Currency conversion shall use real-time exchange rates from the Open Exchange Rates API, refreshed every 30 minutes, with the conversion rate locked at the time of booking confirmation.",
        "18. The review and rating system shall allow verified travelers to rate flights, hotels, and activities on a 1-5 scale with written reviews; reviews must be moderated within 48 hours before public display.",
        "19. All customer passport and identity document scans must be encrypted at rest using AES-256 and automatically purged 90 days after trip completion unless the customer opts for storage.",
        "20. The system shall generate monthly sales reports per consultant, destination, and supplier, including booking volume, revenue, commission earned, and cancellation rate.",
        "21. The mobile app shall support offline access to confirmed itineraries, boarding passes, and hotel vouchers, with automatic sync when connectivity is restored.",
        "22. Group booking management shall support rooming list uploads (CSV), individual payment splitting, group leader dashboards, and automated name-change handling up to 72 hours before departure.",
    ]),

    # ── 10. Warehouse Automation ─────────────────────────────────────────────
    ("warehouse-01", "Warehouse Automation — Inventory & Robotics Management Requirements", [
        "1. The system shall maintain real-time inventory positions for each storage location (aisle-rack-shelf-bin) with accuracy of 99.9% validated by cycle counts.",
        "2. When a pick order is received from the WMS, the system shall generate an optimized pick path for the warehouse robot, minimizing total travel distance using the Travelling Salesman heuristic, and dispatch the robot within 5 seconds.",
        "3. An inbound shipment transitions from 'Announced' to 'Received' upon dock scan; from 'Received' to 'Quality Checked' after inspection; from 'Quality Checked' to 'Put Away' once items are placed in assigned storage locations; and to 'Rejected' if quality check fails.",
        "4. Only users with the 'Warehouse Supervisor' role shall be permitted to override automated storage location assignments, authorize write-offs for damaged goods, or modify robot zone configurations.",
        "5. Each inventory transaction must contain: transaction_id (UUID), sku (string), location_id (string), quantity (integer), transaction_type (enum: Receive|PutAway|Pick|Pack|Ship|Adjust|Transfer|CycleCount), timestamp (ISO 8601), operator_id (UUID), and reference_order_id (UUID, nullable).",
        "6. The system shall integrate with SAP EWM for enterprise inventory synchronization and with carrier APIs (FedEx, UPS, DHL) for shipping label generation and tracking; if SAP is unavailable, transactions shall be queued and batch-synced upon reconnection.",
        "7. The warehouse should run smoothly and efficiently.",
        "8. The robot fleet manager shall monitor battery levels for all AGVs (Automated Guided Vehicles); when a robot's battery drops below 20%, it shall be automatically routed to the nearest charging station, and its pending tasks reassigned to available robots.",
        "9. Only a 'Dock Manager' may authorize the release of outbound shipments; 'Warehouse Workers' may complete packing tasks but not mark shipments as released.",
        "10. The wave planning engine shall batch orders by shipping carrier, delivery zone, and priority level, generating optimized pick waves that maximize picker utilization above 85%.",
        "11. Barcode and RFID scanning shall validate item identity at each process step (receive, put-away, pick, pack, ship) with a scan-to-confirmation latency under 200ms.",
        "12. If a pick location is empty but the WMS shows positive inventory, the system shall create an automatic cycle count task, flag the discrepancy, and redirect the pick to an alternative location holding the same SKU.",
        "13. The system should handle peak holiday season volumes without slowdowns.",
        "14. The slotting optimization engine shall recommend storage location reassignments monthly based on pick frequency, item velocity (ABC classification), and ergonomic considerations (heavy items at waist height).",
        "15. Conveyor system integration shall track tote positions in real time using barcode scan points at each divert gate, with sort accuracy exceeding 99.95%.",
        "16. The labor management module shall track individual picker productivity (units per hour, accuracy rate), generate daily performance scorecards, and flag performance below 80% of the standard rate.",
        "17. All robot movement commands must be validated by the collision avoidance system before execution; if a potential collision is detected, the robot shall halt and request a new path within 500ms.",
        "18. The receiving module shall support ASN (Advanced Shipping Notice) matching, validating received quantities against expected shipment data and flagging discrepancies exceeding 2% by quantity or value.",
        "19. Temperature-controlled zone monitoring shall track and log temperature every 60 seconds for cold chain storage areas; readings outside the configured range (2-8 C for pharma, -18 C for frozen) shall trigger immediate alerts.",
        "20. The system shall generate daily warehouse KPI dashboards showing: orders fulfilled, units shipped, dock-to-stock time, order accuracy rate, robot utilization, and labor efficiency.",
        "21. Returns processing shall include inspection workflows, disposition decisions (restock, refurbish, scrap), and automatic inventory adjustment upon disposition completion.",
        "22. The system shall support multi-warehouse inventory visibility with cross-dock transfer recommendations when a warehouse has excess stock and another has a shortage for the same SKU.",
        "23. Emergency shutdown protocols shall allow a supervisor to halt all robot movement within 2 seconds via the dashboard kill switch or physical e-stop buttons mounted at each zone entry.",
    ]),
]


# ─────────────────────────────────────────────────────────────────────────────
# FILE WRITER & INGESTION (same logic as batch 1)
# ─────────────────────────────────────────────────────────────────────────────
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_requirements"


def write_files():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for slug, title, reqs in DOCUMENTS:
        fp = DATA_DIR / f"{slug}.txt"
        with open(fp, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n")
            f.write("Functional Requirements\n\n")
            for r in reqs:
                f.write(r + "\n")
        print(f"  Written: {fp.name}  ({len(reqs)} requirements)")
        written += 1
    return written


def ingest_all():
    from specforge.ingestion.service import ingest_document
    from specforge.preprocessing.service import preprocess_requirement
    from specforge.classification.service import classify_and_store
    from specforge.ambiguity.service import detect_and_store
    from specforge.db.session import get_session
    from specforge.db.models import Requirement
    from sqlalchemy import select

    total_units = 0
    docs_done = 0

    for slug, title, reqs in DOCUMENTS:
        # Skip if already ingested
        with get_session() as s:
            existing = s.execute(
                select(Requirement).where(Requirement.source_doc_id == slug)
            ).scalars().first()
            if existing:
                print(f"  [{slug}] already in DB -- skipping.")
                continue

        print(f"\nIngesting [{slug}] ...")
        fp = DATA_DIR / f"{slug}.txt"

        # 1. Ingest raw document
        req = ingest_document(file_path=str(fp), source_doc_id=slug)
        print(f"  [1/3] Raw document ingested (id={req.requirement_id})")

        # 2. Segment into atomic units
        units = preprocess_requirement(req.requirement_id)
        print(f"  [2/3] Segmented into {len(units)} atomic units.")

        # 3. Classify + ambiguity score each unit
        ok = 0
        for u in units:
            try:
                classify_and_store(u.requirement_id)
                detect_and_store(u.requirement_id)
                ok += 1
            except Exception as exc:
                print(f"    WARN: unit {u.requirement_id}: {exc}")
        print(f"  [3/3] Classified and scored {ok}/{len(units)} units. [OK]")
        total_units += len(units)
        docs_done += 1

    return docs_done, total_units


if __name__ == "__main__":
    print("=" * 60)
    print("SpecForge AI -- Synthetic Data Generator (Batch 2)")
    print("=" * 60)

    print("\n[Step 1] Writing .txt requirement files...")
    n = write_files()
    print(f"\n[OK] {n} files written to {DATA_DIR}\n")

    print("[Step 2] Ingesting into database...")
    docs, units = ingest_all()
    print(f"\n{'=' * 60}")
    print(f"Ingestion complete.")
    print(f"  Documents processed : {docs}")
    print(f"  Atomic units stored : {units}")
    print(f"{'=' * 60}")
    print("\n[Done] Batch 2 synthetic data generation complete.")
