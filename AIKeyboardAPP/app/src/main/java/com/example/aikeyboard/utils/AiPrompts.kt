package com.example.aikeyboard.utils

object AiPrompts {
    const val DIRECT_INSTRUCTION = "Give the ans in single line or multiple if required but make it direct. (RAG not required): "

    const val FORMAL = "Make the following text formal. $DIRECT_INSTRUCTION"
    const val GRAMMAR = "Fix grammar and spelling only for the following text. $DIRECT_INSTRUCTION"
    const val PROFESSIONAL = "Make the following text sound professional. $DIRECT_INSTRUCTION"
    const val REPLY = "Do not use RAG. Write a reply for this message in a polite manner. Do not write extra things, just a direct single line or 2-3 line message reply: "
}
