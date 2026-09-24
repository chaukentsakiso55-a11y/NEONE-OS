package com.darthwolf.neonos

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

class NeonBootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            context.getSharedPreferences("neon", Context.MODE_PRIVATE)
                .edit()
                .putLong("last_boot", System.currentTimeMillis())
                .apply()
        }
    }
}
