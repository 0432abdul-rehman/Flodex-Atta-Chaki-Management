package com.flodex.attachaki.voice

data class VoiceIntent(
    val action: String,
    val customerQuery: String? = null,
    val weight: Double? = null,
    val period: String? = null,
)

class VoiceCommandParser {
    fun parse(text: String): VoiceIntent {
        val normalized = text.lowercase().replace("flodex", "").trim()
        return when {
            normalized.contains("aaj ka data") -> VoiceIntent(action = "summary", period = "daily")
            normalized.contains("hafta") -> VoiceIntent(action = "summary", period = "weekly")
            normalized.contains("mahina") -> VoiceIntent(action = "summary", period = "monthly")
            normalized.contains("data nikalo") -> {
                val name = normalized.substringBefore("ka data nikalo").trim()
                VoiceIntent(action = "find_customer", customerQuery = name)
            }
            normalized.contains("kg") -> {
                val number = Regex("(\\d+(?:\\.\\d+)?)").find(normalized)?.value?.toDoubleOrNull()
                VoiceIntent(action = "add_transaction", weight = number)
            }
            else -> VoiceIntent(action = "unknown")
        }
    }
}
