import datetime

name = "Udit Rawat"
day_number = 1
series_name = "Python & AI Engineering"

# --- Printing ---
# print() is a built-in function that displays output to the terminal.
# We will use it constantly while learning.

print("Hello, " + name + "!")


# --- f-strings ---
# An f-string (formatted string) lets you embed variables directly inside text.
# Prefix the string with f and wrap variable names in curly braces {}.
# f-strings are the standard way to format strings in Python 3.6+.

print(f"Welcome to Day {day_number} of {series_name}.")


# --- Using the datetime module ---
# Python comes with a standard library full of useful tools.
# 'datetime' is a module (a file of reusable code) for working with dates and times.

today = datetime.date.today()
formatted_date = today.strftime("%A, %d %B %Y")

print(f"Today is {formatted_date}.")
print("Let's build something real.")