package com.flodex.attachaki

import android.os.Bundle
import android.widget.ArrayAdapter
import android.widget.Button
import android.widget.EditText
import android.widget.Spinner
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.flodex.attachaki.data.AppDatabase
import com.flodex.attachaki.data.FlodexRepository
import com.flodex.attachaki.voice.VoiceCommandParser
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {
    private lateinit var repository: FlodexRepository
    private val parser = VoiceCommandParser()
    private var selectedCustomerId: Int? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        repository = FlodexRepository(AppDatabase.getInstance(this))

        val nameInput = findViewById<EditText>(R.id.nameInput)
        val phoneInput = findViewById<EditText>(R.id.phoneInput)
        val addressInput = findViewById<EditText>(R.id.addressInput)
        val wheatInput = findViewById<EditText>(R.id.wheatInput)
        val flourInput = findViewById<EditText>(R.id.flourInput)
        val amountInput = findViewById<EditText>(R.id.amountInput)
        val paymentSpinner = findViewById<Spinner>(R.id.paymentSpinner)
        val voiceInput = findViewById<EditText>(R.id.voiceInput)
        val output = findViewById<TextView>(R.id.outputText)

        paymentSpinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, listOf("PAID", "UNPAID"))

        findViewById<Button>(R.id.saveCustomerBtn).setOnClickListener {
            lifecycleScope.launch {
                val name = nameInput.text.toString().trim()
                val phone = phoneInput.text.toString().trim()
                if (name.isBlank() || phone.isBlank()) {
                    output.text = "Name and phone required"
                    return@launch
                }

                val customer = repository.addOrGetCustomer(
                    name = name,
                    phone = phone,
                    address = addressInput.text.toString().trim(),
                )
                selectedCustomerId = customer.id
                output.text = "Customer ready: ${customer.name}"
            }
        }

        findViewById<Button>(R.id.addTransactionBtn).setOnClickListener {
            lifecycleScope.launch {
                val cid = selectedCustomerId
                if (cid == null) {
                    output.text = "Select/save customer first"
                    return@launch
                }

                val wheat = wheatInput.text.toString().toDoubleOrNull()
                val flour = flourInput.text.toString().toDoubleOrNull()
                val amount = amountInput.text.toString().toDoubleOrNull()
                if (wheat == null || flour == null || amount == null) {
                    output.text = "Enter valid wheat/flour/amount"
                    return@launch
                }

                repository.addTransaction(
                    customerId = cid,
                    wheat = wheat,
                    flour = flour,
                    amount = amount,
                    paymentStatus = paymentSpinner.selectedItem.toString(),
                )
                output.text = "Transaction added (${wheat} KG)"
            }
        }

        findViewById<Button>(R.id.runVoiceBtn).setOnClickListener {
            val intent = parser.parse(voiceInput.text.toString())
            lifecycleScope.launch {
                when (intent.action) {
                    "wake_word_required" -> output.text = "Start with wake word: Flodex"

                    "find_customer" -> {
                        val customer = repository.findCustomer(intent.customerQuery.orEmpty())
                        output.text = if (customer != null) {
                            selectedCustomerId = customer.id
                            nameInput.setText(customer.name)
                            phoneInput.setText(customer.phone)
                            addressInput.setText(customer.address)
                            "Found customer: ${customer.name}"
                        } else {
                            "Customer not found"
                        }
                    }

                    "summary" -> {
                        val summary = repository.summary(intent.period ?: "daily")
                        output.text = "${summary.label}: Wheat ${"%.2f".format(summary.wheat)} KG, Flour ${"%.2f".format(summary.flour)} KG, Amount ${"%.2f".format(summary.amount)}, Unpaid ${"%.2f".format(summary.unpaid)}"
                    }

                    "add_transaction" -> {
                        val weight = intent.weight
                        if (weight != null) {
                            wheatInput.setText(weight.toString())
                            flourInput.setText((weight * 0.9).toString())
                            output.text = "Weight captured ${weight} KG, fill amount and save"
                        } else {
                            output.text = "Weight not detected"
                        }
                    }

                    "unpaid_report" -> {
                        val summary = repository.summary("all")
                        output.text = "Current unpaid total: ${"%.2f".format(summary.unpaid)}"
                    }

                    else -> output.text = "Command not understood"
                }
            }
        }

        findViewById<Button>(R.id.dailySummaryBtn).setOnClickListener { showSummary("daily", output) }
        findViewById<Button>(R.id.weeklySummaryBtn).setOnClickListener { showSummary("weekly", output) }
        findViewById<Button>(R.id.monthlySummaryBtn).setOnClickListener { showSummary("monthly", output) }
    }

    private fun showSummary(period: String, output: TextView) {
        lifecycleScope.launch {
            val summary = repository.summary(period)
            output.text = "${summary.label}: Wheat ${"%.2f".format(summary.wheat)} KG, Flour ${"%.2f".format(summary.flour)} KG, Amount ${"%.2f".format(summary.amount)}, Unpaid ${"%.2f".format(summary.unpaid)}"
        }
    }
}
