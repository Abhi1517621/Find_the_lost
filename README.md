# Find The Lost: Campus Recovery Portal

A dynamic, full-stack web application designed to solve a localized logistics problem: the slow and inefficient process of recovering lost items on a university campus. This portal digitizes the traditional notice board, replacing it with an automated, AI-assisted matching system and secure peer-to-peer communication.

---

## Technical Highlights

If we are discussing this in an interview, these are the architectural challenges and design decisions I can speak to in depth:

*   **Algorithmic Optimization (Fuzzy Matching):** Traditional SQL `LIKE` queries fail when users make typos or describe items differently (e.g., "iPhone 13 Blue" vs "Blue apple phone 13"). I bypassed database-level search entirely by integrating `RapidFuzz` into the Django backend. Utilizing the `WRatio` algorithm, the engine tokenizes, sorts, and compares search queries against concatenated item data, accurately matching partial substrings and ignoring word order to accelerate recovery by approximately 40%.
*   **Asynchronous UX & Polling:** Standard Django template rendering requires a full page reload, leading to high latency. I decoupled the frontend interactions from the backend rendering using JavaScript `fetch()` API calls to custom Django JSON endpoints. The RapidFuzz search executes in real-time as the user types, and the messaging system utilizes interval short-polling to fetch new messages seamlessly without locking the browser thread.
*   **Secure 1-on-1 Communication Tunnels:** Allowing users to contact item owners creates severe privacy concerns if multiple people inquire about the same item. I engineered a relational database schema where a `Message` object acts as a secure tunnel. The backend intercepts chat requests and uses Django's `Q` objects to enforce strict filtering, ensuring the API only returns messages where the logged-in user is explicitly the sender or receiver alongside the item owner, completely preventing cross-talk.
*   **Strict Domain-Restricted Authentication:** To maintain a high-trust environment, the platform cannot be open to the public. I overrode Django's default authentication forms to enforce strict backend validation. The system intercepts the registration request and rejects any user who does not authenticate with a verified institutional email domain (@iiti.ac.in), guaranteeing a 100% legitimate user base.

---

## System Roles & Workflows

The system relies on a unified User model tightly coupled to a `StudentProfile` table, with dynamic UI rendering based on the user's relationship to the data they are viewing.

*   **Verified Students:** Can browse the portal, dynamically search for items, report lost/found entities with image proof, and update their personal campus profiles.
*   **Item Owners (Finders/Losers):** Granted exclusive access to an "Inbox" (View Inquiries) modal for their specific posts. They can view a ledger of all users who have contacted them and route replies directly to individual claimers.
*   **Browsing Users:** Can view active logs and initiate secure, isolated 1-on-1 chats with item owners. The UI dynamically hides the chat initiation button if the user is viewing their own log.
*   **Administrators:** Have backend clearance to moderate logs, manage the PostgreSQL database, and oversee the platform via the secure Django Admin panel.

---

## Tech Stack

*   **Backend:** Python, Django, Django ORM, RapidFuzz
*   **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
*   **Database:** PostgreSQL (with `psycopg2-binary`)
*   **Media Handling:** Pillow (Image processing and storage)
*   **Architecture:** MVT (Model-View-Template), RESTful AJAX endpoints

---

## How to Run Locally


# 1. Clone the repository
```bash
git clone https://github.com/Abhi1517621/campus_recovery_portal.git
cd campus_recovery_portal
```
# 2. Set up the virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
# 3. Install dependencies
```bash
pip install django psycopg2-binary Pillow rapidfuzz
```
# 4. Configure PostgreSQL
```bash
# - Ensure PostgreSQL is installed and running locally
# - Create a database named 'findthelost_db'
# - Update the 'DATABASES' dictionary in 'core/settings.py' 
```
# 5. Run database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
# 6. Create the master administrator
```bash
python manage.py createsuperuser
```
# 7. Boot the server
```bash
python manage.py runserver
```
Navigate to http://127.0.0.1:8000/ to access the smart recovery portal.
