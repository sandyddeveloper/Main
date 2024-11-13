from werkzeug.security import check_password_hash

# The stored hash from your database for username 'itssandyhere'
stored_hash="scrypt:32768:8:1$HshuFgE0hxew1GzD$4e1f83cdd2507f044536a551b6fb3dd99ea3f7f2b59936087cb4fc935fc0ec4002d4fa78e1a0261a7f67804e1011d634087f05ccfe45c94da0efbc954c2d791e"
password_input = "111"  # The password entered by the user

# Use check_password_hash to validate the password
is_correct_password = check_password_hash(stored_hash, password_input)
print("Password verification result:", is_correct_password)

from werkzeug.security import generate_password_hash

password_input = "111"
new_hash = generate_password_hash(password_input)
print("Generated Hash:", new_hash)
