
CREATE TABLE users (
	id SERIAL NOT NULL, 
	first_name VARCHAR(100) NOT NULL, 
	last_name VARCHAR(100) NOT NULL, 
	position VARCHAR(150) NOT NULL, 
	institution_name VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash TEXT, 
	auth_provider VARCHAR(20) DEFAULT 'email'::character varying, 
	google_id VARCHAR(255), 
	created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
	last_login TIMESTAMP WITH TIME ZONE, 
	CONSTRAINT users_pkey PRIMARY KEY (id), 
	CONSTRAINT users_email_key UNIQUE NULLS DISTINCT (email), 
	CONSTRAINT users_google_id_key UNIQUE NULLS DISTINCT (google_id)
)

