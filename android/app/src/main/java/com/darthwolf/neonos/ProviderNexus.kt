package com.darthwolf.neonos

import android.content.Context
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

object ProviderNexus {
    data class Provider(
        val id: String,
        val label: String,
        val kind: String,
        val endpoint: String,
        val model: String,
        val buildKey: () -> String
    )

    private val http = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(120, TimeUnit.SECONDS)
        .build()

    private val providers = listOf(
        Provider("gemini", "Gemini", "gemini", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent", "gemini-2.5-flash", { BuildConfig.GEMINI_API_KEY }),
        Provider("xkiro", "xKiro", "openai", "https://api.xkiro.com/v1/chat/completions", "auto", { BuildConfig.XKIRO_API_KEY }),
        Provider("anthropic", "Anthropic", "anthropic", "https://api.anthropic.com/v1/messages", "claude-sonnet-5", { BuildConfig.ANTHROPIC_API_KEY }),
        Provider("openai", "OpenAI", "openai", "https://api.openai.com/v1/chat/completions", "gpt-5.6-luna", { BuildConfig.OPENAI_API_KEY }),
        Provider("groq", "Groq", "openai", "https://api.groq.com/openai/v1/chat/completions", "openai/gpt-oss-120b", { BuildConfig.GROQ_API_KEY }),
        Provider("openrouter", "OpenRouter", "openai", "https://openrouter.ai/api/v1/chat/completions", "openrouter/auto", { BuildConfig.OPENROUTER_API_KEY })
    )

    private fun prefs(context: Context) = context.getSharedPreferences("neon_provider_keys", Context.MODE_PRIVATE)

    private fun key(context: Context, provider: Provider): String {
        val stored = prefs(context).getString(provider.id, "").orEmpty()
        return stored.ifBlank { provider.buildKey() }
    }

    fun setKey(context: Context, id: String, value: String): Boolean {
        if (providers.none { it.id == id }) return false
        prefs(context).edit().putString(id, value.trim()).apply()
        return true
    }

    fun status(context: Context): String {
        return providers.joinToString(" • ") {
            it.label + "=" + if (key(context, it).isNotBlank()) "ready" else "missing"
        }
    }

    fun chat(context: Context, prompt: String, route: String = "fast"): String {
        require(prompt.isNotBlank()) { "Prompt is empty" }
        val order = when (route.lowercase()) {
            "coding" -> listOf("xkiro", "anthropic", "openai", "openrouter", "groq", "gemini")
            "reasoning" -> listOf("anthropic", "openai", "gemini", "xkiro", "openrouter", "groq")
            else -> listOf("groq", "gemini", "openrouter", "openai", "xkiro", "anthropic")
        }
        val failures = mutableListOf<String>()
        for (id in order) {
            val provider = providers.first { it.id == id }
            val token = key(context, provider)
            if (token.isBlank()) continue
            try {
                return when (provider.kind) {
                    "gemini" -> gemini(provider, token, prompt)
                    "anthropic" -> anthropic(provider, token, prompt)
                    else -> openAiCompatible(provider, token, prompt)
                }
            } catch (e: Exception) {
                failures += provider.label + ": " + e.message
            }
        }
        error(if (failures.isEmpty()) "No provider keys configured" else failures.takeLast(6).joinToString(" | "))
    }

    private fun openAiCompatible(provider: Provider, token: String, prompt: String): String {
        val messages = JSONArray().put(JSONObject().put("role", "user").put("content", prompt))
        val body = JSONObject()
            .put("model", provider.model)
            .put("messages", messages)
            .put("max_tokens", 1200)
        val request = Request.Builder()
            .url(provider.endpoint)
            .header("Authorization", "Bearer " + token)
            .header("Content-Type", "application/json")
            .header("X-Title", "NEON OS")
            .post(body.toString().toRequestBody("application/json".toMediaType()))
            .build()
        http.newCall(request).execute().use { response ->
            val raw = response.body?.string().orEmpty()
            if (!response.isSuccessful) error("HTTP " + response.code + ": " + raw.take(240))
            return JSONObject(raw)
                .getJSONArray("choices")
                .getJSONObject(0)
                .getJSONObject("message")
                .getString("content")
                .trim()
        }
    }

    private fun anthropic(provider: Provider, token: String, prompt: String): String {
        val body = JSONObject()
            .put("model", provider.model)
            .put("max_tokens", 1200)
            .put("messages", JSONArray().put(JSONObject().put("role", "user").put("content", prompt)))
        val request = Request.Builder()
            .url(provider.endpoint)
            .header("x-api-key", token)
            .header("anthropic-version", "2023-06-01")
            .header("content-type", "application/json")
            .post(body.toString().toRequestBody("application/json".toMediaType()))
            .build()
        http.newCall(request).execute().use { response ->
            val raw = response.body?.string().orEmpty()
            if (!response.isSuccessful) error("HTTP " + response.code + ": " + raw.take(240))
            val parts = JSONObject(raw).optJSONArray("content") ?: JSONArray()
            val out = StringBuilder()
            for (i in 0 until parts.length()) {
                val part = parts.optJSONObject(i)
                if (part?.optString("type") == "text") out.append(part.optString("text"))
            }
            return out.toString().trim()
        }
    }

    private fun gemini(provider: Provider, token: String, prompt: String): String {
        val body = JSONObject().put(
            "contents",
            JSONArray().put(
                JSONObject().put(
                    "parts",
                    JSONArray().put(JSONObject().put("text", prompt))
                )
            )
        )
        val request = Request.Builder()
            .url(provider.endpoint + "?key=" + token)
            .header("Content-Type", "application/json")
            .post(body.toString().toRequestBody("application/json".toMediaType()))
            .build()
        http.newCall(request).execute().use { response ->
            val raw = response.body?.string().orEmpty()
            if (!response.isSuccessful) error("HTTP " + response.code + ": " + raw.take(240))
            return JSONObject(raw)
                .getJSONArray("candidates")
                .getJSONObject(0)
                .getJSONObject("content")
                .getJSONArray("parts")
                .getJSONObject(0)
                .getString("text")
                .trim()
        }
    }
}
