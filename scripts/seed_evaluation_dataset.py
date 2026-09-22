"""
Dataset generator script for evaluation benchmark tasks (15-20 diverse requirements documents).
"""

import json
import os

TASKS = [
    {
        "task_id": "eval_01_todo_api",
        "title": "To-Do List REST API Service",
        "domain": "Web Services / REST API",
        "raw_text": (
            "The system shall provide a REST API for managing to-do items. "
            "Users must be able to create, read, update, and delete tasks. "
            "Tasks should be stored efficiently in a database. "
            "The API must respond quickly under peak workload. "
            "Input arguments shall be validated gracefully without system failure."
        ),
        "ground_truth_checklist": [
            "REST API endpoint for creating a new to-do task",
            "REST API endpoint for retrieving task items",
            "REST API endpoint for updating existing task details",
            "REST API endpoint for deleting a task by ID",
            "Task data model containing title, status, and due date",
            "Database persistence layer for task records",
            "Input validation returning 400 Bad Request on invalid payloads",
            "Error handling returning standard JSON error schema",
            "Task completion status toggling (pending/completed)",
            "Timestamp fields for created_at and updated_at",
            "Pagination support for task listing endpoint",
            "Response latency benchmark under 200ms",
        ],
    },
    {
        "task_id": "eval_02_library_lending",
        "title": "Library Book Lending System",
        "domain": "Enterprise Software / Management",
        "raw_text": (
            "The system shall manage library book checkout and return operations. "
            "Patrons must be registered with a unique member ID. "
            "Overdue books should trigger fine calculations automatically. "
            "The system shall update book availability status seamlessly."
        ),
        "ground_truth_checklist": [
            "Patron registration and unique member ID generation",
            "Book catalog storage with ISBN, title, and author details",
            "Checkout process recording borrower ID and due date",
            "Return process recording return date and updating inventory",
            "Automated overdue fine calculation policy",
            "Book availability status tracking (available/checked_out)",
            "Maximum checkout limit enforcement per patron",
            "Search functionality by title, author, or ISBN",
            "Overdue notification message generation",
            "Database transaction integrity for checkout operations",
            "Admin view for viewing active loan records",
            "Fine payment recording mechanism",
        ],
    },
    {
        "task_id": "eval_03_simple_chat",
        "title": "Real-Time WebSocket Chat Application",
        "domain": "Networking / Real-Time Messaging",
        "raw_text": (
            "The system shall provide real-time chat room messaging using WebSockets. "
            "Messages must be delivered instantly to all connected users. "
            "User connections should be handled robustly without dropping packets. "
            "Chat history shall be logged appropriately."
        ),
        "ground_truth_checklist": [
            "WebSocket endpoint for real-time bi-directional messaging",
            "Chat room joining and leaving event handling",
            "Broadcast mechanism delivering messages to active channel members",
            "User nickname assignment and duplicate handling",
            "Persistent chat message history storage in database",
            "Heartbeat mechanism for detecting disconnected clients",
            "Message payload schema containing sender, text, and timestamp",
            "Input sanitization to prevent XSS injection in chat text",
            "Connection rate limiting per IP address",
            "Graceful handling of server disconnects and reconnects",
            "Unread message indicator tracking",
            "Maximum message length validation",
        ],
    },
    {
        "task_id": "eval_04_inventory_tracker",
        "title": "Warehouse Inventory Tracker",
        "domain": "Logistics / Supply Chain",
        "raw_text": (
            "The system shall track warehouse product stock levels. "
            "Stock counts must update in real time upon receiving or dispatching goods. "
            "Reorder alerts should be sent when inventory falls below a threshold. "
            "Data synchronization must be performed seamlessly."
        ),
        "ground_truth_checklist": [
            "Product SKU registration with name, category, and unit price",
            "Stock quantity adjustment API for receiving shipments",
            "Stock quantity reduction API for dispatching orders",
            "Configurable minimum threshold limit per SKU",
            "Automated low-stock alert event generation",
            "Inventory audit trail logging timestamped stock adjustments",
            "Warehouse bin location assignment tracking",
            "Negative stock quantity prevention logic",
            "Bulk stock import via CSV upload",
            "Inventory valuation report summary generation",
            "User role permissions (warehouse staff vs manager)",
            "Concurrent stock modification lock handling",
        ],
    },
    {
        "task_id": "eval_05_url_shortener",
        "title": "URL Shortener & Analytics Engine",
        "domain": "Web Utilities / Infrastructure",
        "raw_text": (
            "The system shall generate short aliases for long destination URLs. "
            "Redirects must execute fast when a short link is visited. "
            "Click analytics should be recorded for each redirection. "
            "Short code generation shall avoid collisions."
        ),
        "ground_truth_checklist": [
            "API endpoint accepting original URL and returning short code",
            "HTTP 301/302 redirection endpoint mapping short code to long URL",
            "Collision-resistant short code generator algorithm",
            "Original URL format validation and syntax checking",
            "Click count incrementing on each redirection",
            "Click analytics logging timestamp, user agent, and referrer",
            "Optional short link expiration date setting",
            "Custom slug option for user-defined short aliases",
            "Rate limiting on link creation endpoint",
            "High availability lookup latency under 50ms",
            "API endpoint retrieving analytics summary for short link",
            "Database indexing on short code primary key",
        ],
    },
    {
        "task_id": "eval_06_quiz_app",
        "title": "Interactive Quiz & Leaderboard Engine",
        "domain": "Education / Gamification",
        "raw_text": (
            "The system shall present multiple-choice quiz questions to users. "
            "Answers must be scored immediately upon submission. "
            "Leaderboards should display high scores dynamically. "
            "Quiz content shall be managed effectively."
        ),
        "ground_truth_checklist": [
            "Quiz creation endpoint with title, topic, and questions",
            "Question model containing prompt, options, and correct answer key",
            "Quiz session initiation and timer management",
            "User answer submission endpoint with automated scoring",
            "Leaderboard computation ranking users by score and completion time",
            "User quiz history tracking and score archives",
            "Randomized question order per quiz session",
            "Score breakdown showing correct vs incorrect answers",
            "Category filtering for available quizzes",
            "Single-attempt enforcement per quiz session",
            "Validation ensuring questions have at least two options",
            "Exportable quiz performance summary",
        ],
    },
    {
        "task_id": "eval_07_expense_splitter",
        "title": "Group Expense Splitter",
        "domain": "Finance / Personal Utilities",
        "raw_text": (
            "The system shall record shared expenses among group members. "
            "Balances must be calculated accurately to show who owes whom. "
            "Settlements should be logged seamlessly when paid. "
            "Financial precision shall be maintained."
        ),
        "ground_truth_checklist": [
            "Group creation and member registration endpoint",
            "Expense entry creation with description, total amount, and payer ID",
            "Split calculation supporting equal splits among members",
            "Unequal split calculation by exact amount or percentage",
            "Net balance calculation for each group member",
            "Simplified debt settlement algorithm minimizing transfers",
            "Payment recording endpoint marking debts as settled",
            "Currency format handling using fixed decimal precision",
            "Expense activity feed detailing group history",
            "Itemized receipt breakdown per expense",
            "Negative amount validation prevention",
            "Exportable expense balance summary report",
        ],
    },
    {
        "task_id": "eval_08_recipe_organizer",
        "title": "Recipe & Grocery List Manager",
        "domain": "Consumer Apps / Productivity",
        "raw_text": (
            "The system shall store recipes with ingredients and cooking steps. "
            "Users must be able to search recipes by ingredient keyword. "
            "Grocery lists should be generated automatically from selected recipes. "
            "Recipe images shall be uploaded appropriately."
        ),
        "ground_truth_checklist": [
            "Recipe creation endpoint with title, instructions, and preparation time",
            "Ingredient list model specifying name, quantity, and measurement unit",
            "Keyword search filtering recipes by available ingredients",
            "Automated grocery list aggregation from multiple recipes",
            "Ingredient quantity consolidation on grocery list",
            "Serving size scaling adjusting ingredient amounts",
            "Recipe categorization by meal type (breakfast, lunch, dinner)",
            "Dietary constraint tag filtering (vegan, gluten-free)",
            "Favorite recipe bookmarking per user account",
            "Image upload support for recipe cover photos",
            "Step-by-step cooking mode view",
            "Export grocery list as plain text or PDF",
        ],
    },
    {
        "task_id": "eval_09_habit_tracker",
        "title": "Habit Tracker & Streak Analytics",
        "domain": "Health / Self-Improvement",
        "raw_text": (
            "The system shall track daily user habits and completion streaks. "
            "Habit check-ins must record the date and status. "
            "Streak counters should update accurately without resetting erroneously. "
            "Analytics visualizations shall display habit consistency."
        ),
        "ground_truth_checklist": [
            "Habit creation endpoint with title, frequency (daily/weekly), and goal",
            "Daily check-in endpoint recording habit completion for target date",
            "Current streak calculation counting consecutive completion days",
            "Longest streak history tracking per habit",
            "Missed day detection marking habits as incomplete",
            "Completion rate percentage calculation over 30-day window",
            "Habit reminder notification scheduling",
            "Habit archiving and restoration capability",
            "Notes and reflection entry logging per check-in",
            "Calendar view API endpoint showing monthly check-in matrix",
            "Duplicate check-in prevention for same date",
            "Timezone-aware date boundary processing",
        ],
    },
    {
        "task_id": "eval_10_parking_finder",
        "title": "Parking Spot Finder & Booking Service",
        "domain": "Smart City / Mobility",
        "raw_text": (
            "The system shall locate available parking spots near a destination. "
            "Users must be able to reserve a parking spot for a specified time window. "
            "Spot availability should update instantly upon booking. "
            "Reservation fees shall be computed accurately."
        ),
        "ground_truth_checklist": [
            "Parking lot registration with address, total capacity, and rate per hour",
            "Geographic location search finding nearest parking lots",
            "Real-time spot availability query by arrival and departure time",
            "Spot reservation endpoint locking selected space for user",
            "Hourly fee calculation logic based on duration and lot rate",
            "Reservation status workflow (reserved, active, completed, cancelled)",
            "Double booking prevention for overlapping time slots",
            "User booking history and digital parking pass generation",
            "Cancellation policy enforcement and refund window calculation",
            "Lot operator dashboard for viewing occupied spots",
            "Vehicle license plate registration per booking",
            "Grace period handling for late arrivals",
        ],
    },
    {
        "task_id": "eval_11_blog_generator",
        "title": "Static Markdown Site Generator",
        "domain": "Developer Tools / Publishing",
        "raw_text": (
            "The system shall compile Markdown files into a static HTML blog. "
            "Articles must be parsed with frontmatter metadata tags. "
            "Site build speed should be optimal for large content repositories. "
            "HTML output shall follow structured templates."
        ),
        "ground_truth_checklist": [
            "Markdown file scanner reading input content directory",
            "YAML frontmatter parser extracting title, date, tags, and author",
            "Markdown to HTML content rendering engine",
            "HTML layout template engine injecting rendered body into page wrapper",
            "Blog post index page generator with paginated article lists",
            "Tag archive page generator grouping articles by tag",
            "RSS feed XML generation containing recent posts",
            "Static asset copying (CSS, JS, images) to output build folder",
            "Incremental build option recompiling modified files only",
            "Draft article filtering excluding posts marked draft=true",
            "Syntax highlighting for code blocks in post content",
            "Build log output reporting compiled pages and total time",
        ],
    },
    {
        "task_id": "eval_12_weather_dashboard",
        "title": "Weather Forecast Aggregator",
        "domain": "Web Utilities / API Aggregation",
        "raw_text": (
            "The system shall aggregate weather forecasts from multiple external APIs. "
            "Location weather queries must return temperature, humidity, and wind conditions. "
            "Forecast data should be cached efficiently to minimize external API rate limits. "
            "API failure fallbacks shall operate smoothly."
        ),
        "ground_truth_checklist": [
            "City or zip code weather search query endpoint",
            "Integration with external weather data provider API",
            "Data normalization mapping provider responses to unified schema",
            "Response caching layer (in-memory or Redis) with configurable TTL",
            "Fallback provider handling if primary weather API is unreachable",
            "Current weather metrics return (temperature, humidity, wind, pressure)",
            "5-day forecast data endpoint with daily high/low temperatures",
            "Severe weather alert parsing and notification flag",
            "Temperature unit conversion (Celsius to Fahrenheit)",
            "API rate limit tracking and throttle management",
            "Geocoding lookup converting city name to latitude/longitude",
            "Cache hit/miss metric logging",
        ],
    },
    {
        "task_id": "eval_13_health_logger",
        "title": "Patient Vitals & Health Logger",
        "domain": "Healthcare / Telemedicine",
        "raw_text": (
            "The system shall log patient vital signs including blood pressure and heart rate. "
            "Out-of-range vital readings must trigger clinical warning flags immediately. "
            "Patient data privacy should be maintained securely. "
            "Vitals history shall be exported cleanly for physician review."
        ),
        "ground_truth_checklist": [
            "Patient record management with unique patient identifier",
            "Vital sign entry creation (systolic BP, diastolic BP, heart rate, temperature)",
            "Configurable clinical threshold bounds per vital metric",
            "Automated out-of-range vital alert flag generation",
            "Role-based access control protecting patient health data",
            "Audit logging of all vital record reads and writes",
            "Timestamped historical vitals list endpoint per patient",
            "Physician review summary report generation",
            "Data encryption at rest for sensitive health records",
            "Validation enforcing physiological min/max range limits",
            "Patient trend analysis calculating weekly average vitals",
            "PDF/CSV export of patient health log",
        ],
    },
    {
        "task_id": "eval_14_fitness_tracker",
        "title": "Workout & Cardio Session Tracker",
        "domain": "Fitness / Wearable Integration",
        "raw_text": (
            "The system shall log workout sessions including strength training and cardio runs. "
            "Exercise sets must record weight, repetitions, and rest interval. "
            "Caloric expenditure should be calculated accurately based on activity duration. "
            "Fitness goals shall be monitored effectively."
        ),
        "ground_truth_checklist": [
            "Workout session creation with title, category, and start/end time",
            "Exercise detail entry specifying exercise name, weight, and rep count",
            "Cardio session entry specifying distance, duration, and pace",
            "Calorie burn estimation formula based on MET values and body weight",
            "Personal record (1-rep max) tracking per exercise",
            "Weekly workout volume calculation (total weight lifted)",
            "Rest timer tracking between sets",
            "Fitness goal setting (e.g. 4 workouts per week) and progress tracker",
            "Custom exercise definition addition to library",
            "Workout template saving for recurring routines",
            "Body weight and metric tracking endpoint",
            "Activity log feed sorted chronologically",
        ],
    },
    {
        "task_id": "eval_15_ticket_service",
        "title": "Event Ticket Booking Service",
        "domain": "E-Commerce / Ticketing",
        "raw_text": (
            "The system shall manage event ticket sales and venue seat reservations. "
            "Customers must select seats and complete checkout within a time window. "
            "Seat holds should expire automatically if checkout is not finished. "
            "Ticket issuance shall proceed reliably upon payment confirmation."
        ),
        "ground_truth_checklist": [
            "Event listing creation with venue details, date, and seat map",
            "Seat availability query returning real-time seat status",
            "Temporary seat hold mechanism reserving seat during checkout window",
            "Automated hold expiration background task releasing unpaid seats",
            "Order creation and checkout payment processing trigger",
            "Unique QR code or barcode ticket generation upon payment",
            "Double-booking prevention using database row locking",
            "Tiered ticket pricing (e.g. VIP, Standard, Economy)",
            "Customer booking confirmation email trigger payload",
            "Event organizer sales dashboard reporting revenue and tickets sold",
            "Ticket scan verification endpoint for venue entry",
            "Refund and order cancellation processing within policy window",
        ],
    },
]


def seed_dataset(output_dir: str = "./data/evaluation_tasks") -> None:
    """Write all 15 benchmark task JSON documents into output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    for task in TASKS:
        file_path = os.path.join(output_dir, f"{task['task_id']}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(task, f, indent=2)
        print(f"Seeded evaluation task: {file_path}")


if __name__ == "__main__":
    seed_dataset()
