import dotenv from "dotenv";
import WebSocket from "ws";
import fetch from "node-fetch";

dotenv.config();
// Load environment variables
const { TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID } = process.env;

// Get command-line arguments
const args = process.argv.slice(2); // Remove the first two default arguments
if (args.length < 2) {
  console.error(
    "Please provide the support_price and resist_price as command-line arguments."
  );
  process.exit(1);
}


const support_price_arg = parseFloat(args[0]);
const resist_price_arg = parseFloat(args[1]);
const symbol_arg = args[2];

if (isNaN(support_price_arg) || isNaN(resist_price_arg)) {
  console.error("Target price must be a valid number.");
  process.exit(1);
}

// Function to send a message to Telegram
const sendTelegramMessage = async (message) => {
  const url = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: TELEGRAM_CHAT_ID,
      text: message,
    }),
  });

  const data = await response.json();
  if (data.ok) {
    console.log("Message sent successfully");
  } else {
    console.error("Error sending message:", data.description);
  }
};

// Symbol and target price
const symbol = symbol_arg ?? "btcusdt";
const resistPrice = resist_price_arg;
const supportPrice = support_price_arg;
console.log({symbol, supportPrice, resistPrice});

// WebSocket URL for Binance
const wsUrl = `wss://stream.binance.com:9443/ws/${symbol}@trade`;

// Connect to Binance WebSocket
const ws = new WebSocket(wsUrl);

ws.on("open", () => {
  console.log("WebSocket connection opened");
});

ws.on("message", (data) => {
  const trade = JSON.parse(data);
  const currentPrice = parseFloat(trade.p);

  console.log(`Current price of ${symbol.toUpperCase()}: ${currentPrice}`);

  if (currentPrice > resistPrice) {
    const message = `Price of ${symbol.toUpperCase()} has crossed up ${resistPrice}. Current price is ${currentPrice}. * LONG NOW * and target may be ${supportPrice}`;
    sendTelegramMessage(message);
  }

  if (currentPrice < supportPrice) {
    const message = `Price of ${symbol.toUpperCase()} has crossed down ${supportPrice}. Current price is ${currentPrice}. * SHORT NOW * and target may be ${resistPrice}`;
    sendTelegramMessage(message);
  }
});

ws.on("close", () => {
  console.log("WebSocket connection closed");
});

ws.on("error", (error) => {
  console.error("WebSocket error:", error);
});
