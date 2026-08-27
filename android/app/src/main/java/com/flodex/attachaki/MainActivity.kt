package com.flodex.attachaki

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
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
        val voiceInput = findViewById<EditText>(R.id.voiceInput)
        val output = findViewById<TextView>(R.id.outputText)

        findViewById<Button>(R.id.saveCustomerBtn).setOnClickListener {
            lifecycleScope.launch {
                val customer = repository.addOrGetCustomer(
                    name = nameInput.text.toString().trim(),
                    phone = phoneInput.text.toString().trim(),
                    address = addressInput.text.toString().trim(),
                )
                selectedCustomerId = customer.id
                output.text = "Customer ready: ${customer.name}"
            }
        }

        findViewById<Button>(R.id.runVoiceBtn).setOnClickListener {
            val intent = parser.parse(voiceInput.text.toString())
            lifecycleScope.launch {
                when (intent.action) {
                    "find_customer" -> {
                        val customer = repository.findCustomer(intent.customerQuery.orEmpty())
                        output.text = if (customer != null) {
                            selectedCustomerId = customer.id
                            "Found customer: ${customer.name}"
                        } else {
                            "Customer not found"
                        }
                    }

                    "summary" -> {
                        val (wheat, amount) = repository.todaySummary()
                        output.text = "Today: Wheat ${"%.2f".format(wheat)} KG, Amount ${"%.2f".format(amount)}"
                    }

                    "add_transaction" -> {
                        val cid = selectedCustomerId
                        if (cid != null && intent.weight != null) {
                            repository.addTransaction(cid, intent.weight, intent.weight * 0.9, 0.0, "UNPAID")
                            output.text = "Added ${intent.weight} KG transaction"
                        } else {
                            output.text = "Select customer first or provide weight"
                        }
                    }

                    else -> output.text = "Command not understood"
                }
            }
        }
    }
}
