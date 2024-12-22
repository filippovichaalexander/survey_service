CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,                -- Уникальный идентификатор пользователя
    username VARCHAR(50) NOT NULL UNIQUE, -- Имя пользователя
    password_hash VARCHAR(255) NOT NULL,  -- Хэш пароля для аутентификации
    created_at TIMESTAMP DEFAULT NOW()    -- Дата создания пользователя
);

-- Таблица опросов
CREATE TABLE IF NOT EXISTS surveys (
    id SERIAL PRIMARY KEY,                  -- Уникальный идентификатор опроса
    title VARCHAR(255) NOT NULL,            -- Название опроса
    description TEXT,                       -- Описание опроса
    created_by INT,                         -- ID пользователя, создавшего опрос (NULL для анонимного)
    created_at TIMESTAMP DEFAULT NOW(),     -- Дата создания опроса
    is_active BOOLEAN DEFAULT TRUE,         -- Статус опроса (активен или нет)
    is_single_choice BOOLEAN DEFAULT FALSE, -- Кло-во ответов
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Таблица вариантов ответа
CREATE TABLE IF NOT EXISTS options (
    id SERIAL PRIMARY KEY,                -- Уникальный идентификатор варианта
    survey_id INT NOT NULL,                 -- ID опроса, к которому относится вариант
    option_text VARCHAR(255) NOT NULL,    -- Текст варианта ответа
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE
);

-- Таблица голосов
CREATE TABLE IF NOT EXISTS votes (
    id SERIAL PRIMARY KEY,                -- Уникальный идентификатор голоса
    survey_id INT NOT NULL,                 -- ID опроса, в котором сделан голос
    user_id INT,                          -- ID пользователя (NULL для анонимного голосования)
    voter_ip VARCHAR(45),                  -- IP адрес пользователя (для анонимного голосования)
    created_at TIMESTAMP DEFAULT NOW(),   -- Дата голосования
    FOREIGN KEY (survey_id) REFERENCES surveys(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE (survey_id, user_id),            -- Запрет повторного голосования (для зарегистрированных пользователей)
    UNIQUE (survey_id, voter_ip)           -- Запрет повторного голосования (для зарегистрированных пользователей)
);

CREATE TABLE IF NOT EXISTS vote_options (
    id SERIAL PRIMARY KEY,
    vote_id INT,
    option_id INT,
    FOREIGN KEY (vote_id) REFERENCES votes(id) ON DELETE CASCADE,
    FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE,
    UNIQUE (vote_id, option_id)
);