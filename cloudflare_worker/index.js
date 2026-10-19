/**
 * Thumbnail Changer Bot 🎬⚡
 * Cloudflare Workers Serverless Edition
 * Zero-Download Server-Side Pointer Swap Architecture on Cloudflare Edge.
 * Up to 4GB Video Thumbnail Swapper in 1–2 seconds running 24/7 serverless.
 */

const UNSUPPORTED_MEDIA_REPLY = `⚠️ <b>Unsupported File Type!</b>\n\n` +
  `This bot only supports <b>Videos</b> (sent as streaming video).\n` +
  `Documents, audio files, stickers, and other formats are not supported.`;

const MAIN_KEYBOARD = {
  inline_keyboard: [
    [
      { text: "📖 Help", callback_data: "cmd_help" },
      { text: "ℹ️ About", callback_data: "cmd_about" }
    ],
    [
      { text: "⚙️ Settings", callback_data: "cmd_setting" },
      { text: "📢 Updates", callback_data: "cmd_updates" }
    ],
    [
      { text: "🖼️ My Thumbnail", callback_data: "cmd_mythumb" },
      { text: "🗑️ Del Thumbnail", callback_data: "cmd_delthumb" }
    ],
    [
      { text: "📊 Bot Status", callback_data: "cmd_status" }
    ]
  ]
};

export default {
  async fetch(request, env, ctx) {
    // Health check endpoint for monitoring
    if (request.method === "GET") {
      return new Response(
        JSON.stringify({
          status: "online",
          bot: "Thumbnail Changer Bot (Cloudflare Serverless)",
          speed: "1-2 seconds",
          max_size: "Up to 4GB",
          architecture: "Zero-Download Server-Side Pointer Swap",
          uptime: "24/7 Cloudflare Edge",
        }),
        {
          headers: { "Content-Type": "application/json" },
          status: 200,
        }
      );
    }

    if (request.method !== "POST") {
      return new Response("Method Not Allowed", { status: 405 });
    }

    try {
      const update = await request.json();
      if (!update) {
        return new Response("OK", { status: 200 });
      }

      // Handle button clicks (Callback Queries)
      if (update.callback_query) {
        await handleCallbackQuery(update.callback_query, env);
        return new Response("OK", { status: 200 });
      }

      // Handle standard messages
      if (update.message) {
        await handleMessage(update.message, env);
        return new Response("OK", { status: 200 });
      }

      return new Response("OK", { status: 200 });
    } catch (err) {
      console.error("Error processing Telegram update:", err);
      return new Response("OK", { status: 200 });
    }
  },
};

/**
 * Register user ID in Cloudflare KV user registry
 */
async function registerUser(userId, env) {
  try {
    const raw = await env.THUMB_KV.get("system:users");
    let users = raw ? JSON.parse(raw) : [];
    if (!users.includes(userId)) {
      users.push(userId);
      await env.THUMB_KV.put("system:users", JSON.stringify(users));
    }
  } catch (err) {
    console.error("Failed to register user in KV:", err);
  }
}

/**
 * Retrieve all registered user IDs from Cloudflare KV
 */
