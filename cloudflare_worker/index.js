/**
 * ThumbSwap Bot - Cloudflare Workers Serverless Edition 🎬⚡
 * Zero-Download Server-Side Pointer Swap Architecture on Cloudflare Edge.
 */

const UNSUPPORTED_MEDIA_REPLY = `⚠️ Unsupported File Type!
This bot only supports Videos (sent as streaming video).
Documents, audio files, and other formats are not supported.`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Health check endpoint for monitoring
    if (request.method === "GET") {
      return new Response(
        JSON.stringify({
          status: "online",
          bot: "ThumbSwap Bot (Cloudflare Serverless)",
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
      if (!update || !update.message) {
        return new Response("OK", { status: 200 });
      }

      // Process Telegram message event
      await handleMessage(update.message, env);
      return new Response("OK", { status: 200 });
    } catch (err) {
      console.error("Error processing Telegram update:", err);
      return new Response("OK", { status: 200 });
    }
  },
};

/**
 * Handle incoming Telegram messages
 */
async function handleMessage(message, env) {
  const chatId = message.chat.id;
  const user = message.from || {};
  const userId = user.id ? user.id.toString() : null;

  if (!userId) return;

  const text = (message.text || "").trim();

  // 1. /start command
  if (text === "/start" || text.startsWith("/start ")) {
    const userName = user.first_name || "there";
    const welcomeText = `👋 <b>Welcome, ${userName}, to ThumbSwap Bot!</b> 🎬⚡\n\n` +
      `I can instantly replace the cover / thumbnail of any streaming video ` +
      `(up to <b>4GB</b>) in 1–5 seconds using Telegram's server-side pointer swap.\n\n` +
      `<b>📌 How it works:</b>\n` +
      `1️⃣ <b>Send a Photo:</b> The bot will save it in Cloudflare KV as your new cover.\n` +
      `2️⃣ <b>Send a Streaming Video:</b> The bot will instantly return your video with the new cover applied!\n\n` +
      `✨ <b>Features:</b>\n` +
      `• <b>Zero Download & Zero Re-upload:</b> Instant round-trip (1–5 seconds)\n` +
      `• <b>100% Quality Retention:</b> Original bitrate, resolution, audio & streaming flags preserved\n` +
      `• <b>Serverless Cloud:</b> Powered by Cloudflare Edge 24/7 with zero downtime!\n\n` +
      `Send your thumbnail photo to get started! 🖼️`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: welcomeText,
      parse_mode: "HTML",
    });
    return;
  }

  // 2. /help command
  if (text === "/help" || text.startsWith("/help ")) {
    const helpText = `📖 <b>ThumbSwap Bot - User Guide</b>\n\n` +
      `<b>Step 1:</b> Send a photo you want to use as your thumbnail.\n` +
      `<b>Step 2:</b> Send a video as a <i>Streaming Video</i> (not as a document/file).\n` +
      `<b>Step 3:</b> Receive your video back within seconds with the new thumbnail!\n\n` +
      `<b>Available Commands:</b>\n` +
      `/start - Start the bot & show welcome message\n` +
      `/help - Display this guide\n` +
      `/viewthumb - View your currently saved thumbnail\n` +
      `/clear - Delete your saved thumbnail from memory`;

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: helpText,
      parse_mode: "HTML",
    });
    return;
  }

  // 3. /viewthumb command
  if (text === "/viewthumb" || text.startsWith("/viewthumb ")) {
    const savedCover = await env.THUMB_KV.get(userId);
    if (savedCover) {
      await callTelegram(env.BOT_TOKEN, "sendPhoto", {
        chat_id: chatId,
        photo: savedCover,
        caption: "📸 Here is your currently saved thumbnail photo.",
        reply_to_message_id: message.message_id,
      });
    } else {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: "ℹ️ You do not have any saved thumbnail yet.\nSend a photo to save it as your new thumbnail!",
      });
    }
    return;
  }

  // 4. /clear or /delthumb command
  if (text === "/clear" || text === "/delthumb") {
    await env.THUMB_KV.delete(userId);
    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: "🗑️ Saved thumbnail removed from Cloudflare storage. Send a new photo anytime!",
    });
    return;
  }

  // 5. Photo Received -> Save to Cloudflare KV
  if (message.photo && Array.isArray(message.photo) && message.photo.length > 0) {
    const highestRes = message.photo[message.photo.length - 1];
    await env.THUMB_KV.put(userId, highestRes.file_id);

    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: "✅ Thumbnail Saved! Send your streaming video now.",
      reply_to_message_id: message.message_id,
    });
    return;
  }

  // 6. Non-Streaming Media Filtering (Document, Audio, Voice, Sticker, Animation)
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
      reply_to_message_id: message.message_id,
    });
    return;
  }

  // 7. Streaming Video Received -> Zero-Download Pointer Swap
  if (message.video) {
    const savedCover = await env.THUMB_KV.get(userId);
    if (!savedCover) {
      await callTelegram(env.BOT_TOKEN, "sendMessage", {
        chat_id: chatId,
        text: "⚠️ Please send a thumbnail photo first before sending a video!",
        reply_to_message_id: message.message_id,
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
      });
    }
    return;
  }

  // 8. Plain text fallback
  if (text) {
    await callTelegram(env.BOT_TOKEN, "sendMessage", {
      chat_id: chatId,
      text: "ℹ️ Send me a <b>Photo</b> first to save your thumbnail, then send a <b>Streaming Video</b> to instantly apply it!",
      parse_mode: "HTML",
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
