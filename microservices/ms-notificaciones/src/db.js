const { Pool } = require('pg');

// se crea un poool para ahorra recursos
const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
});

pool.on('error', (err, client) => {
    console.error('Error inesperado en el cliente de la base de datos', err);
    process.exit(-1);
});

module.exports = {
    // Exportamos una función para ejecutar queries 
    query: (text, params) => pool.query(text, params),
};