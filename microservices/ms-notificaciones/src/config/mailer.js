const { BrevoClient } = require('@getbrevo/brevo');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

// En la versión 5.x, se usa BrevoClient
const apiInstance = new BrevoClient({
    apiKey: process.env.BREVO_API_KEY
});

module.exports = apiInstance;
