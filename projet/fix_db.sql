-- À exécuter dans PostgreSQL si les colonnes / tables n'existent pas encore
-- (pgAdmin ou psql)

ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS nom_complet VARCHAR(150) DEFAULT '';
ALTER TABLE utilisateurs ADD COLUMN IF NOT EXISTS contact VARCHAR(100) DEFAULT '';

CREATE TABLE IF NOT EXISTS etablissement (
    id BIGSERIAL PRIMARY KEY,
    nom VARCHAR(200) NOT NULL DEFAULT 'Lycée',
    adresse VARCHAR(255) DEFAULT '',
    telephone VARCHAR(50) DEFAULT '',
    email VARCHAR(254) DEFAULT '',
    devise VARCHAR(150) DEFAULT ''
);
