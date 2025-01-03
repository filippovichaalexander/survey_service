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

CHECK_USER_VOTED = """
SELECT 1
FROM votes
WHERE survey_id = %s AND user_id = %s;
"""

CHECK_ANONYMOUS_USER_VOTED = """
SELECT 1
FROM votes
WHERE survey_id = %s AND voter_ip = %s;
"""

GET_SURVEY = """
SELECT s.id, s.title, s.description, s.created_by, s.created_at, s.is_active, s.is_single_choice, u.id, u.username
FROM surveys as s
JOIN users as u on u.id = s.created_by
WHERE s.id = %s;
"""

GET_VOTES_FOR_SURVEY = """
SELECT o.option_text, count(v_o.id) as vote_count
FROM votes as v
JOIN vote_options as v_o on v.id = v_o.vote_id
JOIN options as o on o.id = v_o.option_id
WHERE v.survey_id = %s
GROUP BY o.option_text;
"""

CREATE_VOTE = """
INSERT INTO votes (survey_id, user_id, voter_ip)
VALUES (%s, %s, %s)
RETURNING id, survey_id, user_id;
"""

CREATE_VOTE_OPTIONS = """
INSERT INTO vote_options (vote_id, option_id)
VALUES (%s, %s)
RETURNING id, vote_id, option_id;
"""

DELETE_SURVEY = """
DELETE FROM surveys
WHERE id = %s
RETURNING id;
"""