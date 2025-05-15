
/**
* @file backend.js
*
* @brief This file handles the backend of the weather station
*/
// Using Node.js frameworks
const express = require('express'); // For creating a servers
const axios = require('axios'); // For requests to external APIs
const cors = require('cors');

const app = express();
app.use(cors());

// ThingsBoard credentials
const TB_USERNAME; // insert your ThingsBoard username
const TB_PASSWORD; // insert your ThingsBoard password
const DEVICE_ID = '8b534c60-1667-11f0-8f83-43727cd6bc90';
const TB_BASE_URL = 'https://thingsboard.cloud';

let jwtToken = null;
let tokenExpires = 0;

// Login and get JWT token
/**
* @brief Function to log in to ThingsBoard
*
* @details This function uses TB_USERNAME and TB_PASSWORD to log in to ThingsBoard
*/
async function loginToThingsboard() {
  // response = { data: { token: '...' } , status: 200 , etc. }
  const res = await axios.post(`${TB_BASE_URL}/api/auth/login`, {
    username: TB_USERNAME,
    password: TB_PASSWORD,
  });

  jwtToken = res.data.token;

  // JWT lasts 15 minutes in Community Edition
  tokenExpires = Date.now() + 15 * 60 * 1000;
  console.log("jwtToken:", jwtToken);
  console.log("✅ Logged in to ThingsBoard");
}

// Makes request to ThingsBoard to retrieve brightness
/**
* @brief Function gets brightness value
*
* @details This function checks token then returns brightness value
* @returns String the string representation of brightness levels
*/
async function getBrightness() {
  // Check if token is expired before making request
  if (!jwtToken || Date.now() >= tokenExpires) { 
    await loginToThingsboard(); // Refresh token: login and get token
  }

  const res = await axios.get(
    `${TB_BASE_URL}/api/plugins/telemetry/DEVICE/${DEVICE_ID}/values/timeseries?keys=Brightness`,
    {
      headers: { Authorization: `Bearer ${jwtToken}` },
    }
  );

  // Parse brightness from response data using optional chaining to avoid null errors
  const brightness = parseFloat(res.data.Brightness?.[0]?.value || 0);
  console.log("Brightness:", brightness);
  return brightness;
}

// Endpoint your frontend can call
/**
* @brief Function to allow frontend to print brightness
*
*/
app.get('/brightness', async (req, res) => {
  try {
    const brightness = await getBrightness();
    console.log("📡 Brightness fetched:", brightness);
    res.json({ brightness });
  } catch (err) {
    console.error("Error fetching brightness:", err.message);
    res.status(500).json({ error: 'Failed to fetch brightness' });
  }
});

const PORT = process.env.PORT || 3000;
// Start server using Express.js framework
/**
* @brief Function to start server
*
* @details This function starts the server using Express.js framework
*/
app.listen(PORT, () => {
  console.log(`🚀 Server running at http://localhost:${PORT}`);
});
