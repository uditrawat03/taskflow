# profile.py
# TaskFlow AI — Day 02
# User profile module.
# Stores and displays information about the current user.

# --- Constants ---
APP_NAME = "TaskFlow AI"
VERSION = "0.1.0"
FREE_TRIAL_DAYS = 14
MAX_TASKS_FREE = 10
MAX_TASKS_PREMIUM = 100

# --- User Profile ---
# In a real app this data would come from a database or user input.
# For now, we define it directly to practise data types.

name = "Udit Rawat"  # str
age = 28  # int
email = "udit@example.com"  # str
role = "Developer"  # str
is_premium = True  # bool
is_active = True  # bool
task_count = 0  # int
completion_rate = 0.0  # float  (percentage as decimal)
profile_picture = None  # NoneType — not uploaded yet

# --- Derived Values ---
# These are calculated from the base data above.

max_tasks = MAX_TASKS_PREMIUM if is_premium else MAX_TASKS_FREE
tasks_remaining = max_tasks - task_count
trial_status = "Premium" if is_premium else f"Free ({FREE_TRIAL_DAYS} days remaining)"

# --- Clean & Normalize ---
# Always normalize user-supplied text before storing or displaying it.

name_clean = name.strip().title()
email_clean = email.strip().lower()
first_name = name_clean.split()[0]  # "Udit"

# --- Display Profile ---

print("=" * 38)
print(f"  {APP_NAME} — User Profile  ")
print("=" * 38)
print()
print(f"{'Name':<14}: {name_clean}")
print(f"{'Age':<14}: {age}")
print(f"{'Email':<14}: {email_clean}")
print(f"{'Role':<14}: {role}")
print(f"{'Account':<14}: {trial_status}")
print(f"{'Tasks done':<14}: {task_count}")
print(f"{'Tasks left':<14}: {tasks_remaining}")
print(f"{'Profile pic':<14}: {'Uploaded' if profile_picture else 'Not set'}")
print()
print(f"Account active   : {is_active}")
print(f"Completion rate  : {completion_rate:.1%}")
print()
print(f"Welcome, {first_name}! Let's get productive.")
print(f"You are running {APP_NAME} v{VERSION}.")
