package com.example.aikeyboard.utils

import android.content.Context
import com.example.aikeyboard.data.local.EncryptedPrefsManager

object AppConfig {
    const val DEFAULT_BASE_URL = "http://10.0.2.2:8000/"
    const val DEFAULT_TIMEOUT_SECONDS = 300L // 5 minutes
    const val DEFAULT_SCREENSHOT_HEIGHT_DP = 300

    fun getBaseUrl(context: Context): String {
        val prefs = EncryptedPrefsManager(context)
        val customUrl = prefs.getBaseUrl()
        
        return if (!customUrl.isNullOrBlank()) {
            if (customUrl.endsWith("/")) customUrl else "$customUrl/"
        } else {
            DEFAULT_BASE_URL
        } 
    }

    fun getTimeoutSeconds(context: Context): Long {
        val prefs = EncryptedPrefsManager(context)
        return prefs.getTimeout()
    }

    fun getScreenshotHeight(context: Context): Int {
        val prefs = EncryptedPrefsManager(context)
        return prefs.getScreenshotHeight()
    }

    fun saveScreenshotHeight(context: Context, height: Int) {
        val prefs = EncryptedPrefsManager(context)
        prefs.saveScreenshotHeight(height)
    }
}
