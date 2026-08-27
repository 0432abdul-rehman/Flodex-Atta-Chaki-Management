package com.flodex.attachaki.voice

data class VoiceIntent(
    val action: String,
    val customerQuery: String? = null,
    val weight: Double? = null,
    val period: String? = null,
)

class VoiceCommandParser {
    private val wakeWord = "flodex"

    fun parse(text: String): VoiceIntent {
        val lowered = text.lowercase().trim()
        val hasWakeWord = lowered.contains(wakeWord)
        val normalized = lowered.replace(wakeWord, "").trim()

        if (!hasWakeWord && !normalized.contains("data") && !normalized.contains("kg")) {
            return VoiceIntent(action = "wake_word_required")
        }

        return when {
            normalized.contains("aaj ka data") || normalized.contains("today") ->
                VoiceIntent(action = "summary", period = "daily")

            normalized.contains("hafta") || normalized.contains("week") ->
                VoiceIntent(action = "summary", period = "weekly")

            normalized.contains("mahina") || normalized.contains("month") ->
                VoiceIntent(action = "summary", period = "monthly")

            normalized.contains("all data") || normalized.contains("poora data") ->
                VoiceIntent(action = "summary", period = "all")

            normalized.contains("unpaid") || normalized.contains("loan") || normalized.contains("qarz") ->
                VoiceIntent(action = "unpaid_report")

            normalized.contains("data nikalo") -> {
                val name = normalized.substringBefore("ka data nikalo").trim()
                VoiceIntent(action = "find_customer", customerQuery = name)
            }

            normalized.contains("kg") || normalized.contains("add") -> {
                val number = Regex("(\\d+(?:\\.\\d+)?)").find(normalized)?.value?.toDoubleOrNull()
                VoiceIntent(action = "add_transaction", weight = number)
            }

            else -> VoiceIntent(action = "unknown")
        }
    }
}
