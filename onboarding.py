
# --- Constants ---
APP_NAME = "TaskFlow AI"
VERSION = "0.1.0"
MAX_TASKS_FREE = 10
MAX_TASKS_PREMIUM = 100
VALID_PLANS = ["free", "premium"]

# --- Header ---
print("=" * 40)
print(f"   Welcome to {APP_NAME} v{VERSION}")
print("=" * 40)
print()

# --- Collect Name ---
raw_name = input("What is your name? ")
name = raw_name.strip().title()      # clean and title-case
first_name = name.split()[0]         # extract first name

if not name:
    name = "Friend"
    first_name = "Friend"

# --- Collect Age ---
raw_age = input("How old are you? ").strip()

if raw_age.isdigit():
    age = int(raw_age)
else:
    print("Invalid age entered — setting to 0.")
    age = 0

# --- Collect Role ---
raw_role = input("Are you a developer? (yes/no): ").strip().lower()

if raw_role in ["yes", "y"]:
    is_developer = True
    role = "Developer"
elif raw_role in ["no", "n"]:
    is_developer = False
    role = "General User"
else:
    is_developer = False
    role = "Unknown"
    print("Unrecognized input — defaulting to General User.")

# --- Collect Plan ---
raw_plan = input("Choose your plan — free or premium: ").strip().lower()

if raw_plan in VALID_PLANS:
    plan = raw_plan
else:
    print("Unrecognized plan — defaulting to free.")
    plan = "free"

# --- Derive Settings from Input ---
if plan == "premium":
    max_tasks = MAX_TASKS_PREMIUM
    plan_label = "Premium (100 tasks max)"
    ai_tip = "Premium users get AI-powered task analysis. We'll build that in Phase 4!"
else:
    max_tasks = MAX_TASKS_FREE
    plan_label = "Free (10 tasks max)"
    ai_tip = "Upgrade to Premium to unlock AI features. Type 'upgrade' anytime."

# --- Age-based message ---
if age < 18:
    age_note = "Young builder — impressive!"
elif age < 30:
    age_note = "Prime building years."
elif age < 50:
    age_note = "Experience + code = power."
else:
    age_note = "Wisdom-driven engineering."

# --- Developer-specific message ---
if is_developer:
    dev_note = "Dev mode: you will see extra technical details throughout."
else:
    dev_note = "No coding experience needed — we start from absolute zero."

# --- Summary Output ---
print()
print("-" * 40)
print(f"Hey {first_name}! Great to have you onboard.")
print(f"You are {age} years old. {age_note}")
print()
print(f"{'Role detected':<16}: {role}")
print(f"{'Plan selected':<16}: {plan_label}")
print(f"{'Max tasks':<16}: {max_tasks}")
print()
print(f"Tip: {ai_tip}")
print()
print(dev_note)
print()
print("Your TaskFlow AI journey starts now.")
print("-" * 40)