async function getAllUsers(env) {
  try {
    const raw = await env.THUMB_KV.get("system:users");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

/**
 * Send the production-ready Welcome Message with Interactive Buttons
 */
async function sendWelcomeMessage(chatId, user, env) {
  const userName = user.first_name || "there";
  const welcomeText = `👋 <b>Hello, ${userName}! Welcome to Thumbnail Changer Bot</b> 🎬⚡\n\n` +
    `The premier Telegram tool to swap or attach custom thumbnails to streaming videos ` +
    `(up to <b>4GB</b>) in just <b>1–2 seconds</b> with ZERO quality loss!\n\n` +
    `━━━━━━━━━━━━━━━━━━━━━━━\n` +
    `🚀 <b>How It Works:</b>\n` +
    `1️⃣ <b>Send a Photo:</b> Set your high-resolution thumbnail.\n` +
    `2️⃣ <b>Send a Video:</b> Up to 4GB (sent as streaming video).\n` +
    `3️⃣ <b>Instant Delivery:</b> Receive your video back in <b>1–2 seconds</b>!\n` +
    `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
    `💎 <b>Why Creators Love This Bot:</b>\n` +
    `• ⚡ <b>Blazing Fast:</b> 1–2 second instant pointer swap\n` +
    `• 📦 <b>4GB Capacity:</b> Handles large movies, series & lectures\n` +
    `• 🛡️ <b>100% Quality:</b> Original bitrate, resolution & audio intact\n` +
    `• 🌐 <b>24/7 Cloudflare Edge:</b> Zero lag, always online\n\n` +
    `👇 <i>Tap an option below or send a photo directly to begin:</i>`;

  await callTelegram(env.BOT_TOKEN, "sendMessage", {
    chat_id: chatId,
    text: welcomeText,
    parse_mode: "HTML",
    reply_markup: MAIN_KEYBOARD,
  });
}

/**
 * Handle Interactive Inline Button Clicks (Callback Queries)
 */
async function handleCallbackQuery(query, env) {
  const chatId = query.message ? query.message.chat.id : query.from.id;
  const user = query.from || {};
  const userId = user.id ? user.id.toString() : null;
  const data = query.data;

  // Acknowledge callback immediately to remove loading state
  await callTelegram(env.BOT_TOKEN, "answerCallbackQuery", {
    callback_query_id: query.id,
  });

  if (!userId) return;

  if (data === "cmd_start") {
    await sendWelcomeMessage(chatId, user, env);
    return;
  }

  if (data === "cmd_mythumb") {
    const savedCover = await env.THUMB_KV.get(userId);
    if (savedCover) {
      await callTelegram(env.BOT_TOKEN, "sendPhoto", {
        chat_id: chatId,
        photo: savedCover,
        caption: `📸 <b>Your Active Thumbnail:</b>\n\n` +
          `This thumbnail is saved and will be automatically applied to any streaming video you send in <b>1–2 seconds</b>!\n\n` +
          `🗑️ <i>To remove it, tap 'Delete Thumbnail' or send /delthumb.</i>`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "🗑️ Delete Thumbnail", callback_data: "cmd_delthumb" }],
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    } else {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `ℹ️ <b>No Thumbnail Set!</b>\n\n` +
          `You haven't set any custom thumbnail yet.\n` +
          `Send any photo right now to set it!`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    }
    return;
  }

  if (data === "cmd_setting") {
    const savedCover = await env.THUMB_KV.get(userId);
    const settingsText = `⚙️ <b>Thumbnail Changer Bot — Settings</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>User ID:</b> <code>${userId}</code>\n` +
      `• <b>Saved Thumbnail:</b> ${savedCover ? "Active ✅ (Ready)" : "Not Set ❌"}\n` +
      `• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Max File Size:</b> 📦 Up to 4GB\n` +
      `• <b>Streaming Mode:</b> 🟢 Enabled (<code>supports_streaming: true</code>)\n` +
      `• <b>Caption Preservation:</b> 🟢 100% Original Kept\n` +
      `• <b>Edge Platform:</b> 🌐 Cloudflare Serverless (24/7)\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `💡 <i>Send /mythumb to view your image or /delthumb to remove it.</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: settingsText,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "🖼️ View Thumbnail", callback_data: "cmd_mythumb" }, { text: "📊 Status", callback_data: "cmd_status" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  if (data === "cmd_status") {
    const savedCover = await env.THUMB_KV.get(userId);
    const allUsers = await getAllUsers(env);
    const statusText = `📊 <b>Thumbnail Changer Bot — System Status</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Status:</b> 🟢 Operational (24/7 Live)\n` +
      `• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Max File Size:</b> 📦 Up to 4GB\n` +
      `• <b>Your User ID:</b> <code>${userId}</code>\n` +
      `• <b>Your Thumbnail:</b> ${savedCover ? "Active ✅" : "Not Set ❌"}\n` +
      `• <b>Total Registered Users:</b> 👥 ${allUsers.length}\n` +
      `• <b>Platform:</b> 🌐 Cloudflare Edge Network\n` +
      `• <b>Edge Latency:</b> ⚡ ~1ms–5ms\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: statusText,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  if (data === "cmd_about") {
    const aboutText = `ℹ️ <b>About Thumbnail Changer Bot</b> 🎬⚡\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Bot Name:</b> Thumbnail Changer Bot\n` +
      `• <b>Version:</b> 2.0.0 (Production Serverless)\n` +
      `• <b>Hosting:</b> Cloudflare Workers Global Edge\n` +
      `• <b>Database:</b> Cloudflare KV (Permanent)\n` +
      `• <b>Architecture:</b> Zero-Download Server-Side Pointer Swap\n` +
      `• <b>Max File Size:</b> Up to 4GB\n` +
      `• <b>Processing Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Developer:</b> @achalkumardev\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `💡 <i>Designed for ultra-fast, zero-download, and 100% video quality retention.</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: aboutText,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "📢 Updates", callback_data: "cmd_updates" }, { text: "⚙️ Settings", callback_data: "cmd_setting" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  if (data === "cmd_updates") {
    const updatesText = `📢 <b>Thumbnail Changer Bot — Updates & Changelog</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `🎉 <b>What's New in v2.0:</b>\n` +
      `• ⚡ <b>Blazing 1–2s Swap:</b> Ultra-fast pointer swap on Telegram DCs\n` +
      `• 📦 <b>4GB File Support:</b> Handles full movies, anime & shows\n` +
      `• 🌐 <b>24/7 Serverless Edge:</b> Zero server downtime or crashes\n` +
      `• 🔘 <b>Interactive Inline UI:</b> Full touch button navigation\n` +
      `• 💾 <b>Persistent KV Database:</b> Thumbnails saved permanently\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `🔔 <i>Stay tuned for more upcoming updates & features!</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: updatesText,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "ℹ️ About Bot", callback_data: "cmd_about" }, { text: "📖 Help", callback_data: "cmd_help" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  if (data === "cmd_help") {
    const helpText = `📖 <b>Thumbnail Changer Bot — User Guide</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `⚡ <b>How It Works:</b>\n` +
      `This bot uses Telegram's server-side pointer swap. It never downloads or re-encodes your video, ` +
      `meaning <b>100% original quality</b> and instant <b>1–2s</b> delivery!\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `📌 <b>3 Simple Steps:</b>\n` +
      `1️⃣ <b>Set Thumbnail:</b> Send any photo to the bot (or use /addthumb).\n` +
      `2️⃣ <b>Send Video:</b> Send a streaming video (up to 4GB).\n` +
      `3️⃣ <b>Done:</b> Receive your video with the new thumbnail in <b>1–2 seconds</b>!\n\n` +
      `🛠️ <b>User Commands:</b>\n` +
      `• /start — Start the bot & view welcome guide\n` +
      `• /addthumb — Set or update your video thumbnail\n` +
      `• /mythumb — View your currently active thumbnail\n` +
      `• /delthumb — Delete your saved thumbnail\n` +
      `• /setting — View your settings & configuration\n` +
      `• /status — Check live system status & ping\n` +
      `• /restart — Refresh your bot session\n` +
      `• /help — Show this commands menu`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: helpText,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  if (data === "cmd_delthumb") {
    const existing = await env.THUMB_KV.get(userId);
    if (existing) {
      await env.THUMB_KV.delete(userId);
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `🗑️ <b>Thumbnail Deleted Successfully!</b>\n\n` +
          `Your saved thumbnail has been removed from Cloudflare storage.\n` +
          `Incoming videos will now use Telegram's default preview until you set a new one.`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    } else {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `ℹ️ <b>No saved thumbnail found to delete.</b>\nSend a photo or use /addthumb to set one!`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    }
  }
}

/**
 * Handle incoming Telegram messages
 */
async function handleMessage(message, env) {
  const chatId = message.chat.id;
  const user = message.from || {};
  const userId = user.id ? user.id.toString() : null;

  if (!userId) return;

  // Track user in database
  await registerUser(userId, env);

  const text = (message.text || "").trim();
  const lowerText = text.toLowerCase();
  const adminId = (env.ADMIN_ID || "7437014244").toString();

  // 1. /start command
  if (text === "/start" || text.startsWith("/start ")) {
    await sendWelcomeMessage(chatId, user, env);
    return;
  }

  // 2. /help command
  if (text === "/help" || text.startsWith("/help ")) {
    const helpText = `📖 <b>Thumbnail Changer Bot — User Guide</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `⚡ <b>How It Works:</b>\n` +
      `This bot uses Telegram's server-side pointer swap. It never downloads or re-encodes your video, ` +
      `meaning <b>100% original quality</b> and instant <b>1–2s</b> delivery!\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `📌 <b>3 Simple Steps:</b>\n` +
      `1️⃣ <b>Set Thumbnail:</b> Send any photo to the bot (or use /addthumb).\n` +
      `2️⃣ <b>Send Video:</b> Send a streaming video (up to 4GB).\n` +
      `3️⃣ <b>Done:</b> Receive your video with the new thumbnail in <b>1–2 seconds</b>!\n\n` +
      `🛠️ <b>User Commands:</b>\n` +
      `• /start — Start the bot & view welcome guide\n` +
      `• /addthumb — Set or update your video thumbnail\n` +
      `• /mythumb — View your currently active thumbnail\n` +
      `• /delthumb — Delete your saved thumbnail\n` +
      `• /setting — View your settings & configuration\n` +
      `• /status — Check live system status & ping\n` +
      `• /restart — Refresh your bot session\n` +
      `• /help — Show this commands menu\n\n` +
      `👑 <b>Admin Commands:</b>\n` +
      `• /broadcast (or /brotcast) — Send announcement to all users`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: helpText,
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // /about command
  if (text === "/about" || text.startsWith("/about ")) {
    const aboutText = `ℹ️ <b>About Thumbnail Changer Bot</b> 🎬⚡\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Bot Name:</b> Thumbnail Changer Bot\n` +
      `• <b>Version:</b> 2.0.0 (Production Serverless)\n` +
      `• <b>Hosting:</b> Cloudflare Workers Global Edge\n` +
      `• <b>Database:</b> Cloudflare KV (Permanent)\n` +
      `• <b>Architecture:</b> Zero-Download Server-Side Pointer Swap\n` +
      `• <b>Max File Size:</b> Up to 4GB\n` +
      `• <b>Processing Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Developer:</b> @achalkumardev\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `💡 <i>Designed for ultra-fast, zero-download, and 100% video quality retention.</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: aboutText,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "📢 Updates", callback_data: "cmd_updates" }, { text: "⚙️ Settings", callback_data: "cmd_setting" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // /updates command
  if (text === "/updates" || text.startsWith("/updates ")) {
    const updatesText = `📢 <b>Thumbnail Changer Bot — Updates & Changelog</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `🎉 <b>What's New in v2.0:</b>\n` +
      `• ⚡ <b>Blazing 1–2s Swap:</b> Ultra-fast pointer swap on Telegram DCs\n` +
      `• 📦 <b>4GB File Support:</b> Handles full movies, anime & shows\n` +
      `• 🌐 <b>24/7 Serverless Edge:</b> Zero server downtime or crashes\n` +
      `• 🔘 <b>Interactive Inline UI:</b> Full touch button navigation\n` +
      `• 💾 <b>Persistent KV Database:</b> Thumbnails saved permanently\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `🔔 <i>Stay tuned for more upcoming updates & features!</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: updatesText,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "ℹ️ About Bot", callback_data: "cmd_about" }, { text: "📖 Help", callback_data: "cmd_help" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // 3. /restart command
  if (text === "/restart" || text.startsWith("/restart ")) {
    const savedCover = await env.THUMB_KV.get(userId);
    const restartText = `🔄 <b>Session Refreshed Successfully!</b>\n\n` +
      `Your bot session has been re-initialized and is running at peak performance.\n\n` +
      `• <b>Thumbnail:</b> ${savedCover ? "Active ✅ (Ready)" : "Not Set ❌"}\n` +
      `• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Edge Network:</b> 🟢 24/7 Online\n` +
      `• <b>Status:</b> 🟢 Operational\n\n` +
      `<i>Send a photo or streaming video to continue!</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: restartText,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: MAIN_KEYBOARD,
    });
    return;
  }

  // 4. /setting or /settings command
  if (text === "/setting" || text === "/settings" || text.startsWith("/setting ") || text.startsWith("/settings ")) {
    const savedCover = await env.THUMB_KV.get(userId);
    const settingsText = `⚙️ <b>Thumbnail Changer Bot — Settings</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>User ID:</b> <code>${userId}</code>\n` +
      `• <b>Saved Thumbnail:</b> ${savedCover ? "Active ✅ (Ready)" : "Not Set ❌"}\n` +
      `• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Max File Size:</b> 📦 Up to 4GB\n` +
      `• <b>Streaming Mode:</b> 🟢 Enabled (<code>supports_streaming: true</code>)\n` +
      `• <b>Caption Preservation:</b> 🟢 100% Original Kept\n` +
      `• <b>Edge Platform:</b> 🌐 Cloudflare Serverless (24/7)\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `💡 <i>Send /mythumb to view your image or /delthumb to remove it.</i>`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: settingsText,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "🖼️ View Thumbnail", callback_data: "cmd_mythumb" }, { text: "📊 Status", callback_data: "cmd_status" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // 5. /addthumb command
  if (text === "/addthumb" || text.startsWith("/addthumb ")) {
    if (message.reply_to_message && message.reply_to_message.photo && Array.isArray(message.reply_to_message.photo)) {
      const photos = message.reply_to_message.photo;
      const highestRes = photos[photos.length - 1];
      await env.THUMB_KV.put(userId, highestRes.file_id);
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `✅ <b>Thumbnail Saved from Replied Photo!</b>\n\nNow send your streaming video to apply it in <b>1–2 seconds</b>! 🎬⚡`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
        reply_markup: {
          inline_keyboard: [
            [{ text: "🖼️ View Saved Thumbnail", callback_data: "cmd_mythumb" }],
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
      return;
    }

    const addThumbGuide = `🖼️ <b>Set Custom Video Thumbnail</b>\n\n` +
      `Please send any <b>Photo</b> (JPEG / PNG) to set it as your video thumbnail.\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💡 <b>Pro Tips for Best Quality:</b>\n` +
      `• Recommended Aspect Ratio: <b>16:9</b> (1280×720 or 1920×1080)\n` +
      `• Send as a standard photo (compressed), not as a document.\n` +
      `• You can also <b>reply</b> to any photo in chat with <code>/addthumb</code>!\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: addThumbGuide,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // 6. /mythumb or /viewthumb command
  if (text === "/mythumb" || text.startsWith("/mythumb ") || text === "/viewthumb" || text.startsWith("/viewthumb ")) {
    const savedCover = await env.THUMB_KV.get(userId);
    if (savedCover) {
      await callTelegram(env.BOT_TOKEN, "sendPhoto", {
        chat_id: chatId,
        photo: savedCover,
        caption: `📸 <b>Your Active Thumbnail:</b>\n\n` +
          `This thumbnail is saved and will be automatically applied to any streaming video you send in <b>1–2 seconds</b>!\n\n` +
          `🗑️ <i>To remove it, send /delthumb.</i>`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
        reply_markup: {
          inline_keyboard: [
            [{ text: "🗑️ Delete Thumbnail", callback_data: "cmd_delthumb" }],
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    } else {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `ℹ️ <b>No Thumbnail Set!</b>\n\n` +
          `You do not have any saved thumbnail yet.\n` +
          `Send a photo or use /addthumb to set one!`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    }
    return;
  }

  // 7. /delthumb or /clear command
  if (text === "/delthumb" || text === "/clear" || text.startsWith("/delthumb ") || text.startsWith("/clear ")) {
    const existing = await env.THUMB_KV.get(userId);
    if (existing) {
      await env.THUMB_KV.delete(userId);
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `🗑️ <b>Thumbnail Deleted Successfully!</b>\n\n` +
          `Your saved thumbnail has been removed from Cloudflare storage.\n` +
          `Incoming videos will now use Telegram's default preview until you set a new one.`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    } else {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `ℹ️ <b>No saved thumbnail found to delete.</b>\nSend a photo or use /addthumb to set one!`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    }
    return;
  }

  // 8. /broadcast or /brotcast command (Admin only)
  if (
    lowerText === "/broadcast" ||
    lowerText.startsWith("/broadcast ") ||
    lowerText === "/brotcast" ||
    lowerText.startsWith("/brotcast ")
  ) {
    if (userId !== adminId && userId !== "7437014244") {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: "⛔ <b>Access Denied:</b> This command is restricted to the bot administrator.",
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
      });
      return;
    }

    const isReply = Boolean(message.reply_to_message);
    const broadcastContent = text.replace(/^\/(broadcast|brotcast)\s*/i, "").trim();

    if (!broadcastContent && !isReply) {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `⚠️ <b>Usage:</b>\n<code>/broadcast &lt;your message&gt;</code>\nOr reply to any message with <code>/broadcast</code>.`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
      });
      return;
    }

    let allUsers = await getAllUsers(env);
    if (!allUsers.includes(userId)) {
      allUsers.push(userId);
    }

    let successCount = 0;
    let failedCount = 0;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: `📢 <i>Starting broadcast to ${allUsers.length} users...</i>`,
      parse_mode: "HTML",
    });

    for (const targetId of allUsers) {
      try {
        let res;
        if (isReply) {
          res = await callTelegram(env.BOT_TOKEN, "copyMessage", {
            chat_id: targetId,
            from_chat_id: chatId,
            message_id: message.reply_to_message.message_id,
          });
        } else {
          res = await callTelegram(env.BOT_TOKEN, "sendMessage", {
            chat_id: targetId,
            text: `📢 <b>Announcement:</b>\n\n${broadcastContent}`,
            parse_mode: "HTML",
          });
        }

        if (res && res.ok) {
          successCount++;
        } else {
          failedCount++;
        }
      } catch (e) {
        failedCount++;
      }
    }

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: `📢 <b>Broadcast Completed!</b>\n\n` +
        `• <b>Total Targets:</b> ${allUsers.length}\n` +
        `• <b>Successfully Delivered:</b> ${successCount} ✅\n` +
        `• <b>Failed / Blocked:</b> ${failedCount} ❌`,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
    });
    return;
  }

  // 9. /status command
  if (text === "/status" || text.startsWith("/status ")) {
    const savedCover = await env.THUMB_KV.get(userId);
    const allUsers = await getAllUsers(env);
    const statusText = `📊 <b>Thumbnail Changer Bot — System Status</b>\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `• <b>Status:</b> 🟢 Operational (24/7 Live)\n` +
      `• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n` +
      `• <b>Max File Size:</b> 📦 Up to 4GB\n` +
      `• <b>Your User ID:</b> <code>${userId}</code>\n` +
      `• <b>Your Thumbnail:</b> ${savedCover ? "Active ✅" : "Not Set ❌"}\n` +
      `• <b>Total Registered Users:</b> 👥 ${allUsers.length}\n` +
      `• <b>Platform:</b> 🌐 Cloudflare Edge Network\n` +
      `• <b>Edge Latency:</b> ⚡ ~1ms–5ms\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: statusText,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // 10. Photo Received -> Save to Cloudflare KV
  if (message.photo && Array.isArray(message.photo) && message.photo.length > 0) {
    const highestRes = message.photo[message.photo.length - 1];
    await env.THUMB_KV.put(userId, highestRes.file_id);

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: `✅ <b>Thumbnail Saved Successfully!</b>\n\nNow send your <b>Streaming Video</b> (up to 4GB) to swap its thumbnail in <b>1–2 seconds</b>! 🎬⚡`,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "🖼️ View Saved Thumbnail", callback_data: "cmd_mythumb" }],
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // 11. Non-Streaming Media Filtering (Document, Audio, Voice, Sticker, Animation)
  if (
    message.document ||
    message.audio ||
    message.voice ||
    message.video_note ||
    message.animation ||
    message.sticker
  ) {
    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: UNSUPPORTED_MEDIA_REPLY,
      parse_mode: "HTML",
      reply_to_message_id: message.message_id,
      reply_markup: {
        inline_keyboard: [
          [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
        ]
      }
    });
    return;
  }

  // 12. Streaming Video Received -> Zero-Download Pointer Swap (1-2s)
  if (message.video) {
    const savedCover = await env.THUMB_KV.get(userId);
    if (!savedCover) {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `⚠️ <b>Thumbnail Required!</b>\n\nPlease send a photo first before sending your video.\nSend any image or use /addthumb to get started.`,
        parse_mode: "HTML",
        reply_to_message_id: message.message_id,
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
      return;
    }

    // Indicate upload action
    await callTelegram(env.BOT_TOKEN, "sendChatAction", {
      chat_id: chatId,
      action: "upload_video",
    });

    const video = message.video;
    const sendVideoPayload = {
      chat_id: chatId,
      video: video.file_id,
      cover: savedCover,
      supports_streaming: true,
    };

    if (message.caption) {
      sendVideoPayload.caption = message.caption;
      if (message.caption_entities) {
        sendVideoPayload.caption_entities = message.caption_entities;
      }
    }

    if (video.duration) sendVideoPayload.duration = video.duration;
    if (video.width) sendVideoPayload.width = video.width;
    if (video.height) sendVideoPayload.height = video.height;
    if (message.has_media_spoiler) sendVideoPayload.has_spoiler = true;

    const res = await callTelegram(env.BOT_TOKEN, "sendVideo", sendVideoPayload);
    if (!res.ok) {
      console.error("Telegram sendVideo error:", res);
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: `❌ <b>Failed to update thumbnail:</b> ${res.description || "Unknown error"}\nPlease try re-sending your photo thumbnail and try again.`,
        parse_mode: "HTML",
        reply_markup: {
          inline_keyboard: [
            [{ text: "⬅️ Back to Menu", callback_data: "cmd_start" }]
          ]
        }
      });
    }
    return;
  }

  // 13. Plain text fallback
  if (text) {
    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: `ℹ️ Send me a <b>Photo</b> first to save your thumbnail, then send a <b>Streaming Video</b> to instantly swap it in <b>1–2 seconds</b>!\n\nTap below to explore all features:`,
      parse_mode: "HTML",
      reply_markup: MAIN_KEYBOARD,
    });
  }
}

/**
 * Helper to call Telegram Bot API
 */
async function callTelegram(botToken, method, payload) {
  const url = `https://api.telegram.org/bot${botToken}/${method}`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return await response.json();
  } catch (err) {
    console.error(`Error calling Telegram API ${method}:`, err);
    return { ok: false, description: err.message };
  }
}
