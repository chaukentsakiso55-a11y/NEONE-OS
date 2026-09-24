package com.darthwolf.neonos

import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.WebView
import org.json.JSONArray
import org.json.JSONObject

class NeonBridge(
    private val activity: MainActivity,
    private val webView: WebView
) {
    private val context: Context get() = activity

    @JavascriptInterface
    fun listApps(): String {
        val intent = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val flags = if (android.os.Build.VERSION.SDK_INT >= 33) {
            PackageManager.ResolveInfoFlags.of(0)
        } else null
        val items = if (flags != null) {
            context.packageManager.queryIntentActivities(intent, flags)
        } else {
            @Suppress("DEPRECATION")
            context.packageManager.queryIntentActivities(intent, 0)
        }
        val out = JSONArray()
        items.sortedBy { it.loadLabel(context.packageManager).toString().lowercase() }.forEach { info ->
            out.put(
                JSONObject()
                    .put("label", info.loadLabel(context.packageManager).toString())
                    .put("package", info.activityInfo.packageName)
                    .put("activity", info.activityInfo.name)
            )
        }
        return out.toString()
    }

    @JavascriptInterface
    fun launchApp(packageName: String): Boolean {
        val intent = context.packageManager.getLaunchIntentForPackage(packageName) ?: return false
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(intent)
        return true
    }

    @JavascriptInterface
    fun requestDefaultHome() {
        activity.runOnUiThread { activity.requestHomeRole() }
    }

    @JavascriptInterface
    fun requestOverlay() {
        activity.runOnUiThread { activity.requestOverlayPermission() }
    }

    @JavascriptInterface
    fun openAccessibility() {
        activity.runOnUiThread { activity.openAccessibilitySettings() }
    }

    @JavascriptInterface
    fun openSystemSettings() {
        activity.runOnUiThread { context.startActivity(Intent(Settings.ACTION_SETTINGS)) }
    }

    @JavascriptInterface
    fun startOrb() {
        activity.runOnUiThread {
            if (android.os.Build.VERSION.SDK_INT < 23 || Settings.canDrawOverlays(context)) {
                context.startService(Intent(context, NeonOverlayService::class.java))
            } else {
                activity.requestOverlayPermission()
            }
        }
    }

    @JavascriptInterface
    fun stopOrb() {
        activity.runOnUiThread { context.stopService(Intent(context, NeonOverlayService::class.java)) }
    }

    @JavascriptInterface
    fun providerStatus(): String = ProviderNexus.status(context)

    @JavascriptInterface
    fun setProviderKey(provider: String, key: String): Boolean = ProviderNexus.setKey(context, provider, key)

    @JavascriptInterface
    fun ask(prompt: String, route: String): String {
        return runCatching { ProviderNexus.chat(context, prompt, route) }
            .getOrElse { "NEON AI error: " + (it.message ?: "provider failed") }
    }

    @JavascriptInterface
    fun goHome() {
        activity.runOnUiThread {
            webView.evaluateJavascript("window.neonHome && window.neonHome()", null)
        }
    }
}
