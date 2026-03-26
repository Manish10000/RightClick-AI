package com.example.aikeyboard.data.model

data class ResumeProfile(
    val name: String = "",
    val email: String = "",
    val phone: String = "",
    val systemInstruction: String = "",
    val skills: List<String> = emptyList(),
    val rawText: String = ""
)
