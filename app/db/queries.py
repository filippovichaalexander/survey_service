ALL_SURVEYS = """SELECT * FROM surveys ORDER BY id;"""

CREATE_USER = """
INSERT INTO users (username, password_hash)
VALUES (%s, %s)
RETURNING id, username;
"""

GET_USER_BY_USERNAME_AND_PASSWORD = """
SELECT id, username
FROM users
WHERE username = %s and password_hash = %s;
"""

CREATE_SURVEY = """
INSERT INTO surveys (title, description, created_by, is_single_choice)
VALUES (%s, %s, %s, %s)
RETURNING id, title, description, created_by, is_single_choice;
"""

CREATE_OPTION = """
INSERT INTO options (survey_id, option_text)
VALUES (%s, %s)
RETURNING id, option_text;
"""

GET_OPTIONS_FOR_SURVEY = """
SELECT id, option_text
FROM options
WHERE survey_id = %s;
"""