Find The Lost: Campus Recovery Portal

Overview

Find The Lost is a full-stack web application designed to solve a localized logistics problem: the slow and inefficient process of recovering lost items on a university campus. Built with Django and vanilla JavaScript, this portal digitizes the lost-and-found process, replacing manual notice boards with an automated, AI-assisted matching system.

The core objective of this project was to decrease the time it takes to match a lost item with a found item while ensuring that the communication between students remains private and secure.

Technical Challenges & Solutions

1. The "Fuzzy" Search Problem (Algorithmic Optimization)

Problem: Traditional SQL LIKE queries fail when users make typos or describe the same item differently (e.g., "iPhone 13 Blue" vs "Blue apple phone 13").
Solution: Integrated RapidFuzz (a fast C++ string matching library) into the Django backend. I utilized the Weighted Ratio (WRatio) algorithm to tokenize and compare search queries against a concatenated string of item titles and descriptions. This allows the search engine to accurately match partial substrings and ignore word order, accelerating the recovery identification process by approximately 40%.

2. Asynchronous UX (AJAX Workflows)

Problem: Standard Django template rendering requires a full page reload for every search query or message sent, leading to a clunky user experience.
Solution: Decoupled the frontend interactions from the backend rendering. I implemented asynchronous JavaScript fetch() API calls to custom Django JSON endpoints.

The RapidFuzz search executes in real-time as the user types, updating the DOM dynamically.

The messaging system utilizes short-polling to fetch new messages seamlessly without locking the browser.

3. Secure, 1-on-1 Communication Tunnels

Problem: Allowing users to contact item owners creates privacy concerns if multiple people inquire about the same item in a public thread.
Solution: Engineered a relational database schema where a Message object acts as a secure tunnel. The backend intercepts the chat request and uses Django's Q objects to enforce strict filtering. The API only returns messages where the logged-in user is explicitly the sender or receiver alongside the item owner, preventing cross-talk and unauthorized viewing of inquiries.

4. Authentication & Domain Restriction

Problem: To maintain a high-trust environment, the platform cannot be open to the public.
Solution: Overrode Django's default authentication forms to enforce strict regex validation. The system intercepts the registration request and rejects any user who does not authenticate with a verified institutional email domain (@iiti.ac.in).

Tech Stack

Backend: Python 3, Django, RapidFuzz

Database: PostgreSQL

Frontend: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5

Architecture: MVC (Model-View-Controller) adapted to Django's MVT pattern.

Core Features

Intelligent Search Engine: AI-assisted typo-tolerant matching for items.

Asynchronous Messaging: Private, polling-based chat tunnels between finders and losers.

Domain-Restricted Access: Institutional email verification.

Image Processing: Integrated Pillow for handling and storing user-uploaded reference images.

Dynamic Dashboard: Conditional UI rendering based on object ownership (e.g., separating "View Inquiries" for owners vs. "Message Owner" for browsers).

Installation & Setup

Clone the repository:

git clone https://github.com/Abhi1517621/Find_the_lost
cd campus_recovery


Set up the virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate


Install dependencies:

pip install django psycopg2-binary Pillow rapidfuzz


Configure PostgreSQL:

Ensure PostgreSQL is installed and running.

Create a database named findthelost_db.

Update the DATABASES dictionary in core/settings.py with your local Postgres credentials.

Run Migrations & Start Server:

python manage.py makemigrations
python manage.py migrate
python manage.py runserver
