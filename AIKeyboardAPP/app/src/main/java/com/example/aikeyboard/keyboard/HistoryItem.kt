package com.example.aikeyboard.keyboard

data class HistoryItem(
    val id: Long = System.currentTimeMillis(),
    val originalText: String,
    val aiReply: String? = null,
    val timestamp: Long = System.currentTimeMillis()
)
