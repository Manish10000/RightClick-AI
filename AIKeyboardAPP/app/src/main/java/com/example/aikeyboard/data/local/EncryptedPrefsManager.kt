package com.example.aikeyboard.data.local

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.example.aikeyboard.data.model.ResumeProfile
import com.example.aikeyboard.utils.AppConfig
import com.google.gson.Gson

class EncryptedPrefsManager(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "ai_keyboard_secure_v4",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    private val gson = Gson()

    fun saveResumeProfile(profile: ResumeProfile) {
        val json = gson.toJson(profile)
        sharedPreferences.edit().putString("resume_profile", json).apply()
    }

    fun getResumeProfile(): ResumeProfile? {
        val json = sharedPreferences.getString("resume_profile", null)
        return if (json != null) {
            gson.fromJson(json, ResumeProfile::class.java)
        } else {
            null
        }
    }

    fun saveBaseUrl(url: String?) {
        sharedPreferences.edit().putString("custom_base_url", url).apply()
    }

    fun getBaseUrl(): String? {
        return sharedPreferences.getString("custom_base_url", null)
    }

    fun saveTimeout(timeout: Long) {
        sharedPreferences.edit().putLong("network_timeout", timeout).apply()
    }

    fun getTimeout(): Long {
        return sharedPreferences.getLong("network_timeout", AppConfig.DEFAULT_TIMEOUT_SECONDS)
    }

    fun saveScreenshotHeight(height: Int) {
        sharedPreferences.edit().putInt("screenshot_height", height).apply()
    }

    fun getScreenshotHeight(): Int {
        return sharedPreferences.getInt("screenshot_height", AppConfig.DEFAULT_SCREENSHOT_HEIGHT_DP)
    }

    fun saveAccessToken(token: String?) {
        sharedPreferences.edit().putString("access_token", token).apply()
    }

    fun getAccessToken(): String? {
        return sharedPreferences.getString("access_token", null)
    }

    fun saveRefreshToken(token: String?) {
        sharedPreferences.edit().putString("refresh_token", token).apply()
    }

    fun getRefreshToken(): String? {
        return sharedPreferences.getString("refresh_token", null)
    }

    fun clearAuth() {
        sharedPreferences.edit()
            .remove("access_token")
            .remove("refresh_token")
            .apply()
    }
}